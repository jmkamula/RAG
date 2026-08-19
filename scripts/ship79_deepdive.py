#!/usr/bin/env python3
"""Ship 79 deep-dive — where is recall going wrong on DPIA + DQA?

Two questions:
  1. **False negatives**: which GT `satisfies` MUSTs did NO path find?
     Those are the recall floor — no amount of prompt tuning fixes them.
  2. **False positives**: for each path's uniquely-emitted MUSTs
     (only in that path), which control-family do they concentrate on?
     That tells us which fingerprint keywords are over-firing.

For DPIA + DQA:
  - Pull GT satisfies + partial sets
  - Pull findings from A/B/D/E per doc
  - Categorise:
      * TP-all         (found by all runs) — extractor floor
      * TP-partial     (found by some runs) — differentiation
      * FN-all         (found by no run) — recall floor
      * FP-unique-in-E (found only by E, not in GT) — worst-case E noise
"""
import sys
sys.path.insert(0, "/data/arioncomply/scripts")
from collections import Counter
from ship77e_compare import (
    _load_findings, _extract_musts_from_yaml,
    RUN_A, RUN_B, RUN_D, RUN_E, GT_DIR,
)


def _finding_musts(findings):
    """Set of (control_ref, must_id) tuples for a doc's findings."""
    return {(f["control_ref"], f["checklist_item_id"] or "") for f in findings}


def _gt_verdict(gt_musts_list, must_id):
    """Return the verdict for a must_id (or 'unknown' if not enumerated)."""
    for m, v, _ in gt_musts_list:
        if m == must_id:
            return v
    return "unknown"


def deepdive(doc_key, yaml_file, doc_name):
    print(f"\n{'='*78}")
    print(f"  {doc_key}: {doc_name}")
    print(f"{'='*78}")

    gt = _extract_musts_from_yaml(GT_DIR / yaml_file)
    strict_expected = {m for m, v, _ in gt if v == "satisfies"}
    partial_expected = {m for m, v, _ in gt if v == "partial"}
    lenient_expected = strict_expected | partial_expected
    not_satisfies_expected = {m for m, v, _ in gt if v == "not_satisfies"}
    all_enumerated = strict_expected | partial_expected | not_satisfies_expected

    print(f"\n  GT: {len(strict_expected)} satisfies + {len(partial_expected)} partial + "
          f"{len(not_satisfies_expected)} not_satisfies = "
          f"{len(all_enumerated)} enumerated MUSTs")

    # Load each run's must-set for this doc
    runs = {}
    for label, run_path in (("A", RUN_A), ("B", RUN_B), ("D", RUN_D), ("E", RUN_E)):
        f_list = _load_findings(run_path).get(doc_name, [])
        runs[label] = {mid for (_ref, mid) in _finding_musts(f_list) if mid}

    print(f"\n  Findings per run (distinct must_ids): "
          f"A={len(runs['A'])} B={len(runs['B'])} D={len(runs['D'])} E={len(runs['E'])}")

    # Q1: Which GT satisfies MUSTs did NO run find? (recall floor)
    fn_all_runs = strict_expected - runs["A"] - runs["B"] - runs["D"] - runs["E"]
    print(f"\n  RECALL FLOOR — GT satisfies MUSTs NO run found ({len(fn_all_runs)}):")
    for m in sorted(fn_all_runs):
        print(f"    {m}")

    # Q2: GT satisfies found by SOME runs
    tp_any = strict_expected - fn_all_runs
    print(f"\n  DIFFERENTIATION — GT satisfies found by some ({len(tp_any)}):")
    for m in sorted(tp_any):
        who = "".join(k for k in ("A", "B", "D", "E") if m in runs[k])
        print(f"    [{who:<4}] {m}")

    # Q3: E's uniques (found only by E, not by A/B/D) — where E hallucinates
    e_uniques = runs["E"] - runs["A"] - runs["B"] - runs["D"]
    print(f"\n  E-UNIQUE MUSTs (found only by E, not A/B/D) ({len(e_uniques)}):")
    e_unique_verdicts = Counter()
    for m in e_uniques:
        v = _gt_verdict(gt, m)
        e_unique_verdicts[v] += 1
    for v, n in sorted(e_unique_verdicts.items()):
        print(f"    {v}: {n}")

    # Q4: Which control families dominate E's FPs?
    e_fps = runs["E"] - strict_expected - partial_expected
    print(f"\n  E's FP concentration by control-family ({len(e_fps)} FPs):")
    fam_counter = Counter()
    for m in e_fps:
        # Extract control-family from must_id: item:Art.35:xxx → Art
        parts = m.split(":", 2)
        if len(parts) >= 2:
            ref = parts[1]
            # Family = first two levels: Art.35 → Art, A.5.34 → A.5
            if ref.startswith("Art."):
                fam = "Art." + ref.split(".")[1] if "." in ref else ref
            elif ref[:2] in ("A.", "B."):
                fam = ".".join(ref.split(".")[:2])
            else:
                fam = ref.split(".")[0]
            fam_counter[fam] += 1
    for fam, n in fam_counter.most_common(15):
        # Is this family in the doc's expected artefacts?
        in_gt = any(m for m in all_enumerated
                    if m.startswith(f"item:{fam}") or
                       any(m.split(":")[1].startswith(fam) for m in all_enumerated if len(m.split(":")) > 1))
        marker = "✓" if in_gt else "✗"
        print(f"    {marker} {fam}: {n} FPs")

    # Q5: E - D delta (what E added beyond D)
    e_minus_d = runs["E"] - runs["D"]
    d_minus_e = runs["D"] - runs["E"]
    print(f"\n  E vs D delta:")
    print(f"    E added over D: {len(e_minus_d)} MUSTs")
    print(f"    D had, E dropped: {len(d_minus_e)} MUSTs")

    if e_minus_d:
        added_verdicts = Counter()
        for m in e_minus_d:
            added_verdicts[_gt_verdict(gt, m)] += 1
        print(f"    E-added by GT verdict: {dict(added_verdicts)}")
    if d_minus_e:
        dropped_verdicts = Counter()
        for m in d_minus_e:
            dropped_verdicts[_gt_verdict(gt, m)] += 1
        print(f"    E-dropped by GT verdict: {dict(dropped_verdicts)}")


for doc_key, yaml_file, doc_name in [
    ("DPIA", "dpia_expected.yaml",
     "Data Protection Impact Assessment (DPIA) Procedure.docx"),
    ("DQA", "dqa_expected.yaml",
     "Data Quality Accuracy Procedure.docx"),
]:
    deepdive(doc_key, yaml_file, doc_name)
