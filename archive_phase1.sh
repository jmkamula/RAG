#!/bin/bash
# ArionComply — Phase 1 Archive
# Creates a complete snapshot of all three databases at Phase 1 completion.
# Run AFTER load_graph_relationships.py succeeds.

set -e
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_DIR="/data/backups/phase1_${TIMESTAMP}"
mkdir -p "$ARCHIVE_DIR"

echo "╔══════════════════════════════════════════════╗"
echo "║  ArionComply — Phase 1 Archive               ║"
echo "║  ${TIMESTAMP}                       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Archive directory: $ARCHIVE_DIR"
echo ""

# ── 1. PostgreSQL dump ────────────────────────────────────────────────────────
echo "▶ PostgreSQL..."
PGPASSWORD=arioncomply2026 pg_dump \
  -U arioncomply -h 127.0.0.1 \
  -d arioncomply_compliance \
  --format=custom \
  --file="$ARCHIVE_DIR/postgres_phase1.pgdump"
echo "  ✓ postgres_phase1.pgdump"

# Schema only (human readable)
PGPASSWORD=arioncomply2026 pg_dump \
  -U arioncomply -h 127.0.0.1 \
  -d arioncomply_compliance \
  --schema-only \
  --file="$ARCHIVE_DIR/postgres_schema.sql"
echo "  ✓ postgres_schema.sql"

# Key table counts
PGPASSWORD=arioncomply2026 psql \
  -U arioncomply -h 127.0.0.1 \
  -d arioncomply_compliance \
  -o "$ARCHIVE_DIR/postgres_counts.txt" << 'SQL'
\echo '=== ROW COUNTS ==='
SELECT tablename,
       (xpath('/row/c/text()', query_to_xml(
           format('SELECT COUNT(*) AS c FROM %I', tablename),
           false, true, '')))[1]::text::int AS row_count
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY row_count DESC, tablename;

\echo ''
\echo '=== POSTURE SUMMARY ==='
SELECT finding, source, confirmation_status, COUNT(*) 
FROM posture_controls 
WHERE is_active = TRUE
GROUP BY finding, source, confirmation_status
ORDER BY finding, source;

\echo ''
\echo '=== DOCUMENT FINDINGS SUMMARY ==='
SELECT status, confidence, COUNT(*)
FROM document_findings
WHERE is_active = TRUE
GROUP BY status, confidence
ORDER BY status, confidence;

\echo ''
\echo '=== TENANT STANDARDS ==='
SELECT ts.standard_id, ts.certification_status, ts.implementation_status
FROM tenant_standards ts;
SQL
echo "  ✓ postgres_counts.txt"

# ── 2. Neo4j export ───────────────────────────────────────────────────────────
echo ""
echo "▶ Neo4j..."
python3 << 'PYEOF'
import json
from neo4j import GraphDatabase
from datetime import datetime

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j","arionneo4j2026"))
archive = {}

with driver.session() as s:
    # Node counts
    archive["node_counts"] = {}
    for r in s.run("CALL db.labels() YIELD label CALL { WITH label MATCH (n) WHERE label IN labels(n) RETURN count(n) AS c } RETURN label, c ORDER BY c DESC"):
        archive["node_counts"][r["label"]] = r["c"]

    # Relationship counts
    archive["relationship_counts"] = {}
    for r in s.run("MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c ORDER BY c DESC"):
        archive["relationship_counts"][r["t"]] = r["c"]

    # Relationship patterns
    archive["relationship_patterns"] = []
    for r in s.run("MATCH (a)-[r]->(b) RETURN DISTINCT labels(a)[0] AS f, type(r) AS t, labels(b)[0] AS to ORDER BY t, f"):
        archive["relationship_patterns"].append({"from": r["f"], "rel": r["t"], "to": r["to"]})

    # Sample RequirementNodes
    archive["sample_nodes"] = []
    for r in s.run("MATCH (n:RequirementNode) RETURN n.id, n.standard_id, n.ref, n.title LIMIT 10"):
        archive["sample_nodes"].append(dict(r))

    archive["archived_at"] = datetime.now().isoformat()
    archive["total_nodes"] = sum(archive["node_counts"].values())
    archive["total_relationships"] = sum(archive["relationship_counts"].values())

driver.close()

with open("/data/backups/ARCHIVE_DIR/neo4j_phase1.json", "w") as f:
    json.dump(archive, f, indent=2)

print(f"  ✓ neo4j_phase1.json")
print(f"    Nodes:         {archive['total_nodes']}")
print(f"    Relationships: {archive['total_relationships']}")
PYEOF

# Fix the placeholder in Python script (heredoc limitation)
python3 -c "
import json, os
src = '/data/backups/ARCHIVE_DIR/neo4j_phase1.json'
dst = '$ARCHIVE_DIR/neo4j_phase1.json'
if os.path.exists(src):
    os.rename(src, dst)
    print('  ✓ neo4j_phase1.json moved')
"

# ── 3. ChromaDB export ────────────────────────────────────────────────────────
echo ""
echo "▶ ChromaDB..."
python3 << 'PYEOF'
import json, chromadb
from datetime import datetime

client = chromadb.HttpClient(host="localhost", port=8000)
archive = {"collections": {}, "archived_at": datetime.now().isoformat()}

for col in client.list_collections():
    c = client.get_collection(col.name)
    count = c.count()
    # Sample first 3 docs
    sample = c.get(limit=3, include=["metadatas", "documents"])
    archive["collections"][col.name] = {
        "count": count,
        "sample_ids": sample["ids"][:3],
        "sample_metadata": sample["metadatas"][:3] if sample["metadatas"] else []
    }
    print(f"  {col.name:40s} {count} docs")

with open("/data/backups/CHROMADB_ARCHIVE/chroma_phase1.json", "w") as f:
    json.dump(archive, f, indent=2)
PYEOF

python3 -c "
import json, os, shutil
src = '/data/backups/CHROMADB_ARCHIVE/chroma_phase1.json'
dst = '$ARCHIVE_DIR/chroma_phase1.json'
if os.path.exists(src):
    os.rename(src, dst)
    print('  ✓ chroma_phase1.json moved')
"

# ── 4. Write phase1 manifest ──────────────────────────────────────────────────
echo ""
echo "▶ Writing manifest..."
cat > "$ARCHIVE_DIR/MANIFEST.md" << MANIFEST
# ArionComply — Phase 1 Archive
**Date:** $(date)
**Archive:** $ARCHIVE_DIR

## Contents
| File | Description |
|------|-------------|
| postgres_phase1.pgdump | Full PostgreSQL binary dump (pg_restore compatible) |
| postgres_schema.sql | Human-readable schema DDL |
| postgres_counts.txt | Row counts and key data summaries |
| neo4j_phase1.json | Neo4j node/relationship inventory |
| chroma_phase1.json | ChromaDB collection inventory |
| MANIFEST.md | This file |

## Database State

### PostgreSQL
- 45 tables
- 1 tenant: Arion Networks
- 2 standards: ISO27001:2022, ISO27701:2019
- posture_controls: 113 rows
- document_findings: 51 rows (from Access_Control_Policy.docx)

### Neo4j
- 654 nodes (RequirementNode, ChecklistItem, ClientFact, ObligationRule, DocumentRequirement, Event)
- Phase 1 relationships: DERIVED_FROM, MUST_CONTAIN, REQUIRES_CONTROL, TRIGGERS_OBLIGATION, SHOULD_CONTAIN, TRIGGERS, REQUIRES_DOCUMENT
- Phase 1b additions: PART_OF (hierarchy), IMPLEMENTS/SUPPORTS/ENABLES (cross-framework)

### ChromaDB
- 3 collections: arioncombly_all(429), gdpr_2016_679(303), iso27001_2022(126)

## Eval Baseline
- 21/21 PASS (eval_post_intake.csv)
- Source guard active: workbook/assessor findings protected from document pipeline overwrites

## Phase 2 Next Steps
- Trace enhancement: trace_id, request_trace_log entries, per-stage timing
- Human-in-the-loop review queue API endpoints
- Cross-framework relationship enrichment (IMPLEMENTS/SUPPORTS loaded in Phase 1b)
MANIFEST

echo "  ✓ MANIFEST.md"

# ── 5. Summary ────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  Phase 1 Archive Complete                    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Location: $ARCHIVE_DIR"
ls -la "$ARCHIVE_DIR"
echo ""
echo "To restore PostgreSQL:"
echo "  pg_restore -U arioncomply -h 127.0.0.1 -d arioncomply_compliance $ARCHIVE_DIR/postgres_phase1.pgdump"
