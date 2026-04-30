"""
ArionComply — Load ClientFact and ObligationRule nodes to Neo4j

Creates the obligation implication graph in Neo4j.
Safe to re-run — uses MERGE so existing nodes are not duplicated.

Usage:
    python3 enrichment/obligations/load_to_neo4j.py --dry-run
    python3 enrichment/obligations/load_to_neo4j.py
"""
from __future__ import annotations

import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from enrichment.obligations.client_facts import ClientFacts
from enrichment.obligations.obligation_rules import ALL_RULES, get_implied_controls


def load_to_neo4j(
    uri:      str,
    user:     str,
    password: str,
    dry_run:  bool = False,
) -> None:
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:

        # ── Step 1: Create ObligationRule nodes ───────────────────────────
        print(f"\nLoading {len(ALL_RULES)} ObligationRule nodes...")
        for rule in ALL_RULES:
            cypher = """
            MERGE (r:ObligationRule {id: $id})
            SET r.description  = $description,
                r.rationale    = $rationale,
                r.trigger_type = $trigger_type,
                r.control_count = $control_count,
                r.updated_at   = datetime()
            RETURN r.id
            """
            params = {
                "id":            rule.id,
                "description":   rule.description,
                "rationale":     rule.rationale,
                "trigger_type":  rule.trigger_type,
                "control_count": len(rule.mandatory_controls),
            }
            if dry_run:
                print(f"  [DRY RUN] MERGE ObligationRule {rule.id} "
                      f"({len(rule.mandatory_controls)} controls)")
            else:
                result = session.run(cypher, **params)
                result.consume()
                print(f"  ✓ {rule.id} ({len(rule.mandatory_controls)} controls)")

        # ── Step 2: Create REQUIRES_CONTROL relationships ─────────────────
        print(f"\nLoading REQUIRES_CONTROL relationships...")
        total_rels = 0
        missing    = []

        for rule in ALL_RULES:
            for control_id in rule.mandatory_controls:

                # Check the RequirementNode exists
                check = session.run(
                    "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                    id=control_id
                ).single()

                if not check:
                    missing.append((rule.id, control_id))
                    if dry_run:
                        print(f"  [MISSING] {control_id} (rule: {rule.id})")
                    continue

                cypher = """
                MATCH (r:ObligationRule {id: $rule_id})
                MATCH (n:RequirementNode {id: $control_id})
                MERGE (r)-[rel:REQUIRES_CONTROL]->(n)
                SET rel.mandatory    = true,
                    rel.rationale    = $rationale,
                    rel.trigger_type = $trigger_type,
                    rel.updated_at   = datetime()
                RETURN rel
                """
                params = {
                    "rule_id":      rule.id,
                    "control_id":   control_id,
                    "rationale":    rule.rationale,
                    "trigger_type": rule.trigger_type,
                }
                if dry_run:
                    print(f"  [DRY RUN] {rule.id} -[:REQUIRES_CONTROL]-> {control_id}")
                else:
                    result = session.run(cypher, **params)
                    result.consume()
                    total_rels += 1

        # ── Step 3: Create ClientFact nodes ───────────────────────────────
        print(f"\nLoading ClientFact nodes...")
        facts_schema = {
            # Scope
            "processes_personal_data":    "Processes personal data",
            "eu_data_subjects":           "Has EU data subjects",
            "uk_data_subjects":           "Has UK data subjects",
            # Role
            "role_controller":            "Acts as data controller",
            "role_processor":             "Acts as data processor",
            "role_joint_controller":      "Acts as joint controller",
            # Data types
            "special_category_data":      "Processes special category data",
            "criminal_conviction_data":   "Processes criminal conviction data",
            "childrens_data":             "Processes children's personal data",
            # Processing
            "automated_decision_making":  "Performs automated decision making",
            "profiling":                  "Performs profiling",
            "large_scale_processing":     "Large scale processing",
            "systematic_monitoring":      "Systematic monitoring of individuals",
            "high_risk_processing":       "High risk processing activities",
            # Organisation
            "employee_count_250_plus":    "250 or more employees",
            "public_authority":           "Is a public authority",
            # Third parties
            "uses_processors":            "Uses third party data processors",
            "uses_cloud_services":        "Uses cloud services for data processing",
            "transfers_data_outside_eu":  "Transfers data outside EU/UK",
            # Technical
            "develops_software":          "Develops software",
            "has_remote_workers":         "Has remote workers",
            "has_physical_premises":      "Has physical premises",
        }

        for fact_name, description in facts_schema.items():
            cypher = """
            MERGE (f:ClientFact {id: $id})
            SET f.fact        = $fact,
                f.description = $description,
                f.updated_at  = datetime()
            RETURN f.id
            """
            params = {
                "id":          f"fact:{fact_name}",
                "fact":        fact_name,
                "description": description,
            }
            if dry_run:
                print(f"  [DRY RUN] MERGE ClientFact {fact_name}")
            else:
                result = session.run(cypher, **params)
                result.consume()
                print(f"  ✓ {fact_name}")

        # ── Step 4: Link facts to rules ───────────────────────────────────
        print(f"\nLinking ClientFacts to ObligationRules...")

        # Define which facts each rule depends on
        RULE_FACT_DEPENDENCIES = {
            "iso_universal":           ["certification_target"],
            "gdpr_universal":          ["processes_personal_data", "eu_data_subjects", "role_controller"],
            "privacy_notices":         ["role_controller", "eu_data_subjects"],
            "uses_processors":         ["role_controller", "uses_processors"],
            "uses_cloud_services":     ["uses_cloud_services", "processes_personal_data"],
            "is_processor":            ["role_processor"],
            "joint_controllers":       ["role_joint_controller"],
            "special_category_data":   ["special_category_data"],
            "criminal_conviction_data":["criminal_conviction_data"],
            "childrens_data":          ["childrens_data"],
            "automated_decision_making":["automated_decision_making", "profiling"],
            "dpo_required":            ["public_authority", "large_scale_processing", "systematic_monitoring"],
            "records_of_processing":   ["employee_count_250_plus", "high_risk_processing", "special_category_data"],
            "dpia_required":           ["high_risk_processing"],
            "international_transfers": ["transfers_data_outside_eu"],
            "software_development":    ["develops_software"],
            "remote_workers":          ["has_remote_workers"],
            "physical_premises":       ["has_physical_premises"],
        }

        for rule_id, fact_names in RULE_FACT_DEPENDENCIES.items():
            for fact_name in fact_names:
                fact_id = f"fact:{fact_name}"
                cypher = """
                MATCH (f:ClientFact {id: $fact_id})
                MATCH (r:ObligationRule {id: $rule_id})
                MERGE (f)-[:TRIGGERS]->(r)
                RETURN f.id, r.id
                """
                if dry_run:
                    print(f"  [DRY RUN] {fact_id} -[:TRIGGERS]-> {rule_id}")
                else:
                    result = session.run(cypher,
                                        fact_id=fact_id, rule_id=rule_id)
                    result.consume()

        # ── Summary ───────────────────────────────────────────────────────
        print(f"\n{'─'*50}")
        if dry_run:
            print("[DRY RUN] No changes written to Neo4j")
        else:
            print(f"✓ ObligationRule nodes: {len(ALL_RULES)}")
            print(f"✓ REQUIRES_CONTROL rels: {total_rels}")
            print(f"✓ ClientFact nodes:  {len(facts_schema)}")
            print(f"✓ TRIGGERS rels created")

        if missing:
            print(f"\n⚠ {len(missing)} controls not found in Neo4j:")
            for rule_id, control_id in missing:
                print(f"  {control_id} (rule: {rule_id})")
            print("  These controls may not be in the index yet.")
            print("  REQUIRES_CONTROL relationships were skipped for these.")

    driver.close()


def verify(uri: str, user: str, password: str) -> None:
    """Verify the loaded graph."""
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        # Count nodes and relationships
        stats = session.run("""
            MATCH (r:ObligationRule) WITH count(r) AS rules
            MATCH (f:ClientFact)    WITH rules, count(f) AS facts
            MATCH ()-[rel:REQUIRES_CONTROL]->() WITH rules, facts, count(rel) AS req_rels
            MATCH ()-[t:TRIGGERS]->()           WITH rules, facts, req_rels, count(t) AS trig_rels
            RETURN rules, facts, req_rels, trig_rels
        """).single()

        print(f"\nNeo4j verification:")
        print(f"  ObligationRule nodes:    {stats['rules']}")
        print(f"  ClientFact nodes:        {stats['facts']}")
        print(f"  REQUIRES_CONTROL rels:   {stats['req_rels']}")
        print(f"  TRIGGERS rels:           {stats['trig_rels']}")

        # Test Arion profile
        from enrichment.obligations.client_facts import ARION_FACTS
        from enrichment.obligations.obligation_rules import get_implied_controls

        implied = get_implied_controls(ARION_FACTS)
        print(f"\nArion Networks implied controls: {len(implied)}")

        # Check how many exist in Neo4j
        control_ids = [item["control_id"] for item in implied]
        found = session.run("""
            UNWIND $ids AS id
            MATCH (n:RequirementNode {id: id})
            RETURN count(n) AS found
        """, ids=control_ids).single()["found"]

        print(f"  Found in Neo4j: {found}/{len(implied)}")

    driver.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load ClientFact and ObligationRule nodes to Neo4j"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing to Neo4j")
    parser.add_argument("--verify", action="store_true",
                        help="Verify after loading")
    parser.add_argument("--neo4j-uri",      default="bolt://127.0.0.1:7687")
    parser.add_argument("--neo4j-user",     default="neo4j")
    parser.add_argument("--neo4j-password", default=None)
    args = parser.parse_args()

    password = (args.neo4j_password
                or os.getenv("NEO4J_PASSWORD", "arionneo4j@2026"))

    print(f"Neo4j: {args.neo4j_uri}")
    print(f"Dry run: {args.dry_run}")

    load_to_neo4j(
        uri      = args.neo4j_uri,
        user     = args.neo4j_user,
        password = password,
        dry_run  = args.dry_run,
    )

    if args.verify and not args.dry_run:
        verify(args.neo4j_uri, args.neo4j_user, password)


if __name__ == "__main__":
    main()
