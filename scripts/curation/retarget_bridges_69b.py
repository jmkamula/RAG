#!/usr/bin/env python3
"""Ship 69'.b — retarget 50 bridge edges to named sub-clause nodes.

For each row in `results/bridge_rationale_audit.csv` with
`classification=retargetable_now`, find the matching `RelationshipEdge(...)`
literal in `enrichment/relationships/relationship_catalog.py` and rewrite
its `target_ref='OLD'` to `target_ref='NEW'`. Then run
`enrichment/relationships/load_to_neo4j.py` to reflect the changes in
Neo4j.

The whole edge block is preserved except for that one line — rationale,
citation, role, source_ref all stay.

Idempotent: re-running against an already-retargeted catalog produces
zero matches (audit.csv reflects post-retarget state after Neo4j reload
+ re-audit).

Usage:
    # dry-run: show planned edits, don't touch anything
    python3 scripts/curation/retarget_bridges_69b.py --dry-run

    # apply: rewrite catalog + reload Neo4j
    python3 scripts/curation/retarget_bridges_69b.py
"""
from __future__ import annotations

import argparse
import ast
import csv
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

CATALOG_PATH = _ROOT / "enrichment/relationships/relationship_catalog.py"
AUDIT_CSV    = _ROOT / "results/bridge_rationale_audit.csv"


def _load_edges_with_lines(src: str) -> list[dict]:
    """AST-walk the catalog, returning one dict per RelationshipEdge call
    with source-file line range + key kwargs."""
    tree = ast.parse(src)
    out: list[dict] = []

    def const(v):
        return v.value if isinstance(v, ast.Constant) else None

    class V(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == "RelationshipEdge":
                kw = {k.arg: k.value for k in node.keywords}
                out.append({
                    "lineno":     node.lineno,
                    "end_lineno": node.end_lineno,
                    "src_ref":    const(kw.get("source_ref")),
                    "src_std":    const(kw.get("source_standard_id")),
                    "tgt_ref":    const(kw.get("target_ref")),
                    "tgt_std":    const(kw.get("target_standard_id")),
                    "et":         const(kw.get("edge_type")),
                })
            self.generic_visit(node)

    V().visit(tree)
    return out


def _load_retargets() -> list[dict]:
    """Return audit rows with classification=retargetable_now, augmented
    with the chosen `new_tgt_ref` (first narrower ref that has a node)."""
    with AUDIT_CSV.open() as fh:
        rows = [r for r in csv.DictReader(fh)
                if r["classification"] == "retargetable_now"]
    for r in rows:
        chosen = (r["narrower_refs_have_nodes"] or "").split(";")[0]
        r["new_tgt_ref"] = chosen
    return rows


def _find_target_ref_line(lines: list[str], start: int, end: int, old: str
                          ) -> int | None:
    """Return 1-based line number within [start, end] whose stripped content
    starts with `target_ref='OLD'` (single-quoted). None if not found."""
    needle = f"target_ref='{old}'"
    for lno in range(start, end + 1):
        idx = lno - 1
        if idx >= len(lines):
            break
        if needle in lines[idx]:
            return lno
    return None


def _rewrite_catalog(retargets: list[dict], dry_run: bool) -> tuple[int, int, list[str]]:
    """Return (matched_count, edited_count, diagnostics)."""
    src = CATALOG_PATH.read_text()
    edges = _load_edges_with_lines(src)
    lines = src.splitlines(keepends=True)

    diagnostics: list[str] = []
    matched = 0
    edited = 0

    for r in retargets:
        hits = [e for e in edges
                if e["src_ref"] == r["src_ref"]
                and e["src_std"] == r["src_std"]
                and e["tgt_ref"] == r["tgt_ref"]
                and e["tgt_std"] == r["tgt_std"]
                and e["et"] == r["et"]]
        if len(hits) != 1:
            diagnostics.append(
                f"SKIP  {r['src_ref']} -[{r['et']}]-> {r['tgt_ref']}: "
                f"{len(hits)} matches"
            )
            continue
        e = hits[0]
        matched += 1
        # Find the `target_ref='OLD'` line inside the edge block.
        lno = _find_target_ref_line(lines, e["lineno"], e["end_lineno"], r["tgt_ref"])
        if lno is None:
            diagnostics.append(
                f"SKIP  {r['src_ref']} -[{r['et']}]-> {r['tgt_ref']}: "
                f"target_ref line not found in L{e['lineno']}-{e['end_lineno']}"
            )
            continue
        idx = lno - 1
        old_needle = f"target_ref='{r['tgt_ref']}'"
        new_needle = f"target_ref='{r['new_tgt_ref']}'"
        lines[idx] = lines[idx].replace(old_needle, new_needle)
        edited += 1
        diagnostics.append(
            f"EDIT  L{lno}: {r['src_ref']} -[{r['et']}]-> "
            f"{r['tgt_ref']} → {r['new_tgt_ref']}"
        )

    if not dry_run and edited > 0:
        CATALOG_PATH.write_text("".join(lines))
    return matched, edited, diagnostics


def _reload_neo4j() -> int:
    """Run the relationship loader to reflect changes in Neo4j."""
    print("\n=== Reloading Neo4j from catalog ===")
    r = subprocess.run(
        [sys.executable, str(_ROOT / "enrichment/relationships/load_to_neo4j.py")],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
    )
    print(r.stdout[-2000:] if r.stdout else "(no stdout)")
    if r.returncode:
        print("STDERR:", r.stderr[-2000:])
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    retargets = _load_retargets()
    print(f"{len(retargets)} retargets requested from audit CSV\n")

    matched, edited, diagnostics = _rewrite_catalog(retargets, args.dry_run)

    for line in diagnostics:
        print(line)

    print(f"\nMatched: {matched}  Edited: {edited}  "
          f"{'(dry-run)' if args.dry_run else ''}")
    if args.dry_run:
        return 0
    if edited == 0:
        print("Nothing to reload.")
        return 0
    return _reload_neo4j()


if __name__ == "__main__":
    sys.exit(main())
