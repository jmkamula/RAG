"""Ship 60'.a — leaf structure fetcher (curation-invariant Neo4j lookup).

Provides `get_control_leaves(control_ref, standard_id)` returning a
`ControlLeaves` snapshot of a curated control's spec:

    ControlLeaves(
        control_ref  = "A.5.15",
        standard_id  = "ISO27001:2022",
        spec_op      = "ALL",
        leaves       = [
            LeafInfo(
                leaf_id       = "req:A.5.15:access_control_policy",
                title         = "Access Control Policy",
                evidence_type = "policy",
                must_ids      = ["item:A.5.15:approval", ...],
                must_texts    = {"item:A.5.15:approval": "The policy is
                                approved by top management.", ...},
                should_ids    = [...],
                should_texts  = {...},
            ),
            ...
        ]
    )

This is the *structural* half of what `evaluate_one_control` used to
return; the *fulfillment* half (which MUSTs are satisfied per tenant)
now lives in `posture_must_verdicts` (Ship 58'/59' SSoT). Consumers
join both to render advisory data.

Design:
- Tenant-agnostic: same data across all tenants (curator-authored).
  Cache key is `(standard_id, control_ref)` — no tenant dimension.
- 30-second TTL cache matches `_cached_er_evidence_types` pattern in
  engine_runner.py. Long enough to absorb one chat turn's fan-out;
  short enough that a curation reload is picked up within seconds.
- Silent fallback: any Neo4j failure returns None; consumers treat
  as "structure unavailable" and skip the advisory (same as
  evaluate_one_control's error contract).
- Driver reuse: `_get_neo_driver()` from advisory.py — module-level
  singleton lazy-created on first use. Ship 60'.a keeps the same
  discipline.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LeafInfo:
    """One EvidenceRequirement leaf under a control's FulfilmentSpec.

    `must_ids` preserves author order (matches engine's iteration order
    for stable UI rendering). `must_texts` is a lookup by id.
    """
    leaf_id:       str
    title:         str
    evidence_type: str
    must_ids:      tuple[str, ...]
    must_texts:    dict[str, str]
    should_ids:    tuple[str, ...] = ()
    should_texts:  dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ControlLeaves:
    """The structural view of a control's FulfilmentSpec.

    `spec_op` is the composition operator ('ALL' | 'ANY' | 'NONE_OF' |
    etc.) — consumers that display posture reasoning can surface this.
    """
    control_ref: str
    standard_id: str
    spec_op:     str
    leaves:      tuple[LeafInfo, ...]


# ── query + cache ────────────────────────────────────────────────────────────

_QUERY = """
MATCH (rn:RequirementNode {id: $control_id})-[:SATISFIED_BY]->(fs:FulfilmentSpec)
OPTIONAL MATCH (fs)-[:REQUIRES_EVIDENCE]->(er:EvidenceRequirement)
OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(mi:ChecklistItem)
WITH rn, fs, er,
     collect(DISTINCT {id: mi.id, text: mi.text}) AS musts
OPTIONAL MATCH (er)-[:SHOULD_CONTAIN]->(si:ChecklistItem)
RETURN
    fs.op            AS spec_op,
    er.id            AS leaf_id,
    er.title         AS title,
    er.evidence_type AS evidence_type,
    musts,
    collect(DISTINCT {id: si.id, text: si.text}) AS shoulds
"""


_CACHE: dict[tuple[str, str], tuple[float, Optional[ControlLeaves]]] = {}
_TTL_S = 30.0


def get_control_leaves(
    control_ref: str,
    standard_id: str = "ISO27001:2022",
    *,
    neo4j_driver = None,
) -> Optional[ControlLeaves]:
    """Return the structural spec view for a control, or None if the
    control has no curated FulfilmentSpec / Neo4j is unavailable.

    Callers pass in a driver when one is already open (batched callers
    reuse driver + session); when omitted, uses the module-level lazy
    driver from `rag.posture.advisory._get_neo_driver`.
    """
    if not control_ref:
        return None

    key = (standard_id, control_ref)
    hit = _CACHE.get(key)
    if hit is not None:
        ts, val = hit
        if (time.monotonic() - ts) < _TTL_S:
            return val

    if neo4j_driver is None:
        # Reuse the singleton driver established by advisory.py so we
        # don't double-open a connection pool. Circular import guard:
        # imported lazily.
        try:
            from rag.posture.advisory import _get_neo_driver
            neo4j_driver = _get_neo_driver()
        except Exception:
            neo4j_driver = None
    if neo4j_driver is None:
        return None

    control_id = f"{standard_id}:{control_ref}"
    try:
        with neo4j_driver.session() as s:
            rows = list(s.run(_QUERY, control_id=control_id))
    except Exception as e:
        logger.warning("leaf_structure: neo4j query failed for %s: %s",
                       control_id, e)
        return None

    if not rows:
        _CACHE[key] = (time.monotonic(), None)
        return None

    spec_op = (rows[0]["spec_op"] or "ALL")
    leaves: list[LeafInfo] = []
    for row in rows:
        leaf_id = row.get("leaf_id")
        if not leaf_id:
            continue  # spec exists but no REQUIRES_EVIDENCE children
        must_records   = [m for m in (row.get("musts")   or []) if m and m.get("id")]
        should_records = [s for s in (row.get("shoulds") or []) if s and s.get("id")]
        must_ids   = tuple(m["id"] for m in must_records)
        should_ids = tuple(s["id"] for s in should_records)
        leaves.append(LeafInfo(
            leaf_id       = leaf_id,
            title         = row.get("title")         or "",
            evidence_type = row.get("evidence_type") or "",
            must_ids      = must_ids,
            must_texts    = {m["id"]: (m.get("text") or "") for m in must_records},
            should_ids    = should_ids,
            should_texts  = {s["id"]: (s.get("text") or "") for s in should_records},
        ))

    if not leaves:
        _CACHE[key] = (time.monotonic(), None)
        return None

    result = ControlLeaves(
        control_ref = control_ref,
        standard_id = standard_id,
        spec_op     = spec_op,
        leaves      = tuple(leaves),
    )
    _CACHE[key] = (time.monotonic(), result)
    return result


def cache_clear() -> None:
    """Test/dev helper — drops the process-level cache."""
    _CACHE.clear()
