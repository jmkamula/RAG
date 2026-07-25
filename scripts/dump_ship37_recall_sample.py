#!/usr/bin/env python3
"""
Ship 37'.b — dump no-excerpt above-floor candidates for HITL recall
review.

Runs consensus on each of the 5 Ship-10-baseline docs with the
no-excerpt-auto-drop invariant DISABLED. Identifies candidates that:
  - have no fingerprint_excerpt (would be dropped by the invariant)
  - scored ≥ arbiter_floor (would have been accepted or arbiter
    without the invariant)

Samples 4-5 per doc (stratified, seed=42), loads MUST canonical text +
signals fired + first-2K-char doc snippet + topic tokens, dumps to
JSON for HITL classification.

Doesn't invoke the LLM arbiter (arbiter_enabled=False) — capture is
about aggregator-level decisions, not LLM verdicts.
"""
from __future__ import annotations

import json
import logging
import os
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.WARNING)
logging.getLogger("neo4j").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

sys.path.insert(0, "/data/arioncomply")
from dotenv import load_dotenv
load_dotenv("/data/arioncomply/.env")

TENANT = "00000000-0000-0000-0000-000000000001"
SHIP10_BASELINE = [
    "Data Quality Accuracy Procedure.docx",
    "Data Protection Impact Assessment (DPIA) Procedure.docx",
    "Records of Processing Activities.docx",
    "Consent Management Procedure.docx",
    "Processor Operations Procedures.docx",
]

# 4-5 per doc, target 20-25 total. seed=42 matches Ship 34'.c
STRATIFIED_PER_DOC = 5
SEED = 42


def _load_upload_paths():
    import psycopg2
    conn = psycopg2.connect(host="127.0.0.1", dbname="arioncomply_compliance",
                            user="arioncomply", password="")
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT filename, storage_path, id::text "
                "FROM document_uploads "
                "WHERE tenant_id=%s::uuid AND filename = ANY(%s)",
                (TENANT, SHIP10_BASELINE),
            )
            return {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    finally:
        conn.close()


def _process_one(filename, storage_path, upload_id):
    """Run consensus with invariant OFF; return list of no-excerpt
    above-floor candidates + doc snippet + topic tokens."""
    from rag.intake.readers import read_document
    from rag.intake.enricher import enrich
    from rag.intake.doc_pipeline import DocumentPipeline
    from rag.intake.extractor import (
        _scope_controls_via_doc_mappings,
        _scope_controls_via_retrieval,
        _fetch_leaves_for_controls,
    )
    from rag.intake.consensus_extraction import default_config
    from rag.intake.consensus_extraction.orchestrator import run_extraction_consensus
    from rag.intake.consensus_extraction.signals.semantic_fit_gate import _fetch_must_texts

    doc = read_document(storage_path, upload_id=upload_id,
                        original_filename=filename)
    api_key = os.getenv("OPENAI_API_KEY", "")
    try: enrich(doc, api_key)
    except Exception: pass

    pipe = DocumentPipeline(
        db_url="host=127.0.0.1 dbname=arioncomply_compliance user=arioncomply",
        api_key=api_key,
    )
    controls, seen = [], set()
    for std in (doc.standard_ids or ["ISO27001:2022"]):
        for c in pipe._load_controls_from_neo4j(std):
            k = (c["ref"], c["standard_id"])
            if k not in seen:
                seen.add(k)
                controls.append(c)

    # Build scoped_leaf_ids the same way extract() does
    scoped = (_scope_controls_via_doc_mappings(controls, doc)
              or _scope_controls_via_retrieval(controls, doc)
              or controls)
    scoped_leaf_ids = _fetch_leaves_for_controls(scoped[:40])

    # Run consensus with invariant OFF + LLM arbiter OFF
    cfg = default_config().with_overrides(
        no_excerpt_auto_drop=False,
        llm_arbiter_enabled=False,
    )
    result = run_extraction_consensus(doc, scoped_leaf_ids, cfg)

    # Identify no-excerpt candidates that would have been accepted or
    # arbiter (score ≥ arbiter_floor) — those the invariant now drops
    victims = []
    for v in result.verdicts:
        if not v.fingerprint_excerpt and v.score >= cfg.arbiter_floor:
            victims.append(v)

    return doc, victims


def _display_candidate(v, must_texts, doc_snippet, topic_tokens):
    """Serialize one candidate for HITL review."""
    leaf_id, must_id = v.candidate
    return {
        "leaf_id":     leaf_id,
        "must_id":     must_id,
        "must_text":   (must_texts.get(must_id, "") or "")[:400],
        "score":       v.score,
        "corroborators": v.corroborators,
        "signals":     v.signals,
        "verdict_pre_invariant": v.verdict,
        # No excerpt — that's the whole point
        "doc_snippet_first_2k": doc_snippet,
        "doc_topic_tokens":     topic_tokens,
    }


def main():
    print("=" * 72)
    print(" Ship 37'.b — recall HITL sample dump (invariant drops)")
    print("=" * 72)

    paths = _load_upload_paths()
    random.seed(SEED)

    all_samples = []
    for filename in SHIP10_BASELINE:
        entry = paths.get(filename)
        if not entry:
            print(f"\n  ⚠ {filename}: no upload"); continue
        storage_path, upload_id = entry
        if not Path(storage_path).exists():
            print(f"\n  ⚠ {filename}: file missing"); continue

        print(f"\n→ {filename}")
        try:
            doc, victims = _process_one(filename, storage_path, upload_id)
        except Exception as e:
            import traceback
            print(f"    ✗ {type(e).__name__}: {e}")
            traceback.print_exc()
            continue

        print(f"    total no-excerpt above-floor: {len(victims)}")

        # Stratified sample
        k = min(STRATIFIED_PER_DOC, len(victims))
        sample = random.sample(victims, k) if k else []
        print(f"    sampling {k}")

        # Preload MUST texts
        must_ids = [v.candidate[1] for v in sample if v.candidate[1]]
        from rag.intake.consensus_extraction.signals.semantic_fit_gate import _fetch_must_texts
        must_texts = _fetch_must_texts(must_ids) if must_ids else {}

        doc_body = (doc.markdown or doc.full_text or "")[:2000]
        topic_tokens = (doc.topic_tokens or [])[:10]

        for v in sample:
            rec = _display_candidate(v, must_texts, doc_body, topic_tokens)
            rec["filename"] = filename
            rec["control_ref"] = v.control_ref
            rec["standard_id"] = v.standard_id
            all_samples.append(rec)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    out = Path("/data/arioncomply/results") / f"ship37b_recall_sample_{ts}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(all_samples, indent=2, default=str))
    print(f"\nSample: {len(all_samples)} candidates → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
