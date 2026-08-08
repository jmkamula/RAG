"""
Per-MUST guidance lookup for the template renderers.

Shipped in Ship 56'.a (2026-08-05). Reads from the Python catalog after
lazily resolving the flat YAML store under enrichment/guidance/.
Process-lifetime cache; invalidated only on API restart.

Both renderers import get_guidance_for_item() to resolve the guidance
for a <<GUIDANCE>> marker by looking up the preceding <<MUST item:X>>'s
item_id.
"""
from __future__ import annotations

from threading import Lock

_LOCK = Lock()
_CACHE: dict[str, tuple[str, ...]] | None = None


def _build_cache() -> dict[str, tuple[str, ...]]:
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS,
        ALL_DERIVED_SPECS,
    )
    from enrichment.guidance.apply_to_catalog import apply_guidance_to_catalog

    apply_guidance_to_catalog(ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS)

    cache: dict[str, tuple[str, ...]] = {}
    all_ers = list(ALL_EVIDENCE_REQUIREMENTS) + [
        er for ds in ALL_DERIVED_SPECS for er in ds.direct_evidence
    ]
    for er in all_ers:
        for item in list(er.must_contain) + list(er.should_contain):
            cache[item.id] = tuple(item.guidance)
    return cache


def get_guidance_for_item(item_id: str) -> tuple[str, ...]:
    """Return the resolved guidance steps for a ChecklistItem id.
    Empty tuple = no bank hit (renderer should suppress the block).
    """
    global _CACHE
    if _CACHE is None:
        with _LOCK:
            if _CACHE is None:
                _CACHE = _build_cache()
    return _CACHE.get(item_id, ())


def prime_cache() -> None:
    """Force resolution at startup rather than at first render.
    Optional — safe to call multiple times."""
    _ = get_guidance_for_item("__prime__")
