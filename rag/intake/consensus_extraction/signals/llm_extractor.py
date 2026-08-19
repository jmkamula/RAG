"""
Signal: llm_extractor — Ship 81'.b — LLM as discovery signal.

Motivation from Ship 81'.a signal analysis (100-candidate sample):
- fingerprint_keyword fires on 100% of TPs but 96% of FPs — indiscriminate
- bm25_topk at 26% precision, adds volume not signal
- Union+critic path had the LLM as VERIFIER on consensus's accepts —
  Ship 80'.d proved that under-serves recall.

New role: LLM sits ALONGSIDE deterministic signals in the discovery
phase. Calls critic-verifier's extract-once pipeline (LLM sees the
doc + scoped controls, emits per-MUST votes for what it observes).
Signal contributes weight per-candidate to the aggregator; corroborates
alongside must_semantic_topk / explicit_ref / doc_mappings_target.

Mode selection via cfg:
  llm_signal_mode = "extract_once"  — one LLM call per doc, cheap
                                       (~$0.005), broad discovery
  llm_signal_mode = "per_must"      — one LLM call per candidate MUST
                                       (~$0.30 per doc), per-MUST rigor

Fail-open: any error → empty signal (extraction continues).
"""
from __future__ import annotations

import logging
from typing import Any

from rag.intake.consensus_extraction.types import (
    ExtractionSignalOutput,
    CandidateKey,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
)

logger = logging.getLogger(__name__)


def compute(
    doc:              Any,   # ParsedDocument
    scoped_leaf_ids:  list[str],
    cfg:              ExtractionConsensusConfig,
) -> ExtractionSignalOutput:
    """Return an ExtractionSignalOutput with per-MUST candidates
    from the LLM extractor. Weight applied per candidate = cfg.llm_extractor_weight.

    Fail-open on any error so the pipeline continues.
    """
    if not getattr(cfg, "llm_extractor_enabled", False):
        return ExtractionSignalOutput(name="llm_extractor", fired=False)

    if not scoped_leaf_ids:
        return ExtractionSignalOutput(name="llm_extractor", fired=False)

    mode = getattr(cfg, "llm_signal_mode", "extract_once")
    weight = getattr(cfg, "llm_extractor_weight", 0.40)

    try:
        if mode == "per_must":
            candidates = _compute_per_must(doc, scoped_leaf_ids, cfg, weight)
        else:
            candidates = _compute_extract_once(doc, scoped_leaf_ids, cfg, weight)
    except Exception as e:
        logger.warning("llm_extractor signal failed for %s (%s); fail-open",
                       getattr(doc, "original_name", "<unknown>"), e)
        return ExtractionSignalOutput(name="llm_extractor", fired=False)

    return ExtractionSignalOutput(
        name       = "llm_extractor",
        candidates = candidates,
        fired      = True,
        metadata   = {"mode": mode, "n_candidates": len(candidates)},
    )


def _compute_extract_once(
    doc:              Any,
    scoped_leaf_ids:  list[str],
    cfg:              ExtractionConsensusConfig,
    weight:           float,
) -> dict[CandidateKey, float]:
    """One LLM call per doc — reuses critic-verifier's extract pipeline.

    Priming set = top control_refs from scoped leaves (deduped).
    Extend pool = Chroma semantic top-K (broadens beyond fingerprint).
    """
    from rag.intake.critic_verifier import (
        _build_priming_set, _build_extend_pool,
        build_control_meta_from_neo4j, _extract_critic_verifier,
    )
    from rag.intake.must_embedding_lookup import semantic_controls_in_scope
    from rag.posture_loader import _build_engine_neo4j_driver

    # Build the priming inputs from scoped leaves — we don't have
    # fingerprint hits at this stage (that's a downstream signal in
    # llm-signal mode), so we seed from control_refs directly.
    control_refs = sorted({lid.split(":")[1] for lid in scoped_leaf_ids
                           if lid.startswith("req:")})
    semantic_top_k = semantic_controls_in_scope(
        doc_text    = doc.markdown or doc.full_text,
        tenant_stds = doc.standard_ids or None,
    ) or set()
    explicit_refs = set(doc.explicit_refs or [])

    all_refs = set(control_refs) | semantic_top_k | explicit_refs
    driver = _build_engine_neo4j_driver()
    meta = build_control_meta_from_neo4j(list(all_refs), driver) if driver else {}
    try:
        driver and driver.close()
    except Exception:
        pass

    # Priming shape: cast each scoped control_ref as a fingerprint-hit
    # placeholder so _build_priming_set sees "signal" behind it.
    priming_hits = [{"control_ref": r, "must_id": None, "standard_id": None}
                    for r in control_refs]
    priming     = _build_priming_set(
        priming_hits, semantic_top_k, explicit_refs, meta,
        max_size = getattr(cfg, "llm_signal_priming_max", 40),
    )
    extend_pool = _build_extend_pool(
        doc.full_text, tenant_stds=doc.standard_ids or None,
        pool_size = getattr(cfg, "llm_signal_pool_size", 100),
    )
    if not priming and not extend_pool:
        return {}

    parsed, err = _extract_critic_verifier(doc, priming, extend_pool)
    if err:
        logger.warning("llm_extractor: critic extract failed for %s: %s",
                       doc.original_name, err)
        return {}

    # Convert LLM's confirmed + extended sets into candidate votes.
    # Confidence "high" → full weight; "medium" → 0.80× weight; "low" → 0.60×.
    # Ship 81'.b fix — leaf_id resolution via Neo4j (same helper as
    # must_semantic_topk); priming.candidate_musts doesn't carry it.
    conf_scale = {"high": 1.0, "medium": 0.80, "low": 0.60}
    from rag.intake.consensus_extraction.signals.must_semantic_topk import (
        _resolve_must_to_leaf,
    )

    entries = (parsed.get("confirmed") or []) + (parsed.get("extended") or [])
    must_ids = [e.get("checklist_item_id") for e in entries if e.get("checklist_item_id")]
    leaf_by_must = _resolve_must_to_leaf(must_ids) if must_ids else {}

    candidates: dict[CandidateKey, float] = {}
    for entry in entries:
        must_id = entry.get("checklist_item_id")
        if not must_id:
            continue
        leaf_id = leaf_by_must.get(must_id, "")
        if not leaf_id:
            # Skip — can't emit a candidate without leaf_id
            continue
        conf = entry.get("confidence", "medium")
        w = weight * conf_scale.get(conf, 0.80)
        key: CandidateKey = (leaf_id, must_id)
        # Take max weight if this MUST already appeared
        candidates[key] = max(candidates.get(key, 0.0), w)

    return candidates


_PER_MUST_SYSTEM = """You are a compliance evidence classifier.

You will be given a document excerpt and a batch of MUST items (with slug + description). For EACH MUST, judge whether the document contains evidence satisfying that MUST.

Return strict JSON: {"verdicts": [{"must_id": "item:X:Y", "verdict": "yes|no", "confidence": "high|medium|low", "quote": "<verbatim excerpt or empty>"}, ...]}

Rules:
- "yes" means: the document has language a compliance auditor would accept as evidence for this specific MUST.
- "no" means: the document does not carry evidence for this MUST (default when uncertain).
- confidence "high" only when the evidence is direct and unambiguous.
- quote: a verbatim substring from the document (≤ 200 chars). Empty string when verdict is "no".
- Do not fabricate evidence. Only cite text that actually appears in the doc.
- Emit one entry per input must_id. Preserve order.
- Return JSON only. No prose."""


def _compute_per_must(
    doc:              Any,
    scoped_leaf_ids:  list[str],
    cfg:              ExtractionConsensusConfig,
    weight:           float,
) -> dict[CandidateKey, float]:
    """Ship 81'.d — per-MUST batched LLM scoring.

    For each MUST on each scoped leaf, ask the LLM (in batches of ~15)
    whether the document contains evidence. LLM's per-MUST verdict maps
    to weight via confidence scaling (same as extract_once mode).

    Cost: 200-300 MUSTs per doc × ~1 LLM call per 15 MUSTs ≈ ~15 calls
    per doc, ~$0.10-0.15 per doc via gpt-4.1-mini. Vs $0.005 for
    extract_once mode — 20-30x cost, but complete MUST coverage.
    """
    from rag.llm_client import call as llm_call
    from neo4j import GraphDatabase
    import os as _os
    import json as _json

    # Fetch all MUSTs for scoped_leaf_ids
    uri  = _os.getenv("NEO4J_URI")
    user = _os.getenv("NEO4J_USER")
    pw   = _os.getenv("NEO4J_PASSWORD")
    if not (uri and user and pw):
        logger.warning("llm_extractor per_must: Neo4j creds missing; fail-open")
        return {}
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    try:
        with driver.session() as s:
            rows = s.run(
                """
                MATCH (er:EvidenceRequirement)-[:MUST_CONTAIN]->(ci:ChecklistItem)
                 WHERE er.id IN $leaf_ids
                RETURN er.id AS leaf_id, ci.id AS must_id, ci.text AS text
                ORDER BY leaf_id, must_id
                """,
                leaf_ids=list(scoped_leaf_ids),
            ).data()
    finally:
        try:
            driver.close()
        except Exception:
            pass

    if not rows:
        return {}

    logger.info("llm_extractor per_must: %d MUSTs on %d leaves for %s",
                len(rows), len(scoped_leaf_ids), doc.original_name)

    # Doc text — cap at ~30K chars so the LLM prompt stays under budget
    doc_text = (doc.markdown or doc.full_text or "")[:30000]

    # Batch MUSTs into groups of 15
    BATCH_SIZE = getattr(cfg, "llm_per_must_batch_size", 15)
    conf_scale = {"high": 1.0, "medium": 0.80, "low": 0.60}
    candidates: dict[CandidateKey, float] = {}

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        must_lines = []
        for r in batch:
            slug = r["must_id"].split(":")[-1]
            text = (r.get("text") or "").strip()[:180]
            must_lines.append(f"  - {r['must_id']}  |  {slug}  |  {text}")
        user_prompt = (
            f"DOCUMENT (excerpt):\n{doc_text[:8000]}\n\n"
            f"BATCH OF MUSTs (id | slug | description):\n"
            + "\n".join(must_lines) +
            f"\n\nJudge each MUST. Return the JSON schema described."
        )
        try:
            resp = llm_call(
                system      = _PER_MUST_SYSTEM,
                user        = user_prompt,
                model       = "gpt-4.1-mini",
                purpose     = "extractor",
                max_tokens  = 2000,
                temperature = 0.1,
                timeout_s   = 60,
                response_format = {"type": "json_object"},
            )
        except Exception as e:
            logger.warning("llm_extractor per_must batch %d failed: %s (fail-open batch)", i//BATCH_SIZE, e)
            continue
        if getattr(resp, "error", None):
            logger.warning("llm_extractor per_must batch %d error: %s", i//BATCH_SIZE, resp.error)
            continue
        try:
            data = _json.loads(resp.text or "{}")
        except Exception:
            continue
        for v in data.get("verdicts", []) or []:
            if v.get("verdict") != "yes":
                continue
            must_id = v.get("must_id")
            if not must_id:
                continue
            # Look up the leaf_id from our batch
            leaf_id = next((r["leaf_id"] for r in batch if r["must_id"] == must_id), None)
            if not leaf_id:
                continue
            conf = v.get("confidence", "medium")
            w = weight * conf_scale.get(conf, 0.80)
            key: CandidateKey = (leaf_id, must_id)
            candidates[key] = max(candidates.get(key, 0.0), w)

    logger.info("llm_extractor per_must: %d yes-verdicts on %d MUSTs (%s)",
                len(candidates), len(rows), doc.original_name)
    return candidates
