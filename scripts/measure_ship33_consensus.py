#!/usr/bin/env python3
"""
Ship 33'.b — shadow-mode consensus extraction measurement on the
5 Ship-10-baseline docs.

Runs BOTH pipelines side-by-side:
  - Existing path: `extract(doc, controls, api_key)` from
    rag.intake.extractor (fingerprint + critic-verifier + concat)
  - New path: `run_extraction_consensus(doc, scoped_leaf_ids, cfg)`
    from rag.intake.consensus_extraction

Reports per-doc counts + total for direct comparison against Ship 32
baseline (265 findings, 100% deterministic, Processor Ops 143 with
9% evidence_text uniqueness).

Does NOT write findings to the DB. Ship 30 hygiene sweep runs at
exit as belt-and-suspenders (should be a no-op since we don't write).
"""
from __future__ import annotations

import json
import logging
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Suppress Neo4j notification chatter
logging.basicConfig(level=logging.WARNING)
logging.getLogger("neo4j").setLevel(logging.ERROR)
logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

TENANT   = "00000000-0000-0000-0000-000000000001"
DOC_DIR  = Path("/data/uploads") / TENANT

# Same 5 docs as measure_ship11_reextraction — the reference corpus
SHIP10_BASELINE = {
    "Data Quality Accuracy Procedure.docx":                    9,
    "Data Protection Impact Assessment (DPIA) Procedure.docx": 13,
    "Records of Processing Activities.docx":                   17,
    "Consent Management Procedure.docx":                       28,
    "Processor Operations Procedures.docx":                    30,
}


def _load_upload_paths():
    import psycopg2
    conn = psycopg2.connect(
        host="127.0.0.1", dbname="arioncomply_compliance",
        user="arioncomply", password="",
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT filename, storage_path, id::text
                FROM document_uploads
                WHERE tenant_id = %s::uuid AND filename = ANY(%s)
                """,
                (TENANT, list(SHIP10_BASELINE.keys())),
            )
            return {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    finally:
        conn.close()


def _run_one_doc(filename, storage_path, upload_id):
    """Read + enrich + run BOTH pipelines. Returns dict of per-path metrics."""
    from rag.intake.readers  import read_document
    from rag.intake.enricher import enrich
    from rag.intake.extractor import extract
    from rag.intake.doc_pipeline import DocumentPipeline
    from rag.intake.consensus_extraction import default_config
    from rag.intake.consensus_extraction.orchestrator import run_extraction_consensus

    doc = read_document(storage_path, upload_id=upload_id,
                        original_filename=filename)
    api_key = os.getenv("OPENAI_API_KEY", "")
    try:
        enrich(doc, api_key)
    except Exception as e:
        print(f"    enrich warn: {e}")

    pipeline = DocumentPipeline(
        db_url=f"host=127.0.0.1 dbname=arioncomply_compliance user=arioncomply",
        api_key=api_key,
    )
    controls = []
    seen = set()
    for std in (doc.standard_ids or ["ISO27001:2022"]):
        for c in pipeline._load_controls_from_neo4j(std):
            key = (c["ref"], c["standard_id"])
            if key not in seen:
                seen.add(key)
                controls.append(c)

    # Build scoped_leaf_ids the same way extract() does — via
    # doc_mappings + fallback retrieval. Then feed to BOTH paths.
    # We can extract this from doc.extraction_metrics after
    # calling extract() (which populates target_leaves).

    # --- Path A: existing extract() ---
    findings_A = extract(doc, controls, api_key)

    # --- Path B: consensus (using doc.extraction_metrics populated by A) ---
    # Get the same scoped_leaf_ids the existing path used
    target_leaves = doc.extraction_metrics.get("target_leaves") or []
    scoped_leaf_ids = [t.get("leaf_id") for t in target_leaves if t.get("leaf_id")]
    if not scoped_leaf_ids:
        # Fallback — pull from _fetch_leaves_for_controls the same way
        from rag.intake.extractor import (
            _fetch_leaves_for_controls, _scope_controls_via_retrieval,
            _scope_controls_via_doc_mappings,
        )
        # Best effort — get all leaves under scoped controls
        scoped = (
            _scope_controls_via_doc_mappings(controls, doc)
            or _scope_controls_via_retrieval(controls, doc)
            or controls
        )
        scoped_leaf_ids = _fetch_leaves_for_controls(scoped[:40])

    cfg = default_config()
    consensus_result = run_extraction_consensus(doc, scoped_leaf_ids, cfg)

    # Aggregate metrics for Path A
    by_source_A = Counter()
    for f in findings_A:
        by_source_A[getattr(f, "inference_source", None) or "extracted"] += 1
    evidence_texts_A = [(f.evidence_text or "").strip() for f in findings_A]
    uniq_A = len(set(evidence_texts_A))

    # Aggregate metrics for Path B
    accepted = consensus_result.accepted()
    arbiter  = consensus_result.arbiter_zone()

    accepted_texts = [(v.fingerprint_excerpt or "").strip() for v in accepted]
    uniq_B_accept = len(set(t for t in accepted_texts if t))

    return {
        "path_a": {
            "total":             len(findings_A),
            "by_source":         dict(by_source_A),
            "unique_evidence":   uniq_A,
        },
        "path_b": {
            "total_candidates":  consensus_result.total_candidates,
            "n_accept":          consensus_result.n_accept,
            "n_arbiter":         consensus_result.n_arbiter,
            "n_drop":            consensus_result.n_drop,
            "signals_fired":     consensus_result.n_signals_fired,
            "signal_counts":     consensus_result.signal_fire_counts,
            "unique_evidence_accept": uniq_B_accept,
            "latency_ms":        consensus_result.latency_ms,
        },
    }


def main():
    print("=" * 72)
    print(" Ship 33'.b — consensus vs existing extraction (5-doc corpus)")
    print("=" * 72)

    paths = _load_upload_paths()
    all_metrics = {}
    total_a = total_b_accept = total_b_arbiter = total_b_drop = 0

    for filename in SHIP10_BASELINE:
        entry = paths.get(filename)
        if not entry:
            print(f"\n  ⚠ {filename}: no upload record — skipped")
            continue
        storage_path, upload_id = entry
        if not Path(storage_path).exists():
            print(f"\n  ⚠ {filename}: missing at {storage_path}")
            continue

        print(f"\n→ {filename}")
        try:
            m = _run_one_doc(filename, storage_path, upload_id)
        except Exception as e:
            import traceback
            print(f"    ✗ error: {type(e).__name__}: {e}")
            traceback.print_exc()
            continue

        all_metrics[filename] = m
        a = m["path_a"]; b = m["path_b"]
        print(f"    Path A (existing): {a['total']:>4d} findings  "
              f"unique_evidence={a['unique_evidence']:>3d}  by_source={a['by_source']}")
        print(f"    Path B (consensus): candidates={b['total_candidates']:>4d}  "
              f"accept={b['n_accept']:>3d}  arbiter={b['n_arbiter']:>3d}  drop={b['n_drop']:>3d}")
        print(f"       unique_evidence_accept={b['unique_evidence_accept']:>3d}  "
              f"signals_fired={b['signals_fired']}/7  {b['latency_ms']}ms")
        print(f"       signal_counts: {b['signal_counts']}")

        total_a += a["total"]
        total_b_accept  += b["n_accept"]
        total_b_arbiter += b["n_arbiter"]
        total_b_drop    += b["n_drop"]

    # Overall summary
    print("\n" + "=" * 72)
    print(" SUMMARY")
    print("=" * 72)
    print(f"  Path A (existing) total:     {total_a}")
    print(f"  Path B accepted (auto):      {total_b_accept}")
    print(f"  Path B arbiter (LLM zone):   {total_b_arbiter}")
    print(f"  Path B dropped:              {total_b_drop}")
    print(f"  Path B total-if-arbiter-all-pass: {total_b_accept + total_b_arbiter}")
    print(f"  Path B total-if-arbiter-all-fail: {total_b_accept}")

    # Persist JSON for later analysis
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    out = Path("/data/arioncomply/results") / f"ship33b_consensus_ab_{ts}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(all_metrics, indent=2, default=str))
    print(f"\n  Full metrics: {out}")

    return 0


if __name__ == "__main__":
    # Ship 30 hygiene — no-op expected but wired defensively
    _run_start = datetime.now(timezone.utc)
    try:
        rc = main()
    finally:
        try:
            from scripts.dev.demo_tenant_cleanup import cleanup_measurement_residue
            result = cleanup_measurement_residue(
                tenant_id = TENANT,
                since     = _run_start,
                dry_run   = False,
                reason    = "measure_ship33_consensus — auto-cleanup",
            )
            print(f"\n⤷ Ship 30 hygiene sweep: {result}")
        except Exception as e:
            print(f"\n⤷ Ship 30 hygiene sweep skipped: {type(e).__name__}: {e}")
    sys.exit(rc or 0)
