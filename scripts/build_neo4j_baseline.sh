#!/usr/bin/env bash
# scripts/build_neo4j_baseline.sh — regenerate Neo4j golden image.
#
# Emits db/baseline/neo4j_baseline.json — a full snapshot of the
# live dev-host Neo4j (all nodes across every label + all
# relationships across every type + all properties). One file,
# ~5-8 MB, git-diffable.
#
# Replaces the 5-loader chain that install.sh used before:
#   load_neo4j.py                             (ISO+GDPR nodes)
#   scripts/seed_27701_requirement_nodes.py   (ISO 27701 nodes)
#   enrichment/relationships/load_to_neo4j.py (relationship catalog)
#   load_graph_relationships.py               (PART_OF + others)
#   enrichment/documents/load_to_neo4j.py     (evidence layer)
#
# The single loader at db/baseline/load_neo4j_baseline.py reads
# this JSON and reproduces the exact graph via MERGE (idempotent).
#
# Requires NEO4J_PASSWORD in environment or in .env at repo root.
#
# Usage:
#   bash scripts/build_neo4j_baseline.sh
#
# Ship 102'.b (2026-09-01).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASELINE_DIR="${REPO_ROOT}/db/baseline"
mkdir -p "$BASELINE_DIR"

log() { printf "\033[1;34m==>\033[0m %s\n" "$*"; }
ok()  { printf "\033[1;32m✓\033[0m  %s\n" "$*"; }

log "exporting Neo4j graph to db/baseline/neo4j_baseline.json"

PYTHONPATH="$REPO_ROOT" python3 - "$BASELINE_DIR/neo4j_baseline.json" <<'PYEOF'
"""
Export the entire Neo4j graph to a single JSON file.

Node identity is via a per-label KEY_MAP (business keys, not Neo4j
internal ids). This lets the loader MERGE nodes reliably even after
a full DB reset.
"""
import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(str(Path(__file__).parent / ".env"))
except ImportError:
    pass

from neo4j import GraphDatabase
from neo4j.time import DateTime as Neo4jDateTime, Date as Neo4jDate

OUT_PATH = Path(sys.argv[1])

# Which properties uniquely identify a node of each label. Every
# customer-catalog label has one — verified during Ship 102'.b audit.
KEY_MAP = {
    "RequirementNode":         ["id"],
    "EvidenceRequirement":     ["id"],
    "FulfilmentSpec":          ["id"],
    "ChecklistItem":           ["id"],
    "Template":                ["leaf_id", "template_version"],
    "ClassificationDimension": ["id"],
    "ClassificationValue":     ["id"],
    "ClientFact":              ["id"],
    "Event":                   ["id"],
    "ObligationRule":          ["id"],
}


def _serialise(v):
    """JSON-encode Neo4j-specific types."""
    if isinstance(v, (Neo4jDateTime, Neo4jDate)):
        return {"__neo4j_datetime__": v.iso_format()}
    if isinstance(v, list):
        return [_serialise(x) for x in v]
    if isinstance(v, dict):
        return {k: _serialise(x) for k, x in v.items()}
    return v


uri  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
user = os.getenv("NEO4J_USER",     "neo4j")
pw   = os.getenv("NEO4J_PASSWORD")
if not pw:
    sys.exit("NEO4J_PASSWORD not set — export it or put it in .env at the repo root")

driver = GraphDatabase.driver(uri, auth=(user, pw))
nodes_out = []
rels_out  = []

with driver.session() as s:
    # ── 1. NODES ──────────────────────────────────────────────────
    for label, key_fields in KEY_MAP.items():
        rows = s.run(f"MATCH (n:`{label}`) RETURN properties(n) AS p").data()
        for r in rows:
            props = {k: _serialise(v) for k, v in r["p"].items()}
            key = {}
            for kf in key_fields:
                if kf not in r["p"]:
                    sys.exit(f"node with label {label} missing key field {kf}: {r['p']}")
                key[kf] = _serialise(r["p"][kf])
            nodes_out.append({
                "labels":     [label],
                "key":        key,
                "properties": props,
            })

    # Sanity: any label in the DB that we didn't export?
    all_labels = [r["label"] for r in s.run("CALL db.labels() YIELD label RETURN label").data()]
    missing = set(all_labels) - set(KEY_MAP.keys())
    if missing:
        sys.exit(f"labels in DB not covered by KEY_MAP: {missing} — extend build_neo4j_baseline.sh KEY_MAP")

    # ── 2. RELATIONSHIPS ──────────────────────────────────────────
    # For each rel, capture:
    #   type, start (label+key), end (label+key), properties
    rel_types = [r["relationshipType"]
                 for r in s.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType").data()]
    for rt in rel_types:
        # Build KEY_MAP lookup — CASE expression per label to pick
        # the right key fields. Done in Python because Cypher can't
        # dispatch by label dynamically inside a single query without
        # APOC.
        rows = s.run(f"""
            MATCH (a)-[r:`{rt}`]->(b)
            RETURN labels(a)[0] AS a_lbl, properties(a) AS a_props,
                   labels(b)[0] AS b_lbl, properties(b) AS b_props,
                   properties(r) AS r_props
        """).data()
        for r in rows:
            a_key = {k: _serialise(r["a_props"][k]) for k in KEY_MAP[r["a_lbl"]]}
            b_key = {k: _serialise(r["b_props"][k]) for k in KEY_MAP[r["b_lbl"]]}
            rels_out.append({
                "type":       rt,
                "start":      {"label": r["a_lbl"], "key": a_key},
                "end":        {"label": r["b_lbl"], "key": b_key},
                "properties": {k: _serialise(v) for k, v in r["r_props"].items()},
            })

driver.close()

try:
    git_sha = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=str(OUT_PATH.parent.parent.parent),
        text=True,
    ).strip()
except Exception:
    git_sha = "unknown"

# Sort for stable diffs. Nodes by (label, key-tuple); rels by (type,
# start.label, start.key-tuple, end.label, end.key-tuple).
def _key_tuple(k):
    return tuple(sorted(k.items()))

nodes_out.sort(key=lambda n: (n["labels"][0], _key_tuple(n["key"])))
rels_out.sort(key=lambda r: (
    r["type"],
    r["start"]["label"], _key_tuple(r["start"]["key"]),
    r["end"]["label"],   _key_tuple(r["end"]["key"]),
))

output = {
    "metadata": {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha":      git_sha,
        "node_count":   len(nodes_out),
        "rel_count":    len(rels_out),
    },
    "nodes":         nodes_out,
    "relationships": rels_out,
}

with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False, sort_keys=True)

print(f"  wrote {len(nodes_out)} nodes + {len(rels_out)} rels to {OUT_PATH}")
PYEOF

file_size=$(stat -c%s "$BASELINE_DIR/neo4j_baseline.json")
size_human=$(numfmt --to=iec-i --suffix=B "$file_size" 2>/dev/null || echo "$file_size B")
ok "wrote $size_human to db/baseline/neo4j_baseline.json"
