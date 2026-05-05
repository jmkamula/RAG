"""
Load ISO and GDPR RequirementNodes from JSON phase files into Neo4j.
Run once after fresh install to rebuild the graph.
"""
import json, os, sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv('/data/arioncomply/.env')

URI  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
USER = os.getenv("NEO4J_USER",     "neo4j")
PASS = os.getenv("NEO4J_PASSWORD", "arionneo4j2026")

driver = GraphDatabase.driver(URI, auth=(USER, PASS))

FILES = [
    '/data/arioncomply/iso_nodes_phase1.json',
    '/data/arioncomply/gdpr_nodes_phase2.json',
]

STRING_KEYS = ('id','standard_id','ref','title','node_type',
               'obligation_type','applies_to','obligation_text',
               'business_description','cross_framework_summary')

total = 0
for path in FILES:
    with open(path) as f:
        nodes = json.load(f)

    print(f"Loading {len(nodes)} nodes from {path.split('/')[-1]}...")

    with driver.session() as s:
        for i, node in enumerate(nodes):
            # Only store string/scalar properties
            props = {
                k: str(v) if v is not None else ""
                for k, v in node.items()
                if k in STRING_KEYS and v is not None
            }
            node_id = node.get('id')
            if not node_id:
                continue

            s.run("""
                MERGE (n:RequirementNode {id: $id})
                SET n += $props
                SET n.standard_id = $standard_id
            """, id=node_id, props=props,
                 standard_id=node.get('standard_id',''))

            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(nodes)}...")

    total += len(nodes)
    print(f"  ✓ done\n")

# Now load relationships from enrichment tier2
tier2_path = '/data/arioncomply/enrichment/tier2_generated.json'
if os.path.exists(tier2_path):
    with open(tier2_path) as f:
        tier2 = json.load(f)
    edges = tier2 if isinstance(tier2, list) else tier2.get('relationships', tier2.get('edges', []))
    print(f"Loading {len(edges)} relationships from tier2_generated.json...")
    with driver.session() as s:
        for rel in edges:
            src   = rel.get('source') or rel.get('from')
            tgt   = rel.get('target') or rel.get('to')
            rtype = rel.get('type', 'RELATED_TO')
            if src and tgt:
                s.run(f"""
                    MATCH (a:RequirementNode {{id: $src}})
                    MATCH (b:RequirementNode {{id: $tgt}})
                    MERGE (a)-[r:{rtype}]->(b)
                """, src=src, tgt=tgt)
    print(f"  ✓ relationships loaded\n")

# Verify
with driver.session() as s:
    n      = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    labels = [r["label"] for r in s.run("CALL db.labels() YIELD label")]
    rels   = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]

print(f"✓ Total nodes:         {n}")
print(f"✓ Total relationships: {rels}")
print(f"✓ Labels:              {labels}")

driver.close()
