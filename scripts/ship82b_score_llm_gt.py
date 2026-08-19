#!/usr/bin/env python3
"""Ship 82'.b — re-score all measurement runs against LLM-authored GT.

Compares hand GT vs LLM GT on all 8 measured extractor paths.
Expected: precision ceiling breaks (hand 17% → LLM 30-50%) because
the LLM GT enumerates MUSTs my hand GT didn't consider.

Run F (union+vocab) is the primary reference. If LLM-GT precision
jumps significantly, that quantifies how much of the "unknown FPs"
were actually legitimate.
"""
from __future__ import annotations
import sys
import re
import yaml
from pathlib import Path
from collections import defaultdict

REPO = Path("/data/arioncomply")
sys.path.insert(0, str(REPO / "scripts"))

# Reuse the scorer + finding loaders from ship77e
from ship77e_compare import (
    _load_findings, _score,
    RUN_A, RUN_B, RUN_C, RUN_D, RUN_E, RUN_F, RUN_G, RUN_H, RUN_I,
    DOCS,
)


LLM_GT_DIR = REPO / "docs" / "ground_truth" / "llm_authored"


def _load_llm_gt(doc_key: str) -> list[tuple[str, str, str]]:
    """Return [(must_id, verdict, confidence)] from LLM-authored yaml.

    Uses regex parsing to tolerate Claude's quote strings which may
    contain YAML-unfriendly escape sequences (e.g. \\() in
    "Accept/Mitigate/Reject" enum lists.
    """
    path = LLM_GT_DIR / f"{doc_key}_expected.yaml"
    if not path.exists():
        return []
    text = path.read_text()
    out: list[tuple[str, str, str]] = []
    # Pattern: - must_id: X\n    verdict: Y\n    confidence: Z
    for m in re.finditer(
        r"-\s*must_id:\s*(\S+)\s*\n"
        r"\s+verdict:\s*(\w+)\s*\n"
        r"\s+confidence:\s*(\w+)",
        text,
    ):
        out.append((m.group(1), m.group(2), m.group(3)))
    return out


def main():
    print("Ship 82'.b — score runs against LLM-authored GT")
    print("=" * 68)

    runs = {
        "consensus (A)":     RUN_A,
        "critic (B)":        RUN_B,
        "cons+verify (C)":   RUN_C,
        "union_tuned (D)":   RUN_D,
        "union_artefact (E)": RUN_E,
        "union_vocab (F)":   RUN_F,
        "wired (G)":         RUN_G,
        "llm_signal (H)":    RUN_H,
        "llm_per_must (I)":  RUN_I,
    }
    findings_by_run = {name: _load_findings(path) if path.exists() else {}
                       for name, path in runs.items()}

    all_scores: dict[str, dict[str, dict]] = {name: {} for name in runs}

    for doc_key, (yaml_file, doc_name) in DOCS.items():
        gt_musts = _load_llm_gt(doc_key)
        if not gt_musts:
            print(f"  [skip] {doc_key} — no LLM GT")
            continue
        print(f"\n─── {doc_key} ({doc_name[:40]}) ───")
        print(f"  LLM GT: satisfies={sum(1 for _,v,_ in gt_musts if v=='satisfies')} "
              f"partial={sum(1 for _,v,_ in gt_musts if v=='partial')} "
              f"not_satisfies={sum(1 for _,v,_ in gt_musts if v=='not_satisfies')} "
              f"not_applicable={sum(1 for _,v,_ in gt_musts if v=='not_applicable')}")
        for name, findings in findings_by_run.items():
            f_list = findings.get(doc_name, [])
            if not f_list:
                continue
            s = _score(f_list, gt_musts)
            all_scores[name][doc_key] = s
            print(f"  {name:<20} {s['n_findings']:>4} findings  "
                  f"strict F1={s['strict']['f1']:>6.2%} "
                  f"(P={s['strict']['p']:.1%} R={s['strict']['r']:.1%} "
                  f"TP={s['strict']['tp']}) | "
                  f"lenient F1={s['lenient']['f1']:>6.2%} "
                  f"(P={s['lenient']['p']:.1%} R={s['lenient']['r']:.1%} "
                  f"TP={s['lenient']['tp']})")

    print("\n" + "=" * 68)
    print("AGGREGATE across all docs (LLM-authored GT)")
    print("=" * 68)
    for name, per_doc in all_scores.items():
        if not per_doc:
            continue
        for scoring in ("strict", "lenient"):
            tps  = sum(per_doc[d][scoring]["tp"] for d in per_doc)
            fps  = sum(per_doc[d][scoring]["fp"] for d in per_doc)
            fns  = sum(per_doc[d][scoring]["fn"] for d in per_doc)
            p = tps / (tps + fps) if (tps + fps) else 0.0
            r = tps / (tps + fns) if (tps + fns) else 0.0
            f = 2*p*r/(p+r) if (p+r) else 0.0
            print(f"  {name:<20} {scoring:8}  P={p:>6.2%} R={r:>6.2%} "
                  f"F1={f:>6.2%}  (TP={tps} FP={fps} FN={fns})")


if __name__ == "__main__":
    main()
