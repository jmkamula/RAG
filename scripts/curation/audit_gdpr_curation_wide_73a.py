#!/usr/bin/env python3
"""Ship 73'.a wide audit — full GDPR curation-state coverage matrix.

For every GDPR article (Art.1..Art.91), enumerate the state across
every curation surface:

  - Neo4j whole-article node existence
  - Sub-clause nodes (Art.N.X, Art.N.X.Y)
  - Inbound bridge edges (whole + to sub-clauses)
  - EvidenceRequirement leaves (from Python catalog)
  - DerivedSpec definitions
  - MUST/SHOULD item content (guidance authored per Ship 56')
  - Prerequisites authored per Ship 57'
  - doc_mappings referencing GDPR leaves
  - workbook_mappings referencing GDPR leaves
  - Fingerprints for GDPR leaf-scan
  - Eval cases mentioning the article ref
  - Arion posture seed rows

Output: `results/gdpr_curation_wide_audit.csv` (per-article) +
console summary with gaps ranked.

Run:
    PYTHONPATH=/data/arioncomply python3 scripts/curation/audit_gdpr_curation_wide_73a.py
"""
from __future__ import annotations

import csv
import glob
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass


def _neo_query() -> dict[str, dict]:
    """Return {ref: {'exists': bool, 'sub_clauses': int, 'bridges_whole': int,
    'bridges_subclause': int}} for every Art.N up to Art.91."""
    from neo4j import GraphDatabase
    uri  = os.getenv("NEO4J_URI",     "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USER",    "neo4j")
    pw   = os.getenv("NEO4J_PASSWORD","arionneo4j2026")
    d = GraphDatabase.driver(uri, auth=(user, pw))

    stats: dict[str, dict] = {}
    for n in range(1, 92):
        stats[f"Art.{n}"] = {
            "exists": False, "sub_clauses": 0,
            "bridges_whole": 0, "bridges_subclause": 0,
        }

    with d.session() as s:
        # Whole-article nodes + inbound ISO bridges
        for row in s.run(r"""
            MATCH (a:RequirementNode {standard_id:"GDPR:2016/679"})
            WHERE a.ref =~ 'Art\.[0-9]+' AND toInteger(replace(a.ref, 'Art.', '')) <= 91
            OPTIONAL MATCH (src:RequirementNode)-[e:IMPLEMENTS|SUPPORTS|ENABLES|GOVERNANCE]->(a)
            WHERE src.standard_id STARTS WITH 'ISO'
            WITH a, count(e) AS n_edges
            RETURN a.ref AS ref, n_edges
        """).data():
            stats[row["ref"]]["exists"] = True
            stats[row["ref"]]["bridges_whole"] = row["n_edges"]

        # Sub-clause nodes + their inbound bridges, aggregated to parent
        for row in s.run(r"""
            MATCH (sub:RequirementNode {standard_id:"GDPR:2016/679"})
            WHERE sub.ref =~ 'Art\.[0-9]+\..+'
            OPTIONAL MATCH (src:RequirementNode)-[e:IMPLEMENTS|SUPPORTS|ENABLES|GOVERNANCE]->(sub)
            WHERE src.standard_id STARTS WITH 'ISO'
            WITH sub, count(e) AS n_edges
            RETURN sub.ref AS ref, n_edges
        """).data():
            m = re.match(r"^(Art\.\d+)\.", row["ref"])
            if m:
                parent = m.group(1)
                if parent in stats:
                    stats[parent]["sub_clauses"] += 1
                    stats[parent]["bridges_subclause"] += row["n_edges"]
    d.close()
    return stats


def _catalog_stats() -> dict[str, dict]:
    """{ref: {'leaves': int, 'derived_specs': int, 'must_total': int,
    'must_with_guidance': int, 'should_total': int, 'should_with_guidance': int}}

    Uses `rag.templates.guidance_lookup.get_guidance_for_item` — which
    triggers `apply_guidance_to_catalog` on first call — so the guidance
    counts reflect the actual store rather than the raw dataclass
    attributes (which are empty until the applier runs).
    """
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    from rag.templates.guidance_lookup import get_guidance_for_item

    stats: dict[str, dict] = defaultdict(lambda: {
        "leaves": 0, "derived_specs": 0,
        "must_total": 0, "must_with_guidance": 0,
        "should_total": 0, "should_with_guidance": 0,
    })

    def _ref_from_leaf_id(leaf_id: str) -> str:
        # req:Art.32:program_review → Art.32
        # req:Art.32.1.b:x → Art.32 (roll sub-clause to parent)
        parts = leaf_id.split(":", 2)
        if len(parts) < 3:
            return ""
        ref = parts[1]
        m = re.match(r"^(Art\.\d+)", ref)
        return m.group(1) if m else ""

    seen_leaves: set[str] = set()
    seen_ds:     set[str] = set()

    def _count_er(er):
        ref = _ref_from_leaf_id(er.id)
        if not ref.startswith("Art."):
            return
        if er.id not in seen_leaves:
            seen_leaves.add(er.id)
            stats[ref]["leaves"] += 1
        for ci in er.must_contain or []:
            stats[ref]["must_total"] += 1
            if get_guidance_for_item(ci.id):
                stats[ref]["must_with_guidance"] += 1
        for ci in er.should_contain or []:
            stats[ref]["should_total"] += 1
            if get_guidance_for_item(ci.id):
                stats[ref]["should_with_guidance"] += 1

    for er in ALL_EVIDENCE_REQUIREMENTS:
        _count_er(er)
    for ds in ALL_DERIVED_SPECS:
        ds_id = getattr(ds, "spec_id", None) or getattr(ds, "id", "")
        # Any GDPR article referenced?
        m = re.search(r"Art\.\d+", ds_id)
        parent_ref = m.group() if m else None
        if parent_ref and parent_ref not in seen_ds:
            seen_ds.add(parent_ref + ":" + ds_id)
            stats[parent_ref]["derived_specs"] += 1
        for er in ds.direct_evidence or []:
            _count_er(er)
    return dict(stats)


def _prereq_stats() -> dict[str, int]:
    """{ref: count of leaves with authored prereqs}."""
    from rag.templates.prerequisites_lookup import get_prerequisites_for_leaf
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    all_ers = list(ALL_EVIDENCE_REQUIREMENTS)
    for ds in ALL_DERIVED_SPECS:
        all_ers.extend(ds.direct_evidence or [])
    counts: dict[str, int] = defaultdict(int)
    for er in all_ers:
        parts = er.id.split(":", 2)
        if len(parts) < 3 or not parts[1].startswith("Art."):
            continue
        if get_prerequisites_for_leaf(er.id):
            counts[parts[1]] += 1
    return dict(counts)


def _mapping_stats() -> dict[str, dict]:
    """{ref: {'doc_mappings': int, 'workbook_mappings': int}}."""
    import yaml
    stats: dict[str, dict] = defaultdict(lambda: {"doc_mappings": 0, "workbook_mappings": 0})
    for path in glob.glob(str(_ROOT / "db/doc_mappings/*.yaml")):
        with open(path) as f:
            try:
                data = yaml.safe_load(f) or {}
            except Exception:
                continue
        for leaf in data.get("target_leaves", []) or []:
            leaf_id = leaf.get("leaf_id", "")
            if ":Art." in leaf_id:
                ref = leaf_id.split(":", 2)[1]
                stats[ref]["doc_mappings"] += 1
    for path in glob.glob(str(_ROOT / "db/workbook_mappings/*.yaml")):
        with open(path) as f:
            try:
                data = yaml.safe_load(f) or {}
            except Exception:
                continue
        # Workbooks use `target_evidence_requirement` per pass or leaf-id refs
        text = open(path).read()
        for m in re.finditer(r"req:(Art\.\d+):", text):
            stats[m.group(1)]["workbook_mappings"] += 1
    return dict(stats)


def _fingerprint_stats() -> dict[str, int]:
    """{ref: count of leaf-scan fingerprint yaml files that mention Art.X}.

    Files live under `db/must_fingerprints/req_Art_N_slug.yaml` — the
    filename encodes the leaf ref. Also inspect the content for
    `req:Art.N:` mentions to catch cross-references.
    """
    stats: dict[str, int] = defaultdict(int)
    seen: set[tuple[str, str]] = set()
    for path in glob.glob(str(_ROOT / "db/must_fingerprints/*.yaml")):
        fname = os.path.basename(path)
        # Filename: req_Art_6_lawful_basis_register.yaml → Art.6
        m = re.match(r"^req_Art_(\d+)_", fname)
        if m:
            ref = f"Art.{m.group(1)}"
            key = (ref, fname)
            if key not in seen:
                seen.add(key)
                stats[ref] += 1
    return dict(stats)


def _eval_stats() -> dict[str, int]:
    """{ref: count of eval cases that mention this article ref}."""
    stats: dict[str, int] = defaultdict(int)
    try:
        eval_text = open(_ROOT / "tests/eval_suite.py").read()
    except Exception:
        return stats
    for m in re.finditer(r"\bArt\.\d+(?:\.\d+(?:\.\w+)?)?\b", eval_text):
        # Normalize to whole-article
        parts = m.group().split(".")
        if len(parts) >= 2:
            ref = ".".join(parts[:2])
            stats[ref] += 1
    return dict(stats)


def _posture_seed_stats() -> dict[str, int]:
    """{ref: count of posture_controls rows for Arion demo}."""
    try:
        import psycopg2
        pw = os.getenv("POSTGRES_PASSWORD", "")
        conn = psycopg2.connect(
            host="127.0.0.1", dbname="arioncomply_compliance",
            user="arioncomply", password=pw,
        )
    except Exception:
        return {}
    tid = "00000000-0000-0000-0000-000000000001"
    stats: dict[str, int] = defaultdict(int)
    try:
        with conn.cursor() as c:
            c.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tid,))
            c.execute("""
                SELECT control_ref
                  FROM posture_controls
                 WHERE tenant_id = %s::uuid AND control_ref LIKE 'Art.%%'
            """, (tid,))
            for (ref,) in c.fetchall():
                # Normalize to whole-article
                parts = ref.split(".")
                if len(parts) >= 2:
                    root = ".".join(parts[:2])
                    stats[root] += 1
    finally:
        conn.close()
    return dict(stats)


def main() -> int:
    print("Querying Neo4j...")
    neo   = _neo_query()
    print("Reading Python catalog...")
    cat   = _catalog_stats()
    print("Reading prereq lookup...")
    prereq = _prereq_stats()
    print("Reading doc + workbook mappings...")
    maps  = _mapping_stats()
    print("Reading fingerprints...")
    fps   = _fingerprint_stats()
    print("Reading eval suite...")
    ev    = _eval_stats()
    print("Reading Arion posture seeds...")
    seeds = _posture_seed_stats()
    print()

    # Emit CSV
    out_dir = _ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "gdpr_curation_wide_audit.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "ref",
            "node_exists", "sub_clauses",
            "bridges_whole", "bridges_subclause",
            "leaves", "derived_specs",
            "must_total", "must_with_guidance",
            "should_total", "should_with_guidance",
            "prereqs_leaves",
            "doc_mappings", "workbook_mappings", "fingerprints",
            "eval_cases", "posture_seeds",
        ])
        for n in range(1, 92):
            ref = f"Art.{n}"
            nn = neo.get(ref, {})
            cc = cat.get(ref, {})
            mm = maps.get(ref, {})
            w.writerow([
                ref,
                "Y" if nn.get("exists") else "N",
                nn.get("sub_clauses", 0),
                nn.get("bridges_whole", 0),
                nn.get("bridges_subclause", 0),
                cc.get("leaves", 0),
                cc.get("derived_specs", 0),
                cc.get("must_total", 0),
                cc.get("must_with_guidance", 0),
                cc.get("should_total", 0),
                cc.get("should_with_guidance", 0),
                prereq.get(ref, 0),
                mm.get("doc_mappings", 0),
                mm.get("workbook_mappings", 0),
                fps.get(ref, 0),
                ev.get(ref, 0),
                seeds.get(ref, 0),
            ])

    # Summary — count gaps per surface
    print("═" * 66)
    print(" GDPR curation coverage — gaps ranked by surface")
    print("═" * 66)
    # Consider "tenant-facing" = classified NOT regulatory_internal in
    # Ship 73'.a. Import that classification to filter.
    tenant_facing_refs = {
        f"Art.{n}" for n in range(1, 92)
    }
    # Drop regulatory-internal (Art.1-4, 50-76, 65-66)
    tenant_facing_refs -= {f"Art.{n}" for n in range(1, 5)}
    tenant_facing_refs -= {f"Art.{n}" for n in range(50, 77)}

    surfaces = [
        ("node_missing",        lambda r,n,c,p,m,f,e,s: not n.get("exists")),
        ("leaves_missing",      lambda r,n,c,p,m,f,e,s: c.get("leaves", 0) == 0),
        ("bridges_whole_missing",   lambda r,n,c,p,m,f,e,s: n.get("bridges_whole",0)==0 and n.get("bridges_subclause",0)==0),
        ("prereqs_missing",     lambda r,n,c,p,m,f,e,s: c.get("leaves",0) > 0 and p.get(r, 0) == 0),
        ("doc_mappings_missing",lambda r,n,c,p,m,f,e,s: c.get("leaves",0) > 0 and (m.get("doc_mappings",0)+m.get("workbook_mappings",0)) == 0),
        ("fingerprints_missing",lambda r,n,c,p,m,f,e,s: c.get("leaves",0) > 0 and f.get(r,0) == 0),
        ("eval_missing",        lambda r,n,c,p,m,f,e,s: c.get("leaves",0) > 0 and e.get(r,0) == 0),
        ("posture_seed_missing",lambda r,n,c,p,m,f,e,s: c.get("leaves",0) > 0 and s.get(r,0) == 0),
        ("guidance_incomplete", lambda r,n,c,p,m,f,e,s: c.get("must_total",0) > 0 and c.get("must_with_guidance",0) < c.get("must_total",0)),
    ]

    for name, pred in surfaces:
        gaps = [
            ref for ref in sorted(tenant_facing_refs, key=lambda x: int(x.split(".")[1]))
            if pred(ref, neo.get(ref, {}), cat.get(ref, {}), prereq, maps.get(ref, {}), fps, ev, seeds)
        ]
        print(f"\n  {name:24} {len(gaps):3} tenant-facing gaps")
        if gaps:
            gap_str = ", ".join(gaps[:20])
            if len(gaps) > 20:
                gap_str += f", ... (+{len(gaps)-20} more)"
            print(f"      {gap_str}")

    print(f"\nCSV: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
