#!/usr/bin/env python3
"""Ship 79'.a — audit the DPIA + DQA union regression.

Ship 78' measured union+tuned F1 dropped ~10-12pp vs pre-union best on
structured docs (DPIA -12.7pp; DQA -9.9pp). This script isolates WHICH
MUSTs consensus caught that critic missed, and whether union+tuned's
LLM-verify step is rejecting them.

For each target doc:
  - Load Run A (consensus alone), Run B (critic alone), Run D
    (union+tuned) findings.
  - Compare MUST sets: what did consensus find that critic didn't?
    What did union+tuned KEEP vs DROP from consensus's uniques?
  - Cross-reference against the ground truth to score which of the
    dropped ones were correct-accepts.

Output: a table showing per-doc where the F1 loss came from.
"""
import sys
sys.path.insert(0, "/data/arioncomply/scripts")
from ship77e_compare import (
    _load_findings, _extract_musts_from_yaml,
    RUN_A, RUN_B, RUN_D, GT_DIR,
)


def _finding_by_must(findings):
    """Return {(control_ref, must_id): finding} — last-write-wins for
    duplicates within a run."""
    out = {}
    for f in findings:
        k = (f["control_ref"], f["checklist_item_id"] or "")
        out[k] = f
    return out


def _yaml_verdicts(yaml_path):
    """Return {must_id: verdict} from a ground-truth yaml."""
    return {m: v for m, v, _ in _extract_musts_from_yaml(yaml_path)}


def audit(doc_key, yaml_file, doc_name):
    print(f"\n=== {doc_key} ({doc_name[:40]}...) ===")

    verdicts = _yaml_verdicts(GT_DIR / yaml_file)
    a = _finding_by_must(_load_findings(RUN_A).get(doc_name, []))
    b = _finding_by_must(_load_findings(RUN_B).get(doc_name, []))
    d = _finding_by_must(_load_findings(RUN_D).get(doc_name, []))

    a_keys = set(a.keys())
    b_keys = set(b.keys())
    d_keys = set(d.keys())

    # What each set found
    only_consensus = a_keys - b_keys
    only_critic    = b_keys - a_keys
    both           = a_keys & b_keys
    print(f"  MUSTs: consensus={len(a_keys)}, critic={len(b_keys)}, "
          f"union+tuned={len(d_keys)}")
    print(f"    only_consensus (A-B): {len(only_consensus)}")
    print(f"    only_critic (B-A):    {len(only_critic)}")
    print(f"    both (A∩B):           {len(both)}")

    # Did union+tuned KEEP or DROP consensus's uniques?
    only_consensus_kept = only_consensus & d_keys
    only_consensus_dropped = only_consensus - d_keys
    print(f"  Of consensus's {len(only_consensus)} uniques:")
    print(f"    kept in union+tuned:  {len(only_consensus_kept)}")
    print(f"    dropped from union+tuned: {len(only_consensus_dropped)}")

    # Ground truth scoring of the dropped consensus uniques
    def _pf(keys):
        # Compute (satisfies, partial, not_satisfies, unknown) split
        s, p, n, u = 0, 0, 0, 0
        for (ref, mid) in keys:
            v = verdicts.get(mid, "unknown")
            if v == "satisfies": s += 1
            elif v == "partial": p += 1
            elif v == "not_satisfies": n += 1
            else: u += 1
        return f"satisfies={s}, partial={p}, not_satisfies={n}, unknown={u}"

    print(f"  GT score of dropped consensus uniques:")
    print(f"    {_pf(only_consensus_dropped)}")
    print(f"  GT score of kept consensus uniques:")
    print(f"    {_pf(only_consensus_kept)}")

    # Same question for critic's uniques (did union keep them?)
    only_critic_kept = only_critic & d_keys
    only_critic_dropped = only_critic - d_keys
    print(f"  Of critic's {len(only_critic)} uniques:")
    print(f"    kept in union+tuned:  {len(only_critic_kept)}")
    print(f"    dropped from union+tuned: {len(only_critic_dropped)}")
    print(f"  GT score of dropped critic uniques:")
    print(f"    {_pf(only_critic_dropped)}")

    # Union-added — MUSTs that appeared in D that were in NEITHER A nor B
    union_added = d_keys - a_keys - b_keys
    if union_added:
        print(f"  Union+tuned added {len(union_added)} MUSTs neither A nor B found")
        print(f"    GT score: {_pf(union_added)}")


def main():
    print("Ship 79'.a — DPIA + DQA regression audit")
    print("=" * 70)
    print("\nTarget docs where union+tuned regressed vs single-path best:")
    print("  DPIA: -12.7pp (consensus 40.7% → union 28.0%)")
    print("  DQA:  -9.9pp  (critic    38.5% → union 28.6%)")

    for doc_key, yaml_file, doc_name in [
        ("dpia", "dpia_expected.yaml",
         "Data Protection Impact Assessment (DPIA) Procedure.docx"),
        ("dqa", "dqa_expected.yaml",
         "Data Quality Accuracy Procedure.docx"),
    ]:
        audit(doc_key, yaml_file, doc_name)


if __name__ == "__main__":
    main()
