"""
ArionComply — Load EvidenceRequirement and ChecklistItem nodes to Neo4j

Writes the four-layer model per control:
  RequirementNode -[:SATISFIED_BY]-> FulfilmentSpec
                                       -[:REQUIRES_EVIDENCE]-> EvidenceRequirement
                                                                 -[:MUST_CONTAIN|SHOULD_CONTAIN]-> ChecklistItem

Safe to re-run — uses MERGE everywhere. Sets curation_status='curated' on
specs it touches (since they're being populated with leaves here).

Usage:
    python3 enrichment/documents/load_to_neo4j.py --dry-run
    python3 enrichment/documents/load_to_neo4j.py --verify
"""
from __future__ import annotations
import argparse
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from enrichment.documents.document_requirements import (
    ALL_DERIVED_SPECS,
    ALL_EVIDENCE_REQUIREMENTS,
    DerivedSpec,
    EvidenceRequirement,
)


def _prune_leaf_orphans(session, req: "EvidenceRequirement", dry_run: bool) -> tuple[int, int]:
    """Drop MUST_CONTAIN / SHOULD_CONTAIN edges from this leaf to ChecklistItems
    not present in the code-defined must / should lists. Makes the loader
    declarative: post-load Neo4j edges for this leaf equal exactly what code says.

    Returns (must_edges_dropped, should_edges_dropped). In dry_run mode,
    counts what would be dropped but performs no writes.

    See [[loader-orphan-cleanup-followup]] for the rationale — single→multi-leaf
    promotion reuses leaf ids while rewriting item lists, and MERGE-only loads
    leave stale edges behind that the leaf evaluator then counts against the
    new spec. An item that legitimately moves between leaves keeps its new-leaf
    edge because this prune is scoped to the current leaf only.
    """
    code_must_ids   = [ci.id for ci in req.must_contain]
    code_should_ids = [ci.id for ci in req.should_contain]

    if dry_run:
        n_must = session.run("""
            MATCH (er:EvidenceRequirement {id: $req_id})-[rel:MUST_CONTAIN]->(i:ChecklistItem)
            WHERE NOT i.id IN $keep
            RETURN count(rel) AS n
        """, req_id=req.id, keep=code_must_ids).single()["n"]
        n_should = session.run("""
            MATCH (er:EvidenceRequirement {id: $req_id})-[rel:SHOULD_CONTAIN]->(i:ChecklistItem)
            WHERE NOT i.id IN $keep
            RETURN count(rel) AS n
        """, req_id=req.id, keep=code_should_ids).single()["n"]
        return n_must, n_should

    must_summary = session.run("""
        MATCH (er:EvidenceRequirement {id: $req_id})-[rel:MUST_CONTAIN]->(i:ChecklistItem)
        WHERE NOT i.id IN $keep
        DELETE rel
    """, req_id=req.id, keep=code_must_ids).consume()
    should_summary = session.run("""
        MATCH (er:EvidenceRequirement {id: $req_id})-[rel:SHOULD_CONTAIN]->(i:ChecklistItem)
        WHERE NOT i.id IN $keep
        DELETE rel
    """, req_id=req.id, keep=code_should_ids).consume()
    return (
        must_summary.counters.relationships_deleted,
        should_summary.counters.relationships_deleted,
    )


def _delete_orphan_items(session, dry_run: bool) -> int:
    """Delete ChecklistItem nodes that have no remaining MUST_CONTAIN or
    SHOULD_CONTAIN edges from any EvidenceRequirement. Run once after every
    leaf has been processed and pruned — at that point any item left without
    edges is genuinely abandoned, not transiently mid-load.

    DETACH DELETE removes any incidental edges (e.g. DERIVED_FROM →
    RequirementNode) on the same node.

    Returns the number of nodes deleted.
    """
    if dry_run:
        return session.run("""
            MATCH (i:ChecklistItem)
            WHERE NOT EXISTS { MATCH (:EvidenceRequirement)-[:MUST_CONTAIN|SHOULD_CONTAIN]->(i) }
            RETURN count(i) AS n
        """).single()["n"]
    summary = session.run("""
        MATCH (i:ChecklistItem)
        WHERE NOT EXISTS { MATCH (:EvidenceRequirement)-[:MUST_CONTAIN|SHOULD_CONTAIN]->(i) }
        DETACH DELETE i
    """).consume()
    return summary.counters.nodes_deleted


def _delete_orphan_ers(session, valid_ids: set, dry_run: bool) -> int:
    """Delete EvidenceRequirement nodes whose id is not in the current
    loader's valid set. Surfaces when a leaf's id field is renamed during
    a promotion (e.g. single-leaf REQ_X.id 'req:A.8.24:encryption_policy'
    → multi-leaf REQ_X824_POLICY.id 'req:A.8.24:cryptography_policy').

    The valid set must include BOTH ALL_EVIDENCE_REQUIREMENTS ids AND each
    DerivedSpec's direct_evidence ids — the loader writes both to Neo4j,
    so both must be honoured here.

    Run BEFORE _delete_orphan_items so newly-orphaned ChecklistItems
    (whose only parent ER was the orphan being deleted) get swept up by
    the next pass.

    Returns the number of EvidenceRequirement nodes deleted.
    """
    if dry_run:
        return session.run("""
            MATCH (r:EvidenceRequirement)
            WHERE NOT r.id IN $valid_ids
            RETURN count(r) AS n
        """, valid_ids=list(valid_ids)).single()["n"]
    summary = session.run("""
        MATCH (r:EvidenceRequirement)
        WHERE NOT r.id IN $valid_ids
        DETACH DELETE r
    """, valid_ids=list(valid_ids)).consume()
    return summary.counters.nodes_deleted


def load(uri: str, user: str, password: str, dry_run: bool = False) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Pre-flight: a control must be curated either via EvidenceRequirement(s)
    # OR via a DerivedSpec, not both. Conflicting curation gives the loader
    # contradictory views of the same FulfilmentSpec's op / applies_when.
    ev_controls = {(r.standard_id, r.control_ref) for r in ALL_EVIDENCE_REQUIREMENTS}
    derived_controls = {(d.standard_id, d.control_ref) for d in ALL_DERIVED_SPECS}
    overlap = ev_controls & derived_controls
    if overlap:
        print(f"\n✗ ERROR: {len(overlap)} control(s) have BOTH EvidenceRequirement and DerivedSpec curation:")
        for std, ctrl in sorted(overlap):
            print(f"    {std}:{ctrl}")
        print("Choose one curation shape per control. Aborting load.")
        driver.close()
        return

    total_reqs = 0
    total_items = 0
    total_rels = 0
    total_specs = 0
    total_derived_specs = 0
    total_derives_from = 0
    pruned_must_edges = 0
    pruned_should_edges = 0
    pruned_items = 0
    missing_controls = []

    with driver.session() as s:

        for req in ALL_EVIDENCE_REQUIREMENTS:

            # ── Check RequirementNode exists ──────────────────────────────
            standard_id = req.standard_id
            node_id     = f"{standard_id}:{req.control_ref}"
            exists = s.run(
                "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                id=node_id
            ).single()

            if not exists:
                missing_controls.append(node_id)
                print(f"  ⚠ {node_id} — RequirementNode not found, skipping")
                continue

            # ── MERGE EvidenceRequirement node ────────────────────────────
            if dry_run:
                print(f"\n[DRY RUN] EvidenceRequirement: {req.id}")
                print(f"  trigger: {req.trigger_type}")
                fresh_tag = f"{req.freshness_days} days" if req.freshness_days else "no freshness req"
                print(f"  freshness: {fresh_tag}")
                print(f"  must_contain: {len(req.must_contain)} items")
                print(f"  should_contain: {len(req.should_contain)} items")
            else:
                s.run("""
                    MERGE (r:EvidenceRequirement {id: $id})
                    SET r.control_ref    = $control_ref,
                        r.standard_id    = $standard_id,
                        r.evidence_type  = $evidence_type,
                        r.title          = $title,
                        r.trigger_type   = $trigger_type,
                        r.description    = $description,
                        r.freshness_days = $freshness_days,
                        r.updated_at     = datetime()
                    REMOVE r.trigger_event
                    RETURN r.id
                """,
                    id             = req.id,
                    control_ref    = req.control_ref,
                    standard_id    = req.standard_id,
                    evidence_type  = req.evidence_type,
                    title          = req.title,
                    trigger_type   = req.trigger_type,
                    description    = req.description,
                    freshness_days = req.freshness_days,
                ).consume()
                total_reqs += 1

            # ── MERGE FulfilmentSpec for this control (idempotent) ────────
            # Spec id is deterministic: 'spec:' + RequirementNode id.
            # If the migration has run, the spec already exists with
            # curation_status='uncurated' for non-curated controls; touching
            # it here promotes it to 'curated' since we're attaching leaves.
            if not dry_run:
                s.run("""
                    MATCH (n:RequirementNode {id: $node_id})
                    MERGE (fs:FulfilmentSpec {id: 'spec:' + n.id})
                      ON CREATE SET
                          fs.op              = 'ALL',
                          fs.applies_when    = NULL,
                          fs.curation_status = 'curated',
                          fs.updated_at      = datetime()
                      ON MATCH SET
                          fs.curation_status = 'curated',
                          fs.updated_at      = datetime()
                    MERGE (n)-[:SATISFIED_BY]->(fs)
                """, node_id=node_id).consume()
                total_specs += 1

            # ── MERGE REQUIRES_EVIDENCE relationship (spec → leaf) ────────
            if not dry_run:
                s.run("""
                    MATCH (n:RequirementNode {id: $node_id})-[:SATISFIED_BY]->(fs:FulfilmentSpec)
                    MATCH (r:EvidenceRequirement {id: $req_id})
                    MERGE (fs)-[edge:REQUIRES_EVIDENCE]->(r)
                      ON CREATE SET edge.role = $role
                """,
                    node_id = node_id,
                    req_id  = req.id,
                    role    = req.evidence_type,
                ).consume()
                total_rels += 1

            # ── MERGE ChecklistItems ──────────────────────────────────────
            all_items = [
                (item, "must")
                for item in req.must_contain
            ] + [
                (item, "should")
                for item in req.should_contain
            ]

            for item, category in all_items:
                if dry_run:
                    gdpr_tag = " [GDPR]" if item.gdpr_aligned else ""
                    print(f"    [{category}] {item.text}{gdpr_tag}")
                else:
                    s.run("""
                        MERGE (i:ChecklistItem {id: $id})
                        SET i.text         = $text,
                            i.category     = $category,
                            i.gdpr_aligned = $gdpr_aligned,
                            i.rationale    = $rationale,
                            i.control_ref  = $control_ref,
                            i.updated_at   = datetime()
                        RETURN i.id
                    """,
                        id           = item.id,
                        text         = item.text,
                        category     = category,
                        gdpr_aligned = item.gdpr_aligned,
                        rationale    = item.rationale,
                        control_ref  = req.control_ref,
                    ).consume()

                    # Link to EvidenceRequirement
                    rel_type = "MUST_CONTAIN" if category == "must" else "SHOULD_CONTAIN"
                    s.run(f"""
                        MATCH (r:EvidenceRequirement {{id: $req_id}})
                        MATCH (i:ChecklistItem {{id: $item_id}})
                        MERGE (r)-[:{rel_type}]->(i)
                    """, req_id=req.id, item_id=item.id).consume()

                    # Link back to RequirementNode for traceability
                    s.run("""
                        MATCH (n:RequirementNode {id: $node_id})
                        MATCH (i:ChecklistItem {id: $item_id})
                        MERGE (i)-[:DERIVED_FROM]->(n)
                    """, node_id=node_id, item_id=item.id).consume()

                    total_items += 1

            # ── Prune stale edges from prior loads (declarative idempotency) ──
            m_dropped, s_dropped = _prune_leaf_orphans(s, req, dry_run)
            pruned_must_edges   += m_dropped
            pruned_should_edges += s_dropped

            if not dry_run:
                prune_tag = (
                    f"  (pruned {m_dropped}M+{s_dropped}S stale edges)"
                    if (m_dropped or s_dropped) else ""
                )
                print(f"  ✓ {req.control_ref:12s} {req.trigger_type:15s} "
                      f"{len(req.must_contain)}M + {len(req.should_contain)}S items  "
                      f"{req.title}{prune_tag}")

        # ── Derived specs (cross-control derivation) ──────────────────────
        for ds in ALL_DERIVED_SPECS:
            node_id = f"{ds.standard_id}:{ds.control_ref}"

            exists = s.run(
                "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                id=node_id
            ).single()
            if not exists:
                missing_controls.append(node_id)
                print(f"  ⚠ {node_id} — RequirementNode not found (derived), skipping")
                continue

            if dry_run:
                print(f"\n[DRY RUN] DerivedSpec: {ds.spec_id}")
                print(f"  op: {ds.op}{f' n={ds.n}' if ds.n else ''}")
                print(f"  applies_when: {ds.applies_when!r}")
                print(f"  derives_from: {len(ds.derives_from)} edges")
                for df in ds.derives_from:
                    scope = f" scope_items={df.scope_items}" if df.scope_items else ""
                    print(f"    → {df.target_standard_id}:{df.target_control_ref}  role={df.role}{scope}")
                print(f"  direct_evidence: {len(ds.direct_evidence)} leaves")
                continue

            # MERGE the FulfilmentSpec with DerivedSpec's op / applies_when
            s.run("""
                MATCH (n:RequirementNode {id: $node_id})
                MERGE (fs:FulfilmentSpec {id: 'spec:' + n.id})
                  ON CREATE SET
                      fs.op              = $op,
                      fs.n               = $n,
                      fs.applies_when    = $applies_when,
                      fs.curation_status = 'curated',
                      fs.updated_at      = datetime()
                  ON MATCH SET
                      fs.op              = $op,
                      fs.n               = $n,
                      fs.applies_when    = $applies_when,
                      fs.curation_status = 'curated',
                      fs.updated_at      = datetime()
                MERGE (n)-[:SATISFIED_BY]->(fs)
            """,
                node_id      = node_id,
                op           = ds.op,
                n            = ds.n,
                applies_when = ds.applies_when,
            ).consume()
            total_derived_specs += 1

            # Emit DERIVES_FROM edges to target controls
            for df in ds.derives_from:
                target_id = f"{df.target_standard_id}:{df.target_control_ref}"
                target_exists = s.run(
                    "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                    id=target_id
                ).single()
                if not target_exists:
                    print(f"  ⚠ {node_id} → DERIVES_FROM target {target_id} missing, skipping edge")
                    continue
                s.run("""
                    MATCH (n:RequirementNode {id: $node_id})-[:SATISFIED_BY]->(fs:FulfilmentSpec)
                    MATCH (target:RequirementNode {id: $target_id})
                    MERGE (fs)-[edge:DERIVES_FROM {role: $role}]->(target)
                      ON CREATE SET
                          edge.applies_when = $applies_when,
                          edge.title        = $title,
                          edge.scope_items  = $scope_items
                      ON MATCH SET
                          edge.applies_when = $applies_when,
                          edge.title        = $title,
                          edge.scope_items  = $scope_items
                """,
                    node_id      = node_id,
                    target_id    = target_id,
                    role         = df.role,
                    applies_when = df.applies_when,
                    title        = df.title,
                    scope_items  = df.scope_items,
                ).consume()
                total_derives_from += 1

            # Direct evidence — same shape as regular EvidenceRequirement
            for req in ds.direct_evidence:
                s.run("""
                    MERGE (r:EvidenceRequirement {id: $id})
                    SET r.control_ref    = $control_ref,
                        r.standard_id    = $standard_id,
                        r.evidence_type  = $evidence_type,
                        r.title          = $title,
                        r.trigger_type   = $trigger_type,
                        r.description    = $description,
                        r.freshness_days = $freshness_days,
                        r.updated_at     = datetime()
                    REMOVE r.trigger_event
                """,
                    id             = req.id,
                    control_ref    = req.control_ref,
                    standard_id    = req.standard_id,
                    evidence_type  = req.evidence_type,
                    title          = req.title,
                    trigger_type   = req.trigger_type,
                    description    = req.description,
                    freshness_days = req.freshness_days,
                ).consume()
                total_reqs += 1

                s.run("""
                    MATCH (n:RequirementNode {id: $node_id})-[:SATISFIED_BY]->(fs:FulfilmentSpec)
                    MATCH (r:EvidenceRequirement {id: $req_id})
                    MERGE (fs)-[edge:REQUIRES_EVIDENCE]->(r)
                      ON CREATE SET edge.role = $role
                """,
                    node_id = node_id,
                    req_id  = req.id,
                    role    = req.evidence_type,
                ).consume()
                total_rels += 1

                # ChecklistItems for the direct evidence
                all_items = [(it, "must") for it in req.must_contain] + \
                            [(it, "should") for it in req.should_contain]
                for item, category in all_items:
                    s.run("""
                        MERGE (i:ChecklistItem {id: $id})
                        SET i.text         = $text,
                            i.category     = $category,
                            i.gdpr_aligned = $gdpr_aligned,
                            i.rationale    = $rationale,
                            i.control_ref  = $control_ref,
                            i.updated_at   = datetime()
                    """,
                        id           = item.id,
                        text         = item.text,
                        category     = category,
                        gdpr_aligned = item.gdpr_aligned,
                        rationale    = item.rationale,
                        control_ref  = req.control_ref,
                    ).consume()
                    rel_type = "MUST_CONTAIN" if category == "must" else "SHOULD_CONTAIN"
                    s.run(f"""
                        MATCH (r:EvidenceRequirement {{id: $req_id}})
                        MATCH (i:ChecklistItem {{id: $item_id}})
                        MERGE (r)-[:{rel_type}]->(i)
                    """, req_id=req.id, item_id=item.id).consume()
                    s.run("""
                        MATCH (n:RequirementNode {id: $node_id})
                        MATCH (i:ChecklistItem {id: $item_id})
                        MERGE (i)-[:DERIVED_FROM]->(n)
                    """, node_id=node_id, item_id=item.id).consume()
                    total_items += 1

                # Prune stale edges on this direct-evidence leaf too
                m_dropped, s_dropped = _prune_leaf_orphans(s, req, dry_run)
                pruned_must_edges   += m_dropped
                pruned_should_edges += s_dropped

            print(f"  ✓ {ds.control_ref:12s} {'derived':15s} "
                  f"{len(ds.derives_from)} deps + {len(ds.direct_evidence)} direct  "
                  f"{ds.title}")

        # ── Final sweep: delete orphan EvidenceRequirements first, then items ──
        # ER orphans surface when leaf ids are renamed during promotions.
        # See [[loader-er-orphan-cleanup-followup]] for the design rationale.
        valid_ev_ids = {r.id for r in ALL_EVIDENCE_REQUIREMENTS} \
                     | {req.id for ds in ALL_DERIVED_SPECS for req in ds.direct_evidence}
        pruned_ers   = _delete_orphan_ers(s, valid_ev_ids, dry_run)
        pruned_items = _delete_orphan_items(s, dry_run)

    driver.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'─'*55}")
    if dry_run:
        print("[DRY RUN] No changes written to Neo4j")
        if pruned_must_edges or pruned_should_edges or pruned_items or pruned_ers:
            print(f"[DRY RUN] Would prune: "
                  f"{pruned_must_edges} MUST_CONTAIN + "
                  f"{pruned_should_edges} SHOULD_CONTAIN edges, "
                  f"{pruned_ers} orphan EvidenceRequirements, "
                  f"{pruned_items} orphan ChecklistItems")
    else:
        print(f"✓ EvidenceRequirement nodes:    {total_reqs}")
        print(f"✓ FulfilmentSpec MERGE calls:   {total_specs}")
        print(f"✓ ChecklistItem nodes:          {total_items}")
        print(f"✓ REQUIRES_EVIDENCE rels:       {total_rels}")
        print(f"✓ DerivedSpec MERGE calls:      {total_derived_specs}")
        print(f"✓ DERIVES_FROM rels:            {total_derives_from}")
        if pruned_must_edges or pruned_should_edges or pruned_items or pruned_ers:
            print(f"✓ Pruned stale edges:           "
                  f"{pruned_must_edges} MUST + {pruned_should_edges} SHOULD")
            print(f"✓ Pruned orphan ERs:            {pruned_ers}")
            print(f"✓ Pruned orphan items:          {pruned_items}")
        else:
            print(f"✓ Pruned stale edges:           0  (clean state)")

    if missing_controls:
        print(f"\n⚠ {len(missing_controls)} controls not found in Neo4j:")
        for c in missing_controls:
            print(f"  {c}")


def verify(uri: str, user: str, password: str) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as s:
        stats = s.run("""
            MATCH (r:EvidenceRequirement) WITH count(r) AS reqs
            MATCH (i:ChecklistItem)       WITH reqs, count(i) AS items
            OPTIONAL MATCH ()-[r1:REQUIRES_EVIDENCE]->() WITH reqs, items, count(r1) AS req_rels
            OPTIONAL MATCH ()-[r2:SATISFIED_BY]->()      WITH reqs, items, req_rels, count(r2) AS sat_rels
            OPTIONAL MATCH ()-[r3:MUST_CONTAIN]->()      WITH reqs, items, req_rels, sat_rels, count(r3) AS must_rels
            OPTIONAL MATCH ()-[r4:SHOULD_CONTAIN]->()    WITH reqs, items, req_rels, sat_rels, must_rels, count(r4) AS should_rels
            OPTIONAL MATCH ()-[r5:DERIVES_FROM]->()      WITH reqs, items, req_rels, sat_rels, must_rels, should_rels, count(r5) AS derives_rels
            RETURN reqs, items, req_rels, sat_rels, must_rels, should_rels, derives_rels
        """).single()

        print(f"\nNeo4j verification:")
        print(f"  EvidenceRequirement nodes: {stats['reqs']}")
        print(f"  ChecklistItem nodes:       {stats['items']}")
        print(f"  REQUIRES_EVIDENCE rels:    {stats['req_rels']}")
        print(f"  SATISFIED_BY rels:         {stats['sat_rels']}")
        print(f"  MUST_CONTAIN rels:         {stats['must_rels']}")
        print(f"  SHOULD_CONTAIN rels:       {stats['should_rels']}")
        print(f"  DERIVES_FROM rels:         {stats['derives_rels']}")

        # Check trigger type distribution
        by_trigger = s.run("""
            MATCH (r:EvidenceRequirement)
            RETURN r.trigger_type AS trigger, count(r) AS cnt
            ORDER BY cnt DESC
        """)
        print(f"\n  By trigger type:")
        for row in by_trigger:
            print(f"    {row['trigger']:15s}: {row['cnt']}")

        # Check GDPR-aligned items
        gdpr = s.run("""
            MATCH (i:ChecklistItem {gdpr_aligned: true})
            RETURN count(i) AS cnt
        """).single()
        print(f"\n  GDPR-aligned checklist items: {gdpr['cnt']}")

    driver.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load EvidenceRequirement and ChecklistItem nodes to Neo4j"
    )
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--verify",   action="store_true")
    parser.add_argument("--neo4j-uri",      default="bolt://127.0.0.1:7687")
    parser.add_argument("--neo4j-user",     default="neo4j")
    parser.add_argument("--neo4j-password", default=None)
    args = parser.parse_args()

    password = args.neo4j_password or os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")

    print(f"Neo4j: {args.neo4j_uri}")
    print(f"Dry run: {args.dry_run}")
    print(f"Requirements: {len(ALL_EVIDENCE_REQUIREMENTS)}")

    load(args.neo4j_uri, args.neo4j_user, password, args.dry_run)

    if args.verify and not args.dry_run:
        verify(args.neo4j_uri, args.neo4j_user, password)


if __name__ == "__main__":
    main()
