"""ArionComply — Neo4j → SpecDescriptor builder.

Reads the FulfilmentSpec subtree for a given RequirementNode and assembles
the in-memory SpecDescriptor that fulfilment_engine consumes. Tenant-
independent (the graph defines what's required; tenant supply is queried
by the engine's leaf evaluators).

Public surface:
    build_spec_descriptor(neo4j_session, control_id) -> SpecDescriptor | None
    build_specs_for_controls(neo4j_driver, control_ids) -> dict[control_id, SpecDescriptor]
    list_curated_control_ids(neo4j_driver) -> list[str]
    build_spec_resolver(neo4j_session) -> SpecResolverFn

Phase 1: handles flat specs (one level of leaves under FulfilmentSpec).
Nested FulfilmentSpec children are recognised by the walker but the only
shape currently in the data is RequirementNode → FulfilmentSpec → leaves.
Nesting is added when curators need it (e.g. Walk 2's 9.2 internal/external
audit ANY-of branch).

Phase 2 (this commit): DERIVES_FROM edges on FulfilmentSpec become ControlRef
edges on the SpecDescriptor. build_spec_resolver returns a closure suitable
for evaluate_spec's spec_resolver parameter, so the engine can walk derived
specs end-to-end against Neo4j.
"""
from __future__ import annotations

from rag.posture.fulfilment_engine import ControlRef, Edge, LeafSpec, SpecDescriptor, SpecResolverFn


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


_DERIVES_FROM_QUERY = """
MATCH (rn:RequirementNode {id: $control_id})-[:SATISFIED_BY]->(fs:FulfilmentSpec)
MATCH (fs)-[df:DERIVES_FROM]->(target:RequirementNode)
RETURN
    target.id          AS target_control_id,
    df.role            AS role,
    df.applies_when    AS applies_when,
    df.title           AS title,
    df.scope_items     AS scope_items
ORDER BY df.role
"""


def build_spec_descriptor(neo4j_session, control_id: str) -> SpecDescriptor | None:
    """Build a SpecDescriptor for one control by reading its FulfilmentSpec
    subtree. Returns None if the control has no spec at all (i.e. the
    migration didn't create one — should not happen post-commit-1).

    Pulls both REQUIRES_EVIDENCE children (LeafSpec edges) and DERIVES_FROM
    children (ControlRef edges) — a spec can have either or both."""
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
            # Spec exists but has no REQUIRES_EVIDENCE children
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

    # DERIVES_FROM children — emitted as ControlRef edges
    for row in neo4j_session.run(_DERIVES_FROM_QUERY, control_id=control_id):
        spec.children.append(Edge(
            role         = row["role"] or "",
            applies_when = row["applies_when"],
            target       = ControlRef(
                target_control_id = row["target_control_id"],
                title             = row["title"] or "",
                scope_items       = list(row["scope_items"]) if row["scope_items"] else None,
            ),
        ))

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


def build_spec_resolver(neo4j_session) -> SpecResolverFn:
    """Return a SpecResolverFn that resolves control_id → SpecDescriptor against
    the given Neo4j session, with per-call memoization so a single engine query
    only reads each control once even if multiple parents reference it.

    Pass this into evaluate_spec/evaluate_control as spec_resolver to walk
    derived specs end-to-end. The session is captured by closure — caller
    owns its lifetime."""
    cache: dict[str, SpecDescriptor] = {}

    def resolve(control_id: str) -> SpecDescriptor:
        if control_id not in cache:
            spec = build_spec_descriptor(neo4j_session, control_id)
            if spec is None:
                raise KeyError(f"no FulfilmentSpec for {control_id!r}")
            cache[control_id] = spec
        return cache[control_id]

    return resolve
