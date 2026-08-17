#!/usr/bin/env python3
"""Ship 77'.f — chaining experiment.

Test: is there a sweet spot between critic (overshoots, 251 findings)
and consensus (undershoots, 168) via chaining?

Approaches tested:
  INTERSECTION:  findings in BOTH paths (must_id match). High
                 precision, low recall.
  UNION:         findings in EITHER path (must_id match). High recall,
                 possibly lower precision than either alone.
  CRITIC-MINUS-CONSENSUS-DROPS:  critic findings whose must_id was
                 NOT explicitly dropped by consensus. Uses consensus's
                 "signal-based drop" as a filter over critic's LLM
                 findings.

Score each against ground truth via the same _score function.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/data/arioncomply/scripts")
from ship77e_compare import (
    _load_findings, _extract_musts_from_yaml, _score,
    RUN_A, RUN_B, RUN_C, GT_DIR, DOCS,
)


def _finding_must_set(findings: list[dict]) -> set[str]:
    """Set of checklist_item_ids emitted by this path."""
    return {f["checklist_item_id"] for f in findings if f["checklist_item_id"]}


def main():
    findings_a = _load_findings(RUN_A)  # consensus
    findings_b = _load_findings(RUN_B)  # critic
    findings_c = _load_findings(RUN_C) if RUN_C.exists() else {}

    # Score six paths total: A, B, C, INTERSECTION(A,B), UNION(A,B),
    # UNION(A,C).
    print("Ship 77'.f — chaining experiment: intersection + union")
    print("=" * 70)

    aggregate = {p: {"strict": [0, 0, 0], "lenient": [0, 0, 0]}
                 for p in ("consensus", "critic", "cons+verify",
                           "intersect(A,B)", "union(A,B)",
                           "critic\\consensus_drops")}

    def _accumulate(agg_key: str, s: dict):
        for k in ("strict", "lenient"):
            aggregate[agg_key][k][0] += s[k]["tp"]
            aggregate[agg_key][k][1] += s[k]["fp"]
            aggregate[agg_key][k][2] += s[k]["fn"]

    for key, (yaml_file, doc_name) in DOCS.items():
        gt_musts = _extract_musts_from_yaml(GT_DIR / yaml_file)
        f_a = findings_a.get(doc_name, [])
        f_b = findings_b.get(doc_name, [])
        f_c = findings_c.get(doc_name, [])

        musts_a = _finding_must_set(f_a)
        musts_b = _finding_must_set(f_b)
        musts_c = _finding_must_set(f_c)

        # Overlap analysis
        overlap = musts_a & musts_b
        only_a = musts_a - musts_b
        only_b = musts_b - musts_a

        print(f"\n─── {key} ───")
        print(f"  consensus musts: {len(musts_a)}, critic musts: {len(musts_b)}, "
              f"overlap: {len(overlap)}")
        print(f"  only in consensus: {len(only_a)}, only in critic: {len(only_b)}")

        # Score all 6 variants
        variants = {
            "consensus":           f_a,
            "critic":              f_b,
            "cons+verify":         f_c,
            "intersect(A,B)":      [f for f in f_a
                                     if f["checklist_item_id"] in overlap],
            "union(A,B)":          f_a + [f for f in f_b
                                     if f["checklist_item_id"] not in musts_a],
            # "critic \ consensus_drops" — critic findings whose must_id
            # was NOT among the consensus DROP set. But we only have
            # consensus's OUTPUT (accepts), not its drops. Approximated
            # here as: critic findings whose must_id is NOT in consensus
            # OUTPUT (i.e., where consensus said "not in accept zone").
            # This is really "critic minus consensus" set difference.
            "critic\\consensus_drops": [f for f in f_b
                                          if f["checklist_item_id"] not in musts_a],
        }

        for name, f_list in variants.items():
            if not f_list and name == "cons+verify":
                continue
            s = _score(f_list, gt_musts)
            _accumulate(name, s)
            x_s = s["strict"]
            x_l = s["lenient"]
            print(f"  {name:26} findings={len(f_list):3}  "
                  f"strict P={x_s['p']:.1%} R={x_s['r']:.1%} F1={x_s['f1']:.1%}  "
                  f"lenient F1={x_l['f1']:.1%}")

    # Aggregate table
    print("\n" + "=" * 70)
    print(f"{'PATH':<26} {'STRICT':^24} {'LENIENT':^24}")
    print(f"{'':<26} {'P':>5} {'R':>5} {'F1':>5} {'TP/FP/FN':>7} "
          f"{'P':>5} {'R':>5} {'F1':>5} {'TP/FP/FN':>7}")
    print("-" * 70)
    for path in ("consensus", "critic", "cons+verify",
                 "intersect(A,B)", "union(A,B)", "critic\\consensus_drops"):
        strict = aggregate[path]["strict"]
        lenient = aggregate[path]["lenient"]
        def _pf(counts):
            tp, fp, fn = counts
            p = tp/(tp+fp) if (tp+fp) else 0.0
            r = tp/(tp+fn) if (tp+fn) else 0.0
            f = 2*p*r/(p+r) if (p+r) else 0.0
            return p, r, f, tp, fp, fn
        sp, sr, sf, stp, sfp, sfn = _pf(strict)
        lp, lr, lf, ltp, lfp, lfn = _pf(lenient)
        print(f"{path:<26} {sp:>5.1%} {sr:>5.1%} {sf:>5.1%} "
              f"{stp:>3}/{sfp:>3}/{sfn:>3}   "
              f"{lp:>5.1%} {lr:>5.1%} {lf:>5.1%} "
              f"{ltp:>3}/{lfp:>3}/{lfn:>3}")


if __name__ == "__main__":
    main()
