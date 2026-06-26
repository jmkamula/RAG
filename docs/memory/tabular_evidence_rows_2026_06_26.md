---
name: tabular-evidence-rows-2026-06-26
description: "SHIPPED 2026-06-26: schema_v47 tabular_evidence_rows sibling table captures multi-row content from tabular EDIT-ZONE uploads. Closes a real evidence-under-discovery gap — extractor's first-non-empty-per-column logic was throwing away N-1 rows of register content (50-row asset register collapsed to 1 row of stored data). Phase 1: capture (extractor + writer + schema) + replay (renderer prefill). Phase 2 deferred: per-row completeness advisory + posture surface enrichment."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## The gap discovered today

`_extract_templated_via_table` in `rag/intake/extractor.py` had this
loop:

    for i in range(min(len(cells), len(columns))):
        if cells[i] and not col_has_data[i]:   # ← stops at first non-empty
            col_has_data[i] = True
            sample_cell[i]  = cells[i]

The extractor's job had two conflated goals on one data path:
**satisfaction check** (does column X have any data, yes/no) +
**content capture** (preserve what the tenant typed). The first
non-empty cell answered satisfaction; everything else was thrown
away. A 50-row asset register stored 1 row's worth of data
(6 findings — one per column with `evidence_text` = the first
non-empty cell of that column).

User caught it: "we want to present real compliance findings, it
seems our extraction has gaps that potentially miss evidence."

## What's NOT fixed by Phase 1

This gap is **one class** of evidence under-discovery. Others remain
their own workstreams:

- LLM missing clauses in narrative `.docx` (`_llm_extract`)
- LLM hallucinating un-grounded evidence (grounding rules)
- Workbook coverage (`workbook_persistence` matchers)
- PDF table parsing
- Image-only docs (no OCR)
- Cross-framework xfw bridges not surfacing
- Form-lane MUSTs tenant skipped

Phase 1 fixes ONLY the templated-tabular multi-row case. It's
necessary-but-not-sufficient. Likely next-biggest contributor:
LLM-narrative under-discovery (`_llm_extract` over `.docx`).

## Architecture — sibling table, not extension

Chose `tabular_evidence_rows (tenant_id, document_id, leaf_id,
row_index, column_values JSONB, is_active)` as a **sibling** to
`document_findings`, not an extension.

**Why**:
- Engine semantics untouched. `document_findings` keeps its
  one-finding-per-MUST shape; engine still asks "is column X
  satisfied?" and gets a yes/no.
- Two concerns live in two places: findings = "did the tenant
  satisfy these MUSTs?", tabular_evidence_rows = "what did the
  tenant literally type, row by row?".
- Cheap to roll back if the design doesn't work — drop the table,
  nothing else moves.
- Sparse JSONB `column_values = {item_id: cell_text}` is
  presence-of-key for completeness — empty cells omitted entirely.

**Supersession**: same discipline as document_findings — re-extract
flips `is_active=FALSE` on prior rows for that `document_id` before
inserting the new batch. Renderer reads only `is_active = TRUE` so
the "most recent" view is automatic.

## How to apply (Phase 2 work)

When wiring per-row advisory:

1. Read `tabular_evidence_rows` for the tenant + leaf.
2. For each item_id in TABLE-COLUMNS metadata, compute fill rate:
   `count(rows where column_values ? item_id) / count(rows)`.
3. Surface: "47 assets, 3 missing owner (rows 12, 19, 34)" — the
   row_index is auditor-friendly.
4. Engine: still uses `document_findings` for the binary verdict.
   Advisory is overlay, not engine surface.

Smoke (`/tmp/smoke_table_prefill.py`): upload 5 rows → extract
captures 5 (verified) → persist → re-render → 5 rows replayed
verbatim with header + separator preserved.

## Related

- [[templates-v2-anchors-complete-2026-06-25]] — the 6 tabular v2
  anchors whose multi-row content this captures.
- [[templated-lane-discipline-2026-06-25]] — the auto-approve
  discipline. Tabular rows inherit the same "tenant-authored, no
  inference" trust.
- [[form-lane-parity-2026-06-26]] — sibling tenant-authored lane.
  Phase 2 advisory should treat form + templated + tabular as one
  population.
- [[feedback-telemetry-before-trouble]] — `extraction_metrics
  ["templated_tabular_rows_captured"]` added so under-discovery
  is now observable. Don't repeat the "one-finding-per-column =
  satisfied" silent loss.
