#!/usr/bin/env python3
"""Ship 84'.b — score XLSX findings against LLM GT.

Reuses ship77e_compare._score + ship82b_score_llm_gt._load_llm_gt.
Data source: `run_xlsx_current.csv` exported from document_findings
for the 2 XLSX docs with LLM GT (iso_workbook + raci).

Reports per-doc + aggregate P/R/F1 under both strict + lenient scoring.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, "/data/arioncomply/scripts")
from ship77e_compare import _load_findings, _score
from ship82b_score_llm_gt import _load_llm_gt

MEASUREMENT_DIR = Path("/data/arioncomply/docs/ground_truth/ship77d_measurement")

XLSX_DOCS = {
    "iso_workbook":  "ISO 27001 workbook Arion Networks.xlsm",
    "raci":          "rt_raci_filled.xlsx",
}


def main():
    print("Ship 84'.b — XLSX findings scored against LLM GT")
    print("=" * 68)

    findings = _load_findings(MEASUREMENT_DIR / "run_xlsx_current.csv")

    all_scores = {}
    for doc_key, doc_name in XLSX_DOCS.items():
        gt = _load_llm_gt(doc_key)
        if not gt:
            print(f"  [skip] {doc_key} — no LLM GT")
            continue
        f_list = findings.get(doc_name, [])
        s = _score(f_list, gt)
        all_scores[doc_key] = s
        print(f"\n─── {doc_key} ({doc_name[:50]}) ───")
        n_sat = sum(1 for _, v, _ in gt if v == "satisfies")
        n_partial = sum(1 for _, v, _ in gt if v == "partial")
        n_ns = sum(1 for _, v, _ in gt if v == "not_satisfies")
        n_na = sum(1 for _, v, _ in gt if v == "not_applicable")
        print(f"  LLM GT: satisfies={n_sat} partial={n_partial} not_satisfies={n_ns} not_applicable={n_na}")
        print(f"  Findings: {s['n_findings']} (distinct MUSTs: {s['n_distinct_musts']})")
        print(f"    strict   P={s['strict']['p']:.2%} R={s['strict']['r']:.2%} F1={s['strict']['f1']:.2%} "
              f"(TP={s['strict']['tp']} FP={s['strict']['fp']} FN={s['strict']['fn']})")
        print(f"    lenient  P={s['lenient']['p']:.2%} R={s['lenient']['r']:.2%} F1={s['lenient']['f1']:.2%} "
              f"(TP={s['lenient']['tp']} FP={s['lenient']['fp']} FN={s['lenient']['fn']})")

    print("\n" + "=" * 68)
    print("AGGREGATE (XLSX)")
    for scoring in ("strict", "lenient"):
        tps = sum(s[scoring]["tp"] for s in all_scores.values())
        fps = sum(s[scoring]["fp"] for s in all_scores.values())
        fns = sum(s[scoring]["fn"] for s in all_scores.values())
        p = tps / (tps + fps) if (tps + fps) else 0.0
        r = tps / (tps + fns) if (tps + fns) else 0.0
        f = 2*p*r/(p+r) if (p+r) else 0.0
        print(f"  {scoring:8} P={p:.2%} R={r:.2%} F1={f:.2%} (TP={tps} FP={fps} FN={fns})")


if __name__ == "__main__":
    main()
