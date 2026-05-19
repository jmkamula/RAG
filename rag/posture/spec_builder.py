"""ArionComply — Neo4j → SpecDescriptor builder.

Reads the FulfilmentSpec subtree for a given RequirementNode and assembles
the in-memory SpecDescriptor that fulfilment_engine consumes. Tenant-
independent (the graph defines what's required; tenant supply is queried
by the engine's leaf evaluators).

Public surface:
    build_spec_descriptor(neo4j_session, control_id) -> SpecDescriptor | None
    build_specs_for_controls(neo4j_driver, control_ids) -> dict[control_id, SpecDescriptor]
    list_curated_control_ids(neo4j_driver) -> list[str]

Phase 1: handles flat specs (one level of leaves under FulfilmentSpec).
Nested FulfilmentSpec children are recognised by the walker but the only
shape currently in the data is RequirementNode → FulfilmentSpec → leaves.
Nesting is added when curators need it (e.g. Walk 2's 9.2 internal/external
audit ANY-of branch).
"""
from __future__ import annotations

from rag.posture.fulfilment_engine import Edge, LeafSpec, SpecDescriptor


_SPEC_QUERY = """
MATCH (rn:RequirementNode {id: $control_id})-[:SATISFIED_BY]->(fs:FulfilmentSpec)
OPTIONAL MATCH (fs)-[edge:REQUIRES_EVIDENCE]->(er:EvidenceRequirement)
OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(mi:ChecklistItem)
WITH rn, fs, edge, er, collect(DISTINCT mi.text) AS must_texts
OPTIONAL MATCH (er)-[:SHOULD_CONTAIN]->(si:ChecklistItem)
WITH rn, fs, edge, er, must_texts, collect(DISTINCT si.text) AS should_texts
RETURN
    rn.id              AS control_id,
    fs.id              AS spec_id,
    fs.op              AS op,
    fs.n               AS n,
    fs.applies_when    AS spec_applies_when,
    fs.curation_status AS curation_status,
    er.id              AS leaf_id,
    er.evidence_type   AS evidence_type,
    er.title           AS title,
    er.freshness_days  AS freshness_days,
    er.control_ref     AS leaf_control_ref,
    er.standard_id     AS leaf_standard_id,
    edge.role          AS edge_role,
    edge.applies_when  AS edge_applies_when,
    must_texts,
    should_texts
"""


def build_spec_descriptor(neo4j_session, control_id: str) -> SpecDescriptor | None:
    """Build a SpecDescriptor for one control by reading its FulfilmentSpec
    subtree. Returns None if the control has no spec at all (i.e. the
    migration didn't create one — should not happen post-commit-1)."""
    rows = list(neo4j_session.run(_SPEC_QUERY, control_id=control_id))
    if not rows:
        return None

    first = rows[0]
    spec = SpecDescriptor(
        spec_id         = first["spec_id"],
        op              = first["op"] or "ALL",
        n               = first["n"],
        applies_when    = first["spec_applies_when"],
        curation_status = first["curation_status"] or "uncurated",
        control_id      = control_id,
        children        = [],
    )

    for row in rows:
        leaf_id = row["leaf_id"]
        if leaf_id is None:
            # Spec exists but has no REQUIRES_EVIDENCE children (uncurated case)
            continue
        leaf = LeafSpec(
            leaf_id        = leaf_id,
            evidence_type  = row["evidence_type"] or "",
            title          = row["title"] or "",
            freshness_days = row["freshness_days"],
            must_items     = list(row["must_texts"] or []),
            should_items   = list(row["should_texts"] or []),
            control_ref    = row["leaf_control_ref"] or "",
            standard_id    = row["leaf_standard_id"] or "",
        )
        edge = Edge(
            role         = row["edge_role"] or leaf.evidence_type,
            applies_when = row["edge_applies_when"],
            target       = leaf,
        )
        spec.children.append(edge)

    return spec


def build_specs_for_controls(neo4j_driver, control_ids: list[str]) -> dict[str, SpecDescriptor]:
    """Batch variant — one Neo4j session, one descriptor per control."""
    out: dict[str, SpecDescriptor] = {}
    if not control_ids:
        return out
    with neo4j_driver.session() as s:
        for cid in control_ids:
            spec = build_spec_descriptor(s, cid)
            if spec is not None:
                out[cid] = spec
    return out


def list_curated_control_ids(neo4j_driver) -> list[str]:
    """Return RequirementNode ids whose FulfilmentSpec has
    curation_status='curated'. These are the controls the engine should
    evaluate; uncurated/deferred/explicit_empty are handled by the engine
    itself if you pass them, but most callers want just the curated set."""
    with neo4j_driver.session() as s:
        result = s.run("""
            MATCH (rn:RequirementNode)-[:SATISFIED_BY]->(fs:FulfilmentSpec {curation_status: 'curated'})
            RETURN rn.id AS control_id
            ORDER BY rn.id
        """)
        return [row["control_id"] for row in result]
