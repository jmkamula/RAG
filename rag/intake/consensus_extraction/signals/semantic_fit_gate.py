"""
Signal: semantic_fit_gate — per-pair cosine similarity between
fingerprint excerpt and MUST's canonical text.

For each candidate that fingerprint_keyword emitted (has an
excerpt), compute cosine(embed(excerpt), embed(must_text)) and
emit +pass_weight or -fail_weight based on threshold.

This is the key signal for solving Ship 32's multi-attribution:
generic summary sentences will have low semantic fit to specific
MUSTs, so they get penalized here.
"""
from __future__ import annotations

from typing import Any

from rag.intake.consensus_extraction.types import (
    ExtractionSignalOutput,
    CandidateKey,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
)


def compute(
    doc:                     Any,
    scoped_leaf_ids:         list[str],
    cfg:                     ExtractionConsensusConfig,
    fingerprint_signal:      ExtractionSignalOutput = None,
) -> ExtractionSignalOutput:
    """Depends on fingerprint_keyword output (excerpts) — must run
    AFTER fingerprint_keyword. Orchestrator passes the fingerprint
    signal via `fingerprint_signal`.

    For each fingerprinted candidate, embed the excerpt + the MUST
    text, compute cosine, emit +/- weight vs threshold.
    """
    if not fingerprint_signal or not fingerprint_signal.fired:
        return ExtractionSignalOutput(name="semantic_fit_gate", fired=False)

    per_candidate = fingerprint_signal.metadata.get("per_candidate", {}) or {}
    if not per_candidate:
        return ExtractionSignalOutput(name="semantic_fit_gate", fired=False)

    # Fetch MUST texts for candidate must_ids in one batch
    must_ids = {mid for (_lid, mid) in per_candidate.keys() if mid}
    must_texts = _fetch_must_texts(list(must_ids))

    from rag.intake.critic_verifier import _get_embed_fn, _semantic_fit_ok
    embed_fn = _get_embed_fn()
    if embed_fn is None:
        # Fail-open — same discipline as critic path when embeddings unavailable
        return ExtractionSignalOutput(name="semantic_fit_gate", fired=False)

    candidates: dict[CandidateKey, float] = {}
    n_pass = n_fail = 0
    per_cand_meta: dict[CandidateKey, dict] = {}

    for key, meta in per_candidate.items():
        excerpt = meta.get("excerpt")
        must_id = key[1]
        if not excerpt or not must_id:
            continue
        must_text = must_texts.get(must_id, "")
        if not must_text:
            # No MUST text available → fail-open, don't penalize
            continue
        fit_ok, reason, sim = _semantic_fit_ok(excerpt, must_text, embed_fn)
        if fit_ok:
            candidates[key] = cfg.semantic_fit_pass_weight
            n_pass += 1
        else:
            candidates[key] = cfg.semantic_fit_fail_weight
            n_fail += 1
        per_cand_meta[key] = {"similarity": round(sim, 3), "reason": reason}

    return ExtractionSignalOutput(
        name       = "semantic_fit_gate",
        candidates = candidates,
        metadata   = {"n_pass": n_pass, "n_fail": n_fail,
                      "per_candidate": per_cand_meta},
        fired      = True,
    )


def _fetch_must_texts(must_ids: list[str]) -> dict[str, str]:
    """Look up MUST canonical text from Neo4j. Cached at process
    level to avoid repeat queries within a batch."""
    if not must_ids:
        return {}
    global _MUST_TEXT_CACHE
    try:
        _MUST_TEXT_CACHE
    except NameError:
        _MUST_TEXT_CACHE = {}

    missing = [m for m in must_ids if m not in _MUST_TEXT_CACHE]
    if not missing:
        return {m: _MUST_TEXT_CACHE[m] for m in must_ids}

    try:
        from rag.posture_loader import _build_engine_neo4j_driver
        driver = _build_engine_neo4j_driver()
        if driver is None:
            return {m: _MUST_TEXT_CACHE.get(m, "") for m in must_ids}
        with driver.session() as s:
            rows = s.run(
                """
                MATCH (c:ChecklistItem)
                 WHERE c.id IN $ids
                RETURN c.id AS id, c.text AS text
                """,
                ids=missing,
            ).data()
        for r in rows:
            _MUST_TEXT_CACHE[r["id"]] = r.get("text") or ""
        try:
            driver.close()
        except Exception:
            pass
    except Exception:
        pass

    return {m: _MUST_TEXT_CACHE.get(m, "") for m in must_ids}


_MUST_TEXT_CACHE: dict[str, str] = {}
