"""
MUST-level semantic lookup — signal-fusion Wave 2 (2026-07-09).

Given a doc's content, returns the set of MUST ids semantically most
similar to any passage in the doc. Used as an INDEPENDENT
corroboration signal alongside doc_mappings' filename/topic-token
match: a fingerprint_match auto-approves when EITHER signal (or both)
corroborate the control's presence in the doc.

Companion to `scripts/build_must_index.py` which builds the
`musts_arioncomply` Chroma collection.

Model: `text-embedding-3-small` (matches the collection).

Cost: one embedding call per doc (or per chunk if the doc exceeds the
context budget). Query is a single Chroma nearest-neighbor lookup —
milliseconds after the embedding call.

Silent fallback: if the collection is missing, the OPENAI key is
absent, or any error surfaces, returns an empty set — corroboration
degrades to doc_mappings only. Never blocks intake.
"""
from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

COLLECTION_NAME = "musts_arioncomply"
CHROMA_DIR      = str(Path(__file__).resolve().parents[2] / "chroma_db")
EMBED_MODEL     = "text-embedding-3-small"

# Query budget — take the first N chars of the doc as the query. Docs
# larger than this are covered by a summary window; the top-K return
# (below) is generous enough that concept coverage still lands.
_QUERY_CHAR_LIMIT = 6000
# top_k=30 tuned 2026-07-09 as the precision/recall sweet spot: DSR
# content (which nominally mentions "transfers" in identity-verification
# context) correctly excludes A.7.5.2 transfer-destinations; a transfer-
# destinations doc correctly includes A.7.5.2. K=100+ pulls A.7.5.2
# into DSR results (false semantic co-occurrence). K=10 misses
# legitimate secondary controls. K=30 is the sharp knee.
_DEFAULT_TOP_K    = 30

_COLLECTION_CACHE: object = None


def _get_collection():
    """Lazy-initialise the Chroma collection handle. Cached per process.
    Returns None on any failure (missing collection, chroma init error,
    OpenAI key absent) — caller degrades gracefully."""
    global _COLLECTION_CACHE
    if _COLLECTION_CACHE is not None:
        return _COLLECTION_CACHE if _COLLECTION_CACHE is not False else None
    try:
        if not os.getenv("OPENAI_API_KEY"):
            logger.debug("OPENAI_API_KEY missing — MUST semantic lookup disabled")
            _COLLECTION_CACHE = False
            return None
        import chromadb
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
        embed_fn = OpenAIEmbeddingFunction(
            api_key    = os.getenv("OPENAI_API_KEY"),
            model_name = EMBED_MODEL,
        )
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        col    = client.get_collection(
            name              = COLLECTION_NAME,
            embedding_function= embed_fn,
        )
        _COLLECTION_CACHE = col
        return col
    except Exception as e:
        logger.warning("MUST semantic lookup unavailable: %s", e)
        _COLLECTION_CACHE = False
        return None


def semantic_musts_in_scope(
    doc_text:     Optional[str],
    top_k:        int = _DEFAULT_TOP_K,
    tenant_stds:  Optional[list[str]] = None,
) -> set[str]:
    """Return the set of `must_id`s semantically most similar to
    `doc_text`. Empty set on any failure. When `tenant_stds` is
    supplied, filters the result to MUSTs whose `standard_id` is in
    that list — avoids corroborating on out-of-scope standards.

    Binary corroboration signal: a MUST either is in the top-K
    (semantically related to the doc) or it's not. No per-MUST score
    surfaced — the writer's gate just needs "is this MUST plausibly
    in scope?".
    """
    if not doc_text:
        return set()
    col = _get_collection()
    if col is None:
        return set()
    try:
        query_text = doc_text[:_QUERY_CHAR_LIMIT]
        # Chroma filter on metadata when tenant_stds narrows the scope.
        # Not required for correctness — the top-K is deliberately generous —
        # but reduces noise + keeps out-of-scope refs from silently corroborating.
        where = None
        if tenant_stds:
            std_list = [s for s in tenant_stds if s]
            if std_list:
                where = {"standard_id": {"$in": std_list}}
        result = col.query(
            query_texts = [query_text],
            n_results   = top_k,
            where       = where,
            include     = ["metadatas"],
        )
        metadatas = (result or {}).get("metadatas") or []
        if not metadatas or not metadatas[0]:
            return set()
        return {md.get("must_id") for md in metadatas[0] if md and md.get("must_id")}
    except Exception as e:
        logger.warning("semantic_musts_in_scope failed: %s", e)
        return set()


def semantic_controls_in_scope(
    doc_text:    Optional[str],
    top_k:       int = _DEFAULT_TOP_K,
    tenant_stds: Optional[list[str]] = None,
) -> set[str]:
    """Convenience: return the set of `control_ref`s appearing in the
    top-K MUSTs. Used by the writer's corroboration gate — coarser than
    per-MUST but matches the granularity of fingerprint control_ref.
    """
    if not doc_text:
        return set()
    col = _get_collection()
    if col is None:
        return set()
    try:
        query_text = doc_text[:_QUERY_CHAR_LIMIT]
        where = None
        if tenant_stds:
            std_list = [s for s in tenant_stds if s]
            if std_list:
                where = {"standard_id": {"$in": std_list}}
        result = col.query(
            query_texts = [query_text],
            n_results   = top_k,
            where       = where,
            include     = ["metadatas"],
        )
        metadatas = (result or {}).get("metadatas") or []
        if not metadatas or not metadatas[0]:
            return set()
        return {md.get("control_ref") for md in metadatas[0] if md and md.get("control_ref")}
    except Exception as e:
        logger.warning("semantic_controls_in_scope failed: %s", e)
        return set()
