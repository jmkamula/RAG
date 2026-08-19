#!/usr/bin/env python3
"""Ship 84'.a — extend LLM GT authoring to XLSX format.

Reuses Ship 82'.a's 2-pass Claude Opus GT authoring (`ship82a_gt_authoring.py`),
just points it at 4 XLSX docs on the demo tenant instead of the 5 DOCX baseline.

The `read_document` reader dispatches to `_read_xlsx` for xlsx/xlsm files;
each sheet renders as a pipe-delimited markdown table. Claude Opus sees
those tables and can judge per-MUST verdicts the same way it does on DOCX.

Docs selected:
  iso_workbook  — 300KB ISO 27001 workbook (93 findings from
                  workbook_persistence path)
  a51_review    — templated A.5.1 annual review (3 findings)
  a51_comm      — templated A.5.1 communication record (3 findings)
  raci          — RACI-filled workbook (4 findings)

Cost estimate: ~$5-6 via claude-opus-4-7 (dominated by big workbook).

Usage:
    PYTHONPATH=. python3 scripts/ship84a_gt_xlsx.py            # all 4 docs
    PYTHONPATH=. python3 scripts/ship84a_gt_xlsx.py --only iso_workbook
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, "/data/arioncomply/scripts")
from ship82a_gt_authoring import (
    author_gt_for_doc, _fetch_leaf_catalog,
)

# 4 XLSX docs from Arion demo tenant (verified extraction_status='completed')
XLSX_DOCS = {
    "iso_workbook":   ("ab4be0ba-9dfa-4ccd-a854-889cad1d1ee6",
                        "ISO 27001 workbook Arion Networks.xlsm"),
    "a51_review":     ("2e4e3cdd-afa0-4706-a109-eaf3fb53e3a7",
                        "A_5_1_annual_review.xlsx"),
    "a51_comm":       ("a647d4f4-f128-4977-a879-87134b1cab47",
                        "A_5_1_communication_record.xlsx"),
    "raci":           ("4a9a34c5-00d2-42d5-90f5-f78c7549ecb5",
                        "rt_raci_filled.xlsx"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="Only run for this doc_key")
    args = ap.parse_args()

    catalog = _fetch_leaf_catalog()
    print(f"Loaded leaf catalog: {len(catalog)} leaves")

    docs_to_run = XLSX_DOCS
    if args.only:
        if args.only not in XLSX_DOCS:
            print(f"Unknown doc_key: {args.only}. Valid: {list(XLSX_DOCS.keys())}", file=sys.stderr)
            sys.exit(2)
        docs_to_run = {args.only: XLSX_DOCS[args.only]}

    total_stats = []
    t_start = time.time()
    for doc_key, (upload_id, doc_name) in docs_to_run.items():
        stats = author_gt_for_doc(doc_key, upload_id, doc_name, catalog)
        total_stats.append(stats)

    print(f"\n=== XLSX TOTALS (elapsed {int(time.time()-t_start)}s) ===")
    for s in total_stats:
        print(f"  {s['doc_key']:<15} in_scope={s['in_scope_leaves']:>3} "
              f"verdicts={s['verdicts_total']:>3}  {s.get('verdicts_by_verdict', {})}")


if __name__ == "__main__":
    main()
