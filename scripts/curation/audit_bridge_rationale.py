#!/usr/bin/env python3
"""Ship 69'.a — bridge rationale classifier.

Reads every IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE bridge edge from
Neo4j; parses `e.rationale` for sub-clause + dimension markers;
classifies each edge into one of four buckets:

  A. retargetable-now   — rationale names a specific sub-clause (Art.X.Y[.z]
                          or A.N.M.k or clause N.M.k) AND that node exists in
                          Neo4j. The edge can be re-pointed to the sub-node
                          with no data model change.
  B. stub-needed         — rationale names a specific sub-clause BUT no such
                          node exists (would need Ship 59'.e-style stub
                          creation before retargeting).
  C. dimension-metadata  — rationale names a specific security dimension
                          (confidentiality / integrity / availability /
                          resilience / encryption / pseudonymisation /
                          access control / etc.) instead of a sub-clause.
                          Ship 69'.c+ would ship dimension metadata on the
                          edge.
  D. unspecified         — rationale is a whole-control-to-whole-control
                          statement with no narrower scope named. These edges
                          are honestly whole-to-whole and stay that way.

Output: `results/bridge_rationale_audit.csv` (one row per edge) +
console summary distribution.

Not idempotent — read-only against Neo4j.

Run:
    PYTHONPATH=/data/arioncomply python3 scripts/curation/audit_bridge_rationale.py
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase


# Sub-clause markers we accept as "specific ref".
# GDPR: Art.32.1.b, Art.5.1.a, Art.32.1
# ISO 27001 Annex A: A.5.15.1  (rare — most rationales cite whole A.5.X)
# ISO clauses: 6.1.2, 6.1.2.a  (with letter tail)
# ISO 27701: A.7.2.6, B.8.4.2
_SUBCLAUSE_RE = re.compile(
    r"""
    \b(
        Art\.\d+(?:\.\d+){1,2}(?:\.[a-z])?      # Art.32.1  / Art.32.1.b
      | [AB]\.\d+\.\d+\.\d+                       # A.5.15.1  / B.8.4.2
      | \b\d+\.\d+\.\d+(?:\.[a-z])?              # 6.1.2 / 6.1.2.a  (with word boundary)
    )\b
    """,
    re.VERBOSE,
)

# Dimensions/mechanisms named in rationales that could become edge
# metadata for a targeted-attribution UX in Ship 69'.c.
_DIMENSION_TOKENS = {
    "confidentiality",
    "integrity",
    "availability",
    "resilience",
    "encryption",
    "pseudonymisation",
    "pseudonymization",
    "anonymisation",
    "anonymization",
    "access control",
    "access rights",
    "authentication",
    "authorisation",
    "authorization",
    "logging",
    "monitoring",
    "backup",
    "recovery",
    "disaster recovery",
    "incident response",
    "incident notification",
    "breach notification",
    "risk assessment",
    "risk treatment",
    "impact assessment",
    "training",
    "awareness",
    "vendor management",
    "supplier management",
    "processor",
    "data minimisation",
    "data minimization",
    "purpose limitation",
    "storage limitation",
    "accuracy",
    "lawfulness",
    "transparency",
    "accountability",
}


def _extract_subclause_refs(text: str) -> list[str]:
    if not text:
        return []
    out = []
    for m in _SUBCLAUSE_RE.finditer(text):
        raw = m.group(1)
        # `9.1` or `9.2` alone matches — we accept only when it looks like
        # an ISO/ISMS clause pattern with the word boundary check baked in.
        out.append(raw)
    return list(dict.fromkeys(out))  # preserve order, dedupe


def _extract_dimensions(text: str) -> list[str]:
    if not text:
        return []
    lower = text.lower()
    hits = []
    for tok in _DIMENSION_TOKENS:
        if tok in lower:
            hits.append(tok)
    return hits


def _classify(refs: list[str], dims: list[str], node_exists: dict[str, bool],
              tgt_ref: str) -> str:
    """Returns one of: retargetable_now / stub_needed / dimension_metadata /
    unspecified.

    A rationale can cite the target's own ref (Art.32 in an edge to Art.32).
    We only consider refs *narrower* than the target (i.e. starts with
    tgt_ref + '.').
    """
    narrower = [r for r in refs if r != tgt_ref and r.startswith(tgt_ref + ".")]
    if narrower:
        # At least one narrower ref named.
        has_node = any(node_exists.get(r, False) for r in narrower)
        return "retargetable_now" if has_node else "stub_needed"
    if dims:
        return "dimension_metadata"
    return "unspecified"


def _fetch_edges(session) -> list[dict]:
    q = """
    MATCH (src:RequirementNode)-[e]->(tgt:RequirementNode)
    WHERE type(e) IN ['IMPLEMENTS','SUPPORTS','ENABLES','GOVERNANCE']
    RETURN src.standard_id AS src_std, src.ref AS src_ref,
           tgt.standard_id AS tgt_std, tgt.ref AS tgt_ref,
           type(e) AS et, coalesce(e.rationale, '') AS rat,
           coalesce(e.role, '') AS role
    """
    return [dict(r) for r in session.run(q)]


def _fetch_all_refs(session, standard_id: str) -> set[str]:
    q = """
    MATCH (n:RequirementNode {standard_id: $sid})
    RETURN n.ref AS ref
    """
    return {r["ref"] for r in session.run(q, sid=standard_id)}


def main() -> int:
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pw = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    edges: list[dict] = []
    all_refs_by_std: dict[str, set[str]] = {}

    with driver.session() as s:
        edges = _fetch_edges(s)
        stds = {e["tgt_std"] for e in edges} | {e["src_std"] for e in edges}
        for sid in stds:
            all_refs_by_std[sid] = _fetch_all_refs(s, sid)

    # Classify + write per-edge CSV.
    out_dir = _ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "bridge_rationale_audit.csv"

    counter = Counter()
    per_class_samples: dict[str, list[dict]] = {
        "retargetable_now": [],
        "stub_needed": [],
        "dimension_metadata": [],
        "unspecified": [],
    }
    per_type_class = Counter()
    dim_counter = Counter()

    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "src_std", "src_ref", "et", "tgt_std", "tgt_ref", "role",
            "classification", "narrower_refs_named",
            "narrower_refs_have_nodes", "dimensions_named", "rationale",
        ])
        for e in edges:
            refs = _extract_subclause_refs(e["rat"])
            dims = _extract_dimensions(e["rat"])
            tgt_std = e["tgt_std"]
            # node_exists dict keyed by ref (in tgt standard).
            node_exists = {
                r: r in all_refs_by_std.get(tgt_std, set()) for r in refs
            }
            cls = _classify(refs, dims, node_exists, e["tgt_ref"])
            counter[cls] += 1
            per_type_class[(e["et"], cls)] += 1
            for d in dims:
                dim_counter[d] += 1
            if len(per_class_samples[cls]) < 5:
                per_class_samples[cls].append({**e, "narrower": refs, "dims": dims})
            narrower_named = [r for r in refs if r != e["tgt_ref"]
                              and r.startswith(e["tgt_ref"] + ".")]
            narrower_nodes = [r for r in narrower_named
                              if node_exists.get(r, False)]
            w.writerow([
                e["src_std"], e["src_ref"], e["et"], e["tgt_std"], e["tgt_ref"],
                e["role"], cls,
                ";".join(narrower_named),
                ";".join(narrower_nodes),
                ";".join(dims),
                e["rat"],
            ])

    total = sum(counter.values())
    print(f"Bridge rationale audit — {total} edges classified\n")
    print("=== Distribution ===")
    for cls in ("retargetable_now", "stub_needed", "dimension_metadata",
                "unspecified"):
        n = counter.get(cls, 0)
        pct = 100.0 * n / total if total else 0.0
        print(f"  {cls:22} {n:4}  ({pct:5.1f}%)")

    print("\n=== Per edge type × class ===")
    for et in ("IMPLEMENTS", "SUPPORTS", "ENABLES", "GOVERNANCE"):
        row_total = sum(v for (e_t, _), v in per_type_class.items() if e_t == et)
        print(f"  {et:12} (n={row_total})")
        for cls in ("retargetable_now", "stub_needed", "dimension_metadata",
                    "unspecified"):
            n = per_type_class.get((et, cls), 0)
            pct = 100.0 * n / row_total if row_total else 0.0
            print(f"    {cls:22} {n:4}  ({pct:5.1f}%)")

    print("\n=== Top-15 dimensions named across all edges ===")
    for dim, n in dim_counter.most_common(15):
        print(f"  {dim:32} {n}")

    print("\n=== Samples per class ===")
    for cls, samples in per_class_samples.items():
        if not samples:
            continue
        print(f"\n-- {cls} --")
        for s in samples:
            print(f"  {s['src_std']} {s['src_ref']} -[{s['et']}]-> "
                  f"{s['tgt_std']} {s['tgt_ref']}")
            if s.get("narrower"):
                print(f"    narrower refs named: {s['narrower']}")
            if s.get("dims"):
                print(f"    dimensions:          {s['dims']}")
            print(f"    rat: {s['rat'][:180]}")

    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
