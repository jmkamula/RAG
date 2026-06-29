"""
ArionComply — Load Event nodes to Neo4j

Safe to re-run — uses MERGE.

Usage:
    python3 enrichment/events/load_to_neo4j.py --dry-run
    python3 enrichment/events/load_to_neo4j.py --verify
"""
from __future__ import annotations
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from enrichment.events.event_nodes import ALL_EVENTS


def load(uri: str, user: str, password: str, dry_run: bool = False) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    total_events       = 0
    total_triggers     = 0
    total_doc_rels     = 0
    # S2b meta-cascade counters
    total_emits        = 0
    total_followups    = 0
    total_fact_updates = 0
    total_expands      = 0
    total_cascades     = 0
    missing            = []

    with driver.session() as s:
        # ── Pre-pass: MERGE every Event node first so that meta-cascade
        # edges (EMITS_EVENT, EXPECTS_FOLLOWUP_EVENT) can reference any
        # target regardless of authoring order in ALL_EVENTS.
        if not dry_run:
            for event in ALL_EVENTS:
                s.run("MERGE (e:Event {id: $id})", id=event.id).consume()

        for event in ALL_EVENTS:

            if dry_run:
                print(f"\n[DRY RUN] Event: {event.id}")
                print(f"  category:  {event.category}")
                print(f"  deadline:  {event.legal_deadline or 'none'}")
                print(f"  severity:  {event.severity_default}")
                print(f"  triggers:  {len(event.triggers)}")
                for t in event.triggers:
                    print(f"    → {t.control_id}" +
                          (f" [{t.deadline}]" if t.deadline else ""))
                if event.requires_evidence:
                    print(f"  documents: {event.requires_evidence}")
                continue

            # ── MERGE Event node ──────────────────────────────────────────
            s.run("""
                MERGE (e:Event {id: $id})
                SET e.event_type       = $event_type,
                    e.category         = $category,
                    e.title            = $title,
                    e.description      = $description,
                    e.legal_deadline   = $legal_deadline,
                    e.severity_default = $severity_default,
                    e.updated_at       = datetime()
                RETURN e.id
            """,
                id               = event.id,
                event_type       = event.event_type,
                category         = event.category,
                title            = event.title,
                description      = event.description,
                legal_deadline   = event.legal_deadline or "",
                severity_default = event.severity_default,
            ).consume()
            total_events += 1

            # ── MERGE TRIGGERS_OBLIGATION relationships ────────────────────
            for trigger in event.triggers:
                exists = s.run(
                    "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                    id=trigger.control_id
                ).single()

                if not exists:
                    missing.append((event.event_type, trigger.control_id))
                    continue

                s.run("""
                    MATCH (e:Event {id: $event_id})
                    MATCH (n:RequirementNode {id: $control_id})
                    MERGE (e)-[r:TRIGGERS_OBLIGATION]->(n)
                    SET r.deadline  = $deadline,
                        r.rationale = $rationale,
                        r.mandatory = true
                """,
                    event_id   = event.id,
                    control_id = trigger.control_id,
                    deadline   = trigger.deadline or "",
                    rationale  = trigger.rationale,
                ).consume()
                total_triggers += 1

            # ── MERGE REQUIRES_EVIDENCE relationships ─────────────────────
            for doc_req_id in event.requires_evidence:
                exists = s.run(
                    "MATCH (r:EvidenceRequirement {id: $id}) RETURN r.id",
                    id=doc_req_id
                ).single()

                if not exists:
                    missing.append((event.event_type, doc_req_id))
                    continue

                s.run("""
                    MATCH (e:Event {id: $event_id})
                    MATCH (r:EvidenceRequirement {id: $doc_req_id})
                    MERGE (e)-[:REQUIRES_EVIDENCE]->(r)
                """,
                    event_id   = event.id,
                    doc_req_id = doc_req_id,
                ).consume()
                total_doc_rels += 1

            # ── S2b: meta-cascade edges from the meditation patterns ─────
            # Each field on Event is optional; loops are no-ops when empty.

            # EMITS_EVENT — event → event (P1: cross-domain handoff)
            for em in event.emits_events:
                tgt = s.run(
                    "MATCH (n:Event {id: $id}) RETURN n.id",
                    id=em.target_event_id
                ).single()
                if not tgt:
                    missing.append((event.event_type, em.target_event_id))
                    continue
                s.run("""
                    MATCH (a:Event {id: $src})
                    MATCH (b:Event {id: $tgt})
                    MERGE (a)-[r:EMITS_EVENT]->(b)
                    SET r.rationale    = $rationale,
                        r.applies_when = coalesce($applies_when, ''),
                        r.updated_at   = datetime()
                """, src=event.id, tgt=em.target_event_id,
                     rationale=em.rationale, applies_when=em.applies_when).consume()
                total_emits += 1

            # EXPECTS_FOLLOWUP_EVENT — event → event with window (P2)
            for ef in event.expects_followups:
                tgt = s.run(
                    "MATCH (n:Event {id: $id}) RETURN n.id",
                    id=ef.target_event_id
                ).single()
                if not tgt:
                    missing.append((event.event_type, ef.target_event_id))
                    continue
                s.run("""
                    MATCH (a:Event {id: $src})
                    MATCH (b:Event {id: $tgt})
                    MERGE (a)-[r:EXPECTS_FOLLOWUP_EVENT]->(b)
                    SET r.window_days = $window_days,
                        r.rationale   = $rationale,
                        r.updated_at  = datetime()
                """, src=event.id, tgt=ef.target_event_id,
                     window_days=ef.window_days, rationale=ef.rationale).consume()
                total_followups += 1

            # UPDATES_FACT — event → ClientFact (P3)
            for uf in event.updates_facts:
                tgt = s.run(
                    "MATCH (n:ClientFact {id: $id}) RETURN n.id",
                    id=uf.fact_id
                ).single()
                if not tgt:
                    missing.append((event.event_type, uf.fact_id))
                    continue
                s.run("""
                    MATCH (a:Event {id: $src})
                    MATCH (b:ClientFact {id: $tgt})
                    MERGE (a)-[r:UPDATES_FACT {operation: $op}]->(b)
                    SET r.rationale  = $rationale,
                        r.updated_at = datetime()
                """, src=event.id, tgt=uf.fact_id,
                     op=uf.operation, rationale=uf.rationale).consume()
                total_fact_updates += 1

            # EXPANDS_SCOPE — event → RequirementNode (P4) with scope_kind
            for es in event.expands_scope:
                for control_id in es.control_set:
                    tgt = s.run(
                        "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                        id=control_id
                    ).single()
                    if not tgt:
                        missing.append((event.event_type, control_id))
                        continue
                    s.run("""
                        MATCH (a:Event {id: $src})
                        MATCH (b:RequirementNode {id: $tgt})
                        MERGE (a)-[r:EXPANDS_SCOPE {scope_kind: $kind}]->(b)
                        SET r.rationale  = $rationale,
                            r.updated_at = datetime()
                    """, src=event.id, tgt=control_id,
                         kind=es.scope_kind, rationale=es.rationale).consume()
                    total_expands += 1

            # CASCADES_REVIEW — event → RequirementNode (re-evaluate)
            for control_id in event.cascades_review:
                tgt = s.run(
                    "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                    id=control_id
                ).single()
                if not tgt:
                    missing.append((event.event_type, control_id))
                    continue
                s.run("""
                    MATCH (a:Event {id: $src})
                    MATCH (b:RequirementNode {id: $tgt})
                    MERGE (a)-[r:CASCADES_REVIEW]->(b)
                    SET r.updated_at = datetime()
                """, src=event.id, tgt=control_id).consume()
                total_cascades += 1

            # Per-event progress line
            meta_summary = ""
            meta_counts = (
                len(event.emits_events), len(event.expects_followups),
                len(event.updates_facts),
                sum(len(es.control_set) for es in event.expands_scope),
                len(event.cascades_review),
            )
            if any(meta_counts):
                meta_summary = (f"  meta=[em:{meta_counts[0]} fu:{meta_counts[1]} "
                                f"uf:{meta_counts[2]} es:{meta_counts[3]} "
                                f"cr:{meta_counts[4]}]")
            print(f"  ✓ {event.event_type:40s} "
                  f"{len(event.triggers)} triggers  "
                  f"{len(event.requires_evidence)} docs{meta_summary}")

    driver.close()

    print(f"\n{'─'*55}")
    if dry_run:
        print("[DRY RUN] No changes written to Neo4j")
    else:
        print(f"✓ Event nodes:              {total_events}")
        print(f"✓ TRIGGERS_OBLIGATION rels: {total_triggers}")
        print(f"✓ REQUIRES_EVIDENCE rels:   {total_doc_rels}")
        print(f"✓ EMITS_EVENT rels:         {total_emits}")
        print(f"✓ EXPECTS_FOLLOWUP rels:    {total_followups}")
        print(f"✓ UPDATES_FACT rels:        {total_fact_updates}")
        print(f"✓ EXPANDS_SCOPE rels:       {total_expands}")
        print(f"✓ CASCADES_REVIEW rels:     {total_cascades}")

    if missing:
        print(f"\n⚠ {len(missing)} nodes not found:")
        for event_type, node_id in missing:
            print(f"  {node_id} (event: {event_type})")


def verify(uri: str, user: str, password: str) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as s:
        stats = s.run("""
            MATCH (e:Event) WITH count(e) AS events
            MATCH ()-[t:TRIGGERS_OBLIGATION]->() WITH events, count(t) AS trigs
            MATCH (e2:Event)-[:REQUIRES_EVIDENCE]->() WITH events, trigs, count(e2) AS doc_rels
            RETURN events, trigs, doc_rels
        """).single()

        print(f"\nNeo4j verification:")
        print(f"  Event nodes:              {stats['events']}")
        print(f"  TRIGGERS_OBLIGATION rels: {stats['trigs']}")
        print(f"  Event REQUIRES_EVIDENCE:  {stats['doc_rels']}")

        # S2b meta-cascade edges
        for et in ('EMITS_EVENT', 'EXPECTS_FOLLOWUP_EVENT',
                   'UPDATES_FACT', 'EXPANDS_SCOPE', 'CASCADES_REVIEW'):
            c = s.run(f"MATCH ()-[r:`{et}`]->() RETURN count(r) AS c").single()['c']
            print(f"  {et:24s}: {c}")

        by_cat = s.run("""
            MATCH (e:Event)
            RETURN e.category AS cat, count(e) AS cnt
            ORDER BY cnt DESC
        """)
        print(f"\n  By category:")
        for r in by_cat:
            print(f"    {r['cat']:10s}: {r['cnt']}")

        # Test full chain — event → obligations → document requirements
        chain = s.run("""
            MATCH (e:Event {event_type: 'personal_data_breach'})
                  -[:TRIGGERS_OBLIGATION]->(n:RequirementNode)
            RETURN e.title AS event, collect(n.ref) AS controls
        """).single()
        if chain:
            print(f"\n  Chain test — {chain['event']}:")
            print(f"    Triggers: {sorted(chain['controls'])}")

    driver.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load Event nodes to Neo4j"
    )
    parser.add_argument("--dry-run",        action="store_true")
    parser.add_argument("--verify",         action="store_true")
    parser.add_argument("--neo4j-uri",      default="bolt://127.0.0.1:7687")
    parser.add_argument("--neo4j-user",     default="neo4j")
    parser.add_argument("--neo4j-password", default=None)
    args = parser.parse_args()

    password = args.neo4j_password or os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")
    print(f"Neo4j:    {args.neo4j_uri}")
    print(f"Dry run:  {args.dry_run}")
    print(f"Events:   {len(ALL_EVENTS)}")

    load(args.neo4j_uri, args.neo4j_user, password, args.dry_run)

    if args.verify and not args.dry_run:
        verify(args.neo4j_uri, args.neo4j_user, password)


if __name__ == "__main__":
    main()
