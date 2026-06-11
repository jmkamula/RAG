"""
DSAR-family bridge curation (2026-06-11).

Prune 14 wrong-shape access-control/inventory/auth bridges to GDPR
DSAR-family articles (Art.15-21), and add 7 IMPLEMENTS bridges from
A.5.34 (PII protection) as the natural primary for subject-rights
procedures.

Edits three sources of truth:
  - iso_nodes_phase1.json   (ISO side cross_framework_summary)
  - gdpr_nodes_phase2.json  (GDPR side cross_framework_summary)
  - Neo4j (both forward and reverse edges)

See [[posture-claim-hallucination-guard]] (Art.18/Art.21 over-attrib
surfaced 2026-06-11 on Security Test Report.docx upload).
"""

import json
import os
import sys
from pathlib import Path

from neo4j import GraphDatabase
from dotenv import load_dotenv


ROOT = Path("/data/arioncomply")
ISO_JSON  = ROOT / "iso_nodes_phase1.json"
GDPR_JSON = ROOT / "gdpr_nodes_phase2.json"


PRUNES = [
    ("ISO27001:2022:A.5.15", "GDPR:2016/679:Art.15", "ENABLES"),
    ("ISO27001:2022:A.5.15", "GDPR:2016/679:Art.18", "IMPLEMENTS"),
    ("ISO27001:2022:A.5.15", "GDPR:2016/679:Art.21", "IMPLEMENTS"),
    ("ISO27001:2022:A.5.18", "GDPR:2016/679:Art.15", "SUPPORTS"),
    ("ISO27001:2022:A.5.18", "GDPR:2016/679:Art.18", "SUPPORTS"),
    ("ISO27001:2022:A.5.9",  "GDPR:2016/679:Art.15", "ENABLES"),
    ("ISO27001:2022:A.5.9",  "GDPR:2016/679:Art.16", "ENABLES"),
    ("ISO27001:2022:A.5.9",  "GDPR:2016/679:Art.17", "ENABLES"),
    ("ISO27001:2022:A.5.9",  "GDPR:2016/679:Art.18", "ENABLES"),
    ("ISO27001:2022:A.5.9",  "GDPR:2016/679:Art.20", "ENABLES"),
    ("ISO27001:2022:A.5.9",  "GDPR:2016/679:Art.21", "ENABLES"),
    ("ISO27001:2022:A.8.3",  "GDPR:2016/679:Art.18", "IMPLEMENTS"),
    ("ISO27001:2022:A.8.5",  "GDPR:2016/679:Art.15", "ENABLES"),
    ("ISO27001:2022:A.8.5",  "GDPR:2016/679:Art.20", "ENABLES"),
]


ADDS = [
    ("ISO27001:2022:A.5.34", "GDPR:2016/679:Art.15", "IMPLEMENTS",
     "PII protection includes subject access request procedures — the primary control for fulfilling DSAR identification, search, and response."),
    ("ISO27001:2022:A.5.34", "GDPR:2016/679:Art.16", "IMPLEMENTS",
     "PII protection includes rectification procedures for maintaining accuracy of personal data."),
    ("ISO27001:2022:A.5.34", "GDPR:2016/679:Art.17", "IMPLEMENTS",
     "PII protection includes erasure procedures — the procedural side of right-to-be-forgotten alongside A.8.10 information deletion."),
    ("ISO27001:2022:A.5.34", "GDPR:2016/679:Art.18", "IMPLEMENTS",
     "PII protection includes processing-restriction procedures triggered by subject requests."),
    ("ISO27001:2022:A.5.34", "GDPR:2016/679:Art.19", "IMPLEMENTS",
     "PII protection includes recipient-notification procedures when data is rectified, erased, or restricted."),
    ("ISO27001:2022:A.5.34", "GDPR:2016/679:Art.20", "IMPLEMENTS",
     "PII protection includes data-portability procedures (structured machine-readable export)."),
    ("ISO27001:2022:A.5.34", "GDPR:2016/679:Art.21", "IMPLEMENTS",
     "PII protection includes objection-handling procedures including opt-out flags for direct marketing/profiling."),
]


def _short(ref: str) -> str:
    return ref.split(":")[-1]


def _load(path: Path):
    with path.open() as f:
        return json.load(f)


def _save(path: Path, data) -> None:
    with path.open("w") as f:
        # ensure_ascii=True matches the original file's escape style so
        # the diff highlights only the bridge changes, not the encoding.
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")


def _index_by_id(nodes):
    return {n["id"]: n for n in nodes}


def edit_json_files() -> dict:
    iso  = _load(ISO_JSON)
    gdpr = _load(GDPR_JSON)
    iso_idx  = _index_by_id(iso)
    gdpr_idx = _index_by_id(gdpr)

    stats = {"prune_iso_side": 0, "prune_gdpr_side": 0,
             "add_iso_side": 0, "add_gdpr_side": 0,
             "prune_missing": []}

    for iso_id, gdpr_id, rel in PRUNES:
        iso_node  = iso_idx.get(iso_id)
        gdpr_node = gdpr_idx.get(gdpr_id)

        if iso_node and "cross_framework_summary" in iso_node:
            cfs = iso_node["cross_framework_summary"]
            entry = cfs.get(gdpr_id)
            if entry and entry.get("relationship_type") == rel:
                del cfs[gdpr_id]
                stats["prune_iso_side"] += 1
            else:
                stats["prune_missing"].append(f"ISO side: {iso_id} → {gdpr_id} ({rel})")

        if gdpr_node and "cross_framework_summary" in gdpr_node:
            cfs = gdpr_node["cross_framework_summary"]
            entry = cfs.get(iso_id)
            if entry and entry.get("relationship_type") == rel:
                del cfs[iso_id]
                stats["prune_gdpr_side"] += 1
            else:
                stats["prune_missing"].append(f"GDPR side: {gdpr_id} ← {iso_id} ({rel})")

    for iso_id, gdpr_id, rel, rationale in ADDS:
        iso_node  = iso_idx.get(iso_id)
        gdpr_node = gdpr_idx.get(gdpr_id)

        if iso_node is not None:
            cfs = iso_node.setdefault("cross_framework_summary", {})
            cfs[gdpr_id] = {
                "related_req_id":   gdpr_id,
                "related_title":    f"GDPR {_short(gdpr_id)}",
                "related_standard": "GDPR:2016/679",
                "relationship_type": rel,
                "confidence":       "HIGH",
                "rationale":        rationale,
                "posture_lookup_ref": iso_id,
            }
            stats["add_iso_side"] += 1

        if gdpr_node is not None:
            cfs = gdpr_node.setdefault("cross_framework_summary", {})
            cfs[iso_id] = {
                "related_req_id":   iso_id,
                "related_title":    f"ISO 27001:2022 {_short(iso_id)}",
                "related_standard": "ISO27001:2022",
                "relationship_type": rel,
                "confidence":       "HIGH",
                "rationale":        rationale,
                "posture_lookup_ref": iso_id,
            }
            stats["add_gdpr_side"] += 1

    _save(ISO_JSON, iso)
    _save(GDPR_JSON, gdpr)
    return stats


def apply_neo4j() -> dict:
    load_dotenv(ROOT / ".env")
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    stats = {"prune_edges_deleted": 0, "add_edges_created": 0}

    with driver.session() as s:
        # Prune: delete both forward and reverse edges
        for iso_id, gdpr_id, rel in PRUNES:
            # forward: iso → gdpr
            r1 = s.run(f"""
                MATCH (a:RequirementNode {{id: $iso}})-[r:{rel}]->(b:RequirementNode {{id: $gdpr}})
                WITH r, count(r) AS c
                DELETE r
                RETURN c
            """, iso=iso_id, gdpr=gdpr_id).single()
            if r1:
                stats["prune_edges_deleted"] += r1["c"]
            # reverse: gdpr → iso
            r2 = s.run(f"""
                MATCH (a:RequirementNode {{id: $iso}})<-[r:{rel}]-(b:RequirementNode {{id: $gdpr}})
                WITH r, count(r) AS c
                DELETE r
                RETURN c
            """, iso=iso_id, gdpr=gdpr_id).single()
            if r2:
                stats["prune_edges_deleted"] += r2["c"]

        # Add: create both forward and reverse edges
        for iso_id, gdpr_id, rel, _rationale in ADDS:
            s.run(f"""
                MATCH (a:RequirementNode {{id: $iso}}), (b:RequirementNode {{id: $gdpr}})
                MERGE (a)-[:{rel}]->(b)
                MERGE (a)<-[:{rel}]-(b)
            """, iso=iso_id, gdpr=gdpr_id)
            stats["add_edges_created"] += 2  # forward + reverse

    driver.close()
    return stats


if __name__ == "__main__":
    print("=== JSON edits ===")
    j_stats = edit_json_files()
    for k, v in j_stats.items():
        if k == "prune_missing":
            if v:
                print(f"  {k}:")
                for line in v:
                    print(f"    - {line}")
        else:
            print(f"  {k}: {v}")

    print()
    print("=== Neo4j edits ===")
    n_stats = apply_neo4j()
    for k, v in n_stats.items():
        print(f"  {k}: {v}")
