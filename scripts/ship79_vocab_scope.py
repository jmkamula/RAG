#!/usr/bin/env python3
"""Ship 79 — measure the vocab-mismatch scope across all 5 baseline docs.

Question: is the DPIA 7-MUST recall floor an outlier, or does the
same fingerprint-catalog gap exist across all docs?

Metric: what % of GT `satisfies` MUSTs did NO run find (aggregate
recall floor)? Break down by:
  - Per-doc miss rate
  - Per-control-family miss rate
  - Per-MUST-shape miss rate (procedure / register / review / scope)
"""
import sys
sys.path.insert(0, "/data/arioncomply/scripts")
from collections import Counter
from ship77e_compare import (
    _load_findings, _extract_musts_from_yaml,
    RUN_A, RUN_B, RUN_D, RUN_E, GT_DIR, DOCS,
)


def _finding_musts(findings):
    return {(f["control_ref"], f["checklist_item_id"] or "") for f in findings}


def _must_shape(must_id):
    """Classify a MUST id into structural buckets by naming convention.
    Curation convention: item:REF:<slug> where slug is prefixed by
    reg_/rev_/proc_/scope_ etc."""
    parts = must_id.split(":")
    if len(parts) < 3:
        return "other"
    slug = parts[2]
    if slug.startswith("reg_"):    return "register"
    if slug.startswith("rev_"):    return "review"
    if slug.startswith("proc_"):   return "procedure"
    if slug.startswith("scope_"):  return "scope"
    if slug.startswith("ropa_"):   return "register"
    if slug.startswith("pia_"):    return "procedure"
    if slug.startswith("dfi_"):    return "register"
    return "other"


def _control_family(must_id):
    """Extract control family from must_id: item:Art.35:xxx → 'Art.35'."""
    parts = must_id.split(":", 2)
    if len(parts) < 2:
        return "unknown"
    ref = parts[1]
    # Trim to family: Art.35.3 → Art.35; A.7.2.5 → A.7.2 (leaf-level family)
    if ref.startswith("Art."):
        bits = ref.split(".")
        return f"Art.{bits[1]}" if len(bits) > 1 else ref
    if ref[:2] in ("A.", "B."):
        bits = ref.split(".")
        return ".".join(bits[:3]) if len(bits) >= 3 else ref
    return ref


def main():
    # Aggregate all GT satisfies + partial across 5 docs
    all_satisfies = []  # (doc_key, must_id)
    for doc_key, (yaml_file, doc_name) in DOCS.items():
        gt = _extract_musts_from_yaml(GT_DIR / yaml_file)
        for m, v, _ in gt:
            if v == "satisfies":
                all_satisfies.append((doc_key, m, doc_name))

    # For each MUST, check if any run found it
    found_by = {}  # (doc_key, must_id) → set of run labels
    for doc_key, m, doc_name in all_satisfies:
        found = set()
        for label, run_path in (("A", RUN_A), ("B", RUN_B), ("D", RUN_D), ("E", RUN_E)):
            f_list = _load_findings(run_path).get(doc_name, [])
            f_musts = {mid for (_ref, mid) in _finding_musts(f_list) if mid}
            if m in f_musts:
                found.add(label)
        found_by[(doc_key, m)] = found

    # Aggregate stats
    total_expected = len(all_satisfies)
    fn_all_runs = [(dk, m) for (dk, m), runs in found_by.items() if not runs]
    tp_any_run = total_expected - len(fn_all_runs)

    print(f"{'='*70}")
    print(f"  VOCAB-MISMATCH SCOPE — aggregate recall floor")
    print(f"{'='*70}")
    print(f"\n  Total GT `satisfies` MUSTs across 5 docs: {total_expected}")
    print(f"  Found by ≥1 run:  {tp_any_run} ({tp_any_run/total_expected:.1%})")
    print(f"  Found by NO run:  {len(fn_all_runs)} ({len(fn_all_runs)/total_expected:.1%})")

    # Per-doc breakdown
    print(f"\n  PER-DOC MISS RATE:")
    for dk in sorted(DOCS.keys()):
        doc_gt = [1 for (d, _, _) in all_satisfies if d == dk]
        doc_missed = [1 for (d, _) in fn_all_runs if d == dk]
        n_gt = len(doc_gt)
        n_missed = len(doc_missed)
        if n_gt:
            print(f"    {dk:12} {n_missed:2}/{n_gt:2} missed ({n_missed/n_gt:.0%})")

    # By MUST shape
    print(f"\n  PER-MUST-SHAPE MISS RATE:")
    shape_gt = Counter()
    shape_missed = Counter()
    for (dk, m, _) in all_satisfies:
        shape = _must_shape(m)
        shape_gt[shape] += 1
        if (dk, m) in [(d, mm) for (d, mm) in fn_all_runs]:
            shape_missed[shape] += 1
    for shape in sorted(shape_gt):
        n_gt = shape_gt[shape]
        n_missed = shape_missed[shape]
        if n_gt:
            print(f"    {shape:12} {n_missed:2}/{n_gt:2} missed ({n_missed/n_gt:.0%})")

    # By control-family (top 15)
    print(f"\n  PER-CONTROL-FAMILY MISS RATE (top 15 by family size):")
    fam_gt = Counter()
    fam_missed = Counter()
    for (dk, m, _) in all_satisfies:
        fam = _control_family(m)
        fam_gt[fam] += 1
        if (dk, m) in [(d, mm) for (d, mm) in fn_all_runs]:
            fam_missed[fam] += 1
    for fam, n_gt in fam_gt.most_common(15):
        n_missed = fam_missed.get(fam, 0)
        print(f"    {fam:12} {n_missed:2}/{n_gt:2} missed ({n_missed/n_gt:.0%})")

    # List the specific missed MUSTs so a curator can act
    print(f"\n  ALL {len(fn_all_runs)} MISSED MUSTs:")
    for dk, m in sorted(fn_all_runs):
        shape = _must_shape(m)
        fam = _control_family(m)
        print(f"    [{dk:9}] [{shape:10}] [{fam:10}] {m}")


if __name__ == "__main__":
    main()
