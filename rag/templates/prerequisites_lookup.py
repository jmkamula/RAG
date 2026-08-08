"""
Per-leaf prerequisites lookup for the template renderers.

Shipped in Ship 57' (2026-08-07). Reads from the Python catalog after
lazily resolving the flat YAML store under enrichment/prerequisites/.
Process-lifetime cache; invalidated only on API restart.

Both renderers import get_prerequisites_for_leaf() to resolve the
prerequisites for a <<PREREQUISITES>> marker by looking up the leaf's
EvidenceRequirement id.
"""
from __future__ import annotations

from threading import Lock

from enrichment.documents.document_requirements import Prerequisite

_LOCK = Lock()
_CACHE: dict[str, tuple[Prerequisite, ...]] | None = None


def _build_cache() -> dict[str, tuple[Prerequisite, ...]]:
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS,
        ALL_DERIVED_SPECS,
    )
    from enrichment.prerequisites.apply_to_catalog import apply_prerequisites_to_catalog

    apply_prerequisites_to_catalog(ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS)

    cache: dict[str, tuple[Prerequisite, ...]] = {}
    all_ers = list(ALL_EVIDENCE_REQUIREMENTS) + [
        er for ds in ALL_DERIVED_SPECS for er in ds.direct_evidence
    ]
    for er in all_ers:
        cache[er.id] = tuple(er.prerequisites)
    return cache


def get_prerequisites_for_leaf(leaf_id: str) -> tuple[Prerequisite, ...]:
    """Return the resolved prerequisites for an EvidenceRequirement id.
    Empty tuple = no bank hit (renderer should suppress the block).
    """
    global _CACHE
    if _CACHE is None:
        with _LOCK:
            if _CACHE is None:
                _CACHE = _build_cache()
    return _CACHE.get(leaf_id, ())


def prime_cache() -> None:
    """Force resolution at startup rather than at first render.
    Optional — safe to call multiple times."""
    _ = get_prerequisites_for_leaf("__prime__")
