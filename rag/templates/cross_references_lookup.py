"""
Per-control cross-references lookup for the template renderers.

Templates Pass 4 (2026-08-08). Reads xfw-bridge edges directly from
Neo4j at startup (process-lifetime cache; invalidated only on API
restart).

Data model — the graph already carries rich rationale prose per edge
(diagnostic 2026-08-08 confirmed 100% of sampled edges have curator-
authored `rationale` fields). No grounded YAML store needed; on-the-fly
resolution from the graph is sufficient.

Edges consumed (Ship 1.7 xfw dedicated lane):
    IMPLEMENTS   258 edges
    SUPPORTS     158 edges
    ENABLES       22 edges
    GOVERNANCE    14 edges

Skipped (surfaced via other UX):
    PREREQUISITE_OF        Ship 57' <<PREREQUISITES>>
    DERIVES_FROM           DerivedSpec mechanics
    TRIGGERS_OBLIGATION    cascade UX
    BLOCKS_WHEN            cascade UX

Cache keyed by source control_ref (NOT leaf_id) — edges connect
RequirementNodes, so all leaves under a control share the same
cross-reference set.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from threading import Lock

_LOCK = Lock()
_CACHE: dict[str, tuple["CrossRef", ...]] | None = None

_EDGE_TYPES = ("IMPLEMENTS", "SUPPORTS", "ENABLES", "GOVERNANCE")


@dataclass(frozen=True)
class CrossRef:
    edge_type: str          # 'IMPLEMENTS' | 'SUPPORTS' | 'ENABLES' | 'GOVERNANCE'
    dst_ref:   str          # 'Art.46'
    dst_std:   str          # 'GDPR:2016/679'
    dst_title: str          # human-readable target-control title (may be empty)
    rationale: str          # curator-authored WHY prose from the edge


def _extract_std(node_id: str) -> str:
    """Extract 'STANDARD:VERSION' portion from 'STANDARD:VERSION:REF'.
    E.g. 'GDPR:2016/679:Art.46' → 'GDPR:2016/679'."""
    parts = node_id.rsplit(":", 1)
    return parts[0] if len(parts) == 2 else node_id


def _build_cache() -> dict[str, tuple[CrossRef, ...]]:
    from neo4j import GraphDatabase
    drv = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"),
              os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")),
    )
    edges_by_src: dict[str, list[CrossRef]] = {}
    try:
        with drv.session() as s:
            for et in _EDGE_TYPES:
                q = f"""
                    MATCH (src:RequirementNode)-[e:{et}]->(dst:RequirementNode)
                    RETURN src.ref AS src_ref,
                           dst.id AS dst_id,
                           dst.ref AS dst_ref,
                           coalesce(dst.title, '') AS dst_title,
                           coalesce(e.rationale, '') AS rationale
                """
                for row in s.run(q).data():
                    src_ref = row["src_ref"]
                    if not src_ref:
                        continue
                    dst_std = _extract_std(row["dst_id"] or "")
                    edges_by_src.setdefault(src_ref, []).append(CrossRef(
                        edge_type=et,
                        dst_ref=row["dst_ref"] or "",
                        dst_std=dst_std,
                        dst_title=(row["dst_title"] or "").strip(),
                        rationale=(row["rationale"] or "").strip(),
                    ))
    finally:
        drv.close()

    # Freeze lists → tuples + stable ordering (edge_type priority, then dst_ref).
    _priority = {t: i for i, t in enumerate(_EDGE_TYPES)}
    return {
        ref: tuple(sorted(edges, key=lambda c: (_priority.get(c.edge_type, 99), c.dst_ref)))
        for ref, edges in edges_by_src.items()
    }


def get_cross_references_for_control(control_ref: str) -> tuple[CrossRef, ...]:
    """Return the outbound xfw-bridge edges for a RequirementNode ref.
    Empty tuple = no bridges (renderer should suppress the block)."""
    global _CACHE
    if _CACHE is None:
        with _LOCK:
            if _CACHE is None:
                _CACHE = _build_cache()
    return _CACHE.get(control_ref, ())


def get_cross_references_for_leaf(leaf_id: str) -> tuple[CrossRef, ...]:
    """Convenience: extract control_ref from leaf_id and look up."""
    # leaf_id shape: 'req:CTRL:SLUG' — control_ref is the middle piece.
    parts = leaf_id.split(":", 2)
    if len(parts) < 3:
        return ()
    return get_cross_references_for_control(parts[1])


def prime_cache() -> None:
    """Force resolution at startup rather than at first render."""
    _ = get_cross_references_for_control("__prime__")
