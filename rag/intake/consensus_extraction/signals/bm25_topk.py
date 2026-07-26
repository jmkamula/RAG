"""
Signal: bm25_topk — lexical relevance scoring using rank-bm25 (BM25Okapi).

Ship 43'.b — 9th consensus_extraction signal. Fills the lexical-fuzzy
gap between fingerprint_keyword (exact token set match) and
must_semantic_topk (embedding-based semantic similarity).

Same discovery-mode shape as must_semantic_topk: emits candidates
outside scoped_leaf_ids via top-K by BM25 score above a floor.
Orchestrator widens leaf pool by unioning must_semantic + BM25
candidates.

Per-doc BM25Okapi index over all MUSTs in the tenant's enrolled
frameworks (bounded lookup, cached). Query with doc tokens. Top-K
above score floor emit candidates with cfg.bm25_weight.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

from rag.intake.consensus_extraction.types import (
    ExtractionSignalOutput,
    CandidateKey,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
)


logger = logging.getLogger(__name__)

# Process-cached MUST catalog: [(leaf_id, must_id, must_text)] across all
# EvidenceRequirement → ChecklistItem edges in Neo4j. Populated lazily.
_MUST_CATALOG_CACHE: Optional[list[tuple[str, str, str]]] = None


_TOKEN_RE = re.compile(r"\b\w+\b")


def _tokenize(text: str) -> list[str]:
    """Simple lowercasing + word-boundary tokenization. No stemming for
    v1 — keep dependencies minimal; language-specific preprocessing is
    future work."""
    if not text:
        return []
    return _TOKEN_RE.findall(text.lower())


def _load_must_catalog() -> list[tuple[str, str, str]]:
    """Return all (leaf_id, must_id, must_text) triples from Neo4j.
    Cached at process level. Silent-fail returns empty list."""
    global _MUST_CATALOG_CACHE
    if _MUST_CATALOG_CACHE is not None:
        return _MUST_CATALOG_CACHE

    try:
        from rag.posture_loader import _build_engine_neo4j_driver
        driver = _build_engine_neo4j_driver()
        if driver is None:
            _MUST_CATALOG_CACHE = []
            return _MUST_CATALOG_CACHE
        with driver.session() as s:
            rows = s.run(
                """
                MATCH (er:EvidenceRequirement)-[:MUST_CONTAIN]->(ci:ChecklistItem)
                RETURN er.id AS leaf_id, ci.id AS must_id, ci.text AS must_text
                """,
            ).data()
        catalog = [
            (r["leaf_id"], r["must_id"], r["must_text"] or r["must_id"])
            for r in rows
            if r.get("leaf_id") and r.get("must_id")
        ]
        try:
            driver.close()
        except Exception:
            pass
        _MUST_CATALOG_CACHE = catalog
        logger.info(f"bm25_topk: loaded MUST catalog with {len(catalog)} items")
    except Exception as e:
        logger.warning(f"bm25_topk: Neo4j catalog fetch failed: {e}")
        _MUST_CATALOG_CACHE = []

    return _MUST_CATALOG_CACHE


def compute(
    doc:              Any,
    scoped_leaf_ids:  list[str],
    cfg:              ExtractionConsensusConfig,
) -> ExtractionSignalOutput:
    """Score all catalog MUSTs against doc text via BM25Okapi.
    Emit top-K above score floor.

    Discovery-mode: emits candidates regardless of whether their leaf
    is in scoped_leaf_ids. Orchestrator widens the leaf pool via union.
    """
    try:
        from rank_bm25 import BM25Okapi
    except Exception as e:
        logger.warning(f"bm25_topk: rank_bm25 unavailable: {e}")
        return ExtractionSignalOutput(name="bm25_topk", fired=False)

    doc_text = getattr(doc, "markdown", None) or getattr(doc, "full_text", None) or ""
    if not doc_text:
        return ExtractionSignalOutput(name="bm25_topk", fired=False)

    doc_tokens = _tokenize(doc_text)
    if not doc_tokens:
        return ExtractionSignalOutput(name="bm25_topk", fired=False)

    catalog = _load_must_catalog()
    if not catalog:
        return ExtractionSignalOutput(name="bm25_topk", fired=False)

    # Build per-doc index over MUSTs. Rebuilds each call; ~sub-second
    # for 2595 MUSTs. V2 candidate: cache the index or MUST tokens.
    must_tokens_per_item = [_tokenize(txt) for (_lid, _mid, txt) in catalog]
    # Filter out MUSTs with empty tokens to avoid division-by-zero in BM25
    valid_idx = [i for i, t in enumerate(must_tokens_per_item) if t]
    if not valid_idx:
        return ExtractionSignalOutput(name="bm25_topk", fired=False)

    valid_must_tokens = [must_tokens_per_item[i] for i in valid_idx]
    bm25 = BM25Okapi(valid_must_tokens)
    scores = bm25.get_scores(doc_tokens)

    # Pair scores with catalog entries; rank top-K above floor
    ranked = sorted(
        (
            (scores[j], catalog[valid_idx[j]])
            for j in range(len(valid_idx))
        ),
        key=lambda x: x[0],
        reverse=True,
    )

    candidates: dict[CandidateKey, float] = {}
    n_above_floor = 0
    top_scores_sample = []
    for score, (leaf_id, must_id, _text) in ranked[: cfg.bm25_topk]:
        if score < cfg.bm25_score_floor:
            break
        candidates[(leaf_id, must_id)] = cfg.bm25_weight
        n_above_floor += 1
        if len(top_scores_sample) < 5:
            top_scores_sample.append(round(float(score), 2))

    return ExtractionSignalOutput(
        name       = "bm25_topk",
        candidates = candidates,
        metadata   = {
            "n_catalog":      len(catalog),
            "n_doc_tokens":   len(doc_tokens),
            "n_above_floor":  n_above_floor,
            "top_scores":     top_scores_sample,
            "score_floor":    cfg.bm25_score_floor,
        },
        fired      = True,
    )
