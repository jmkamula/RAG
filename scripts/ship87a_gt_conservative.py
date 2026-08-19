#!/usr/bin/env python3
"""Ship 87'.a — LLM GT re-authoring with corroboration discipline.

Ship 87' pivot: workbook_persistence YAMLs are auditor-correct (data
presence alone = partial, not satisfies). LLM GT authoring in Ship
82'.a was too permissive — Claude marked `satisfies` on single-column
presence. Re-author with a corroboration-required prompt so GT
matches the YAML authors' actual auditor discipline.

Reuses Ship 82'.a's structure (Pass 1 scope enumeration + Pass 2
per-MUST verdicts) but overrides the Pass 2 system prompt with the
corroboration-strict framing below.

Usage:
    # Single doc
    python scripts/ship87a_gt_conservative.py --only iso_workbook

    # All 4 XLSX docs
    python scripts/ship87a_gt_conservative.py

Output overwrites `docs/ground_truth/llm_authored/{key}_expected.yaml`
by design — Ship 87' replaces the previous over-permissive GT.
"""
from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, "/data/arioncomply/scripts")
import ship82a_gt_authoring as base
from ship82a_gt_authoring import (
    author_gt_for_doc, _fetch_leaf_catalog,
)
from ship84a_gt_xlsx import XLSX_DOCS


# ── Override Pass 2 system prompt with corroboration discipline ────────

_PASS2_CORROBORATION_SYSTEM = """You are a strict compliance auditor.

For each MUST item in the batch, judge whether the document contains evidence satisfying it.

Return strict JSON:
{"verdicts": [
  {"must_id": "item:X:Y",
   "verdict": "satisfies" | "partial" | "not_satisfies" | "not_applicable",
   "confidence": "high" | "medium" | "low",
   "quote": "<verbatim quote from doc, or empty>",
   "rationale": "<one-sentence reason>"},
  ...
]}

VERDICT DEFINITIONS (corroboration-strict — this is what real auditors apply):

- "satisfies": the MUST is fully evidenced. For a REGISTER MUST (`reg_*`),
  this means the row has the target column AS WELL AS corroborating
  columns (owner, date, status, or the row's identity column). A single
  populated column is NOT satisfies. Prose MUSTs need explicit statement,
  not implicit mention.
  Examples:
    * `item:A.5.9:asset_records` on Asset Register with populated Asset ID +
      Asset Name + Owner columns → satisfies.
    * `item:10.1:reg_target_date` on ISMS Schedule with only DUE DATE populated
      (no owner or status corroborating the row) → partial, NOT satisfies.
    * `item:7.2:owner` on a Competence Records sheet where the Owner column
      is populated AND the row has other filled columns (Role, Competency)
      → satisfies.
    * `item:7.2:owner` where Owner is populated on an otherwise-empty row
      → partial.

- "partial": the MUST's target column IS populated in some rows, but rows
  lack corroborating context — OR the MUST addresses intent through prose
  that lacks specificity, dates, ownership, or required attributes.

- "not_satisfies": the MUST is in the doc's scope but no evidence found.
  The doc could carry evidence for this MUST but doesn't.

- "not_applicable": the MUST is not in scope for this document type.

RULES:
- Quote must be verbatim substring from the doc (≤ 250 chars).
- Empty quote when verdict is "not_satisfies" or "not_applicable".
- Do not fabricate evidence — only cite text that actually appears.
- Return one verdict per input must_id, preserving order.
- **Default to partial when in doubt.** Satisfies should be the auditor-
  defensible verdict, not the generous one.
- Return JSON only."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="Only run for this doc_key (from XLSX_DOCS)")
    args = ap.parse_args()

    # Monkey-patch the Pass 2 system prompt so base.author_gt_for_doc uses
    # the corroboration-strict version.
    base._PASS2_SYSTEM = _PASS2_CORROBORATION_SYSTEM

    catalog = _fetch_leaf_catalog()
    print(f"Loaded catalog: {len(catalog)} leaves")
    print(f"Using corroboration-strict Pass 2 prompt (Ship 87'.a)")
    print()

    docs_to_run = XLSX_DOCS
    if args.only:
        if args.only not in XLSX_DOCS:
            print(f"Unknown key: {args.only}", file=sys.stderr)
            sys.exit(2)
        docs_to_run = {args.only: XLSX_DOCS[args.only]}

    t_start = time.time()
    total_stats = []
    for doc_key, (upload_id, doc_name) in docs_to_run.items():
        stats = author_gt_for_doc(doc_key, upload_id, doc_name, catalog)
        total_stats.append(stats)

    print(f"\n=== Ship 87'.a XLSX (corroboration-strict) — elapsed {int(time.time()-t_start)}s ===")
    for s in total_stats:
        print(f"  {s['doc_key']:<15} in_scope={s['in_scope_leaves']:>3} "
              f"verdicts={s['verdicts_total']:>3}  {s.get('verdicts_by_verdict', {})}")


if __name__ == "__main__":
    main()
