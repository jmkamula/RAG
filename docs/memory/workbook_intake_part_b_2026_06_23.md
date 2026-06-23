---
name: workbook-intake-part-b-2026-06-23
description: "SHIPPED 2026-06-23 (9743e11): Part B closes the workbook-intake curation gap. 4 new workbook_mappings YAMLs for sheets Part A's classifier flagged as unmapped (Spec Int Engagement → A.5.6; BIA → A.5.30; Quarterly Security Review → A.5.36; ISMS Schedule → 10.1) + meta-skip extended with 'change control' patterns. 100% sheet coverage on Arion's workbook; 197 bound findings vs 169 pre-Part-B."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

Part A retired `_extract_structured` for xlsx/xlsm. Sheets without
YAMLs produced 0 findings + a telemetry signal listing the gap.
Part B authors the missing YAMLs to close the gap.

The classifier (Part A, `_classify_workbook_sheets`) had flagged 5
unmapped sheets on Arion's 2026-06-23 workbook:

| Sheet | Resolution |
|---|---|
| Spec Int Engagement log | **YAML → A.5.6 contact_register** |
| BIA Bus. Impact Ass. | **YAML → A.5.30 ict_service_register** |
| Quarterly Security Review | **YAML → A.5.36 compliance_review_record** |
| ISMS Schedule | **YAML → 10.1 improvement_action_register** |
| This Doc Chng Control | **Meta-skip** (workbook self-changelog, doesn't fit any MUST leaf) |

## The 4 YAMLs

### `special_interest_group_register.yaml` → A.5.6

Per-group engagement record. Direct fit — A.5.6 contact_register
MUSTs (sigs_listed / owner / topics_shared / basis_of_contact /
last_engaged) map cleanly to Group Name / Assigned To / Focus Area /
Engagement Type / Last Review Date columns.

### `bia_ict_service_register.yaml` → A.5.30

Business Impact Assessment per asset. CIA + RTO/RPO + criticality
columns feed ict_service_register MUSTs (reg_service_id /
reg_recovery_owner / reg_criticality / reg_rto_rpo /
reg_dependencies). Cross-links to A.5.9 (asset register overlap)
and 6.1.2 (risk assessment input).

### `quarterly_compliance_review_record.yaml` → A.5.36

Per-quarter scope-by-scope review log. Columns map cleanly to
compliance_review_record MUSTs (review_date / owner / scope /
findings / corrective_actions / method / schedule). Freshness set
to 120 days (quarterly cadence). YAML tolerates the workbook's
typo "Remidiation" via alternative_fingerprints.

### `isms_schedule_improvement_register.yaml` → 10.1

ISMS task tracker (REF ID / TASK / OWNER / DUE DATE / STATUS).
Maps to improvement_action_register MUSTs. Cross-links to 9.2 for
AUD* tasks — row-filter-by-prefix not yet supported in the YAML
schema, so audit-shaped rows feed the improvement register
broadly rather than the audit programme specifically.

## Meta-skip extension

The "This Doc Chng Control" sheet is the workbook's own change log
(rows 0-12 = DOC005 self-meta; rows 15+ = change events on the
workbook itself). Genuine evidence of doc-change-control practice
but the evidence shape doesn't match any MUST leaf cleanly.

Added patterns: `doc chng control` / `this doc chng` / `change
control` / `doc change control` / `doc change log`. Catches similar
self-metadata sheets in other tenants' workbooks too.

## Verification

Arion workbook re-extract via re-extract endpoint:

```
Before Part B: 38 proposals + 169 findings  (5 sheets unmapped)
After Part B:  43 proposals + 197 findings  (0 sheets unmapped)

Lift: +5 proposals, +28 findings
trace_log:
  workbook_sheets_total: 32
  workbook_sheets_mapped: 32
  workbook_sheets_unmapped: 0
  workbook_skipped_meta_sheets: TOC, Documentation, Mapping,
    This Doc Chng Control, Instructions and Definitions, Formulas
```

## Effort actually spent

~1.5 hours. Significantly less than the 8-10 hr estimate in the
Part A memory. Reasons:
- The classifier output gave precise leaf-target hints (no Neo4j
  exploration needed beyond a quick query for MUST ids)
- The YAML schema is well-established — copy/paste from
  audit_execution_log.yaml + adapt
- 4 YAMLs share a common shape (register or review_record); not
  4 distinct designs
- Sheet evidence inspection (column headers + sample rows) gave
  unambiguous binding decisions in most cases

This suggests the per-workbook-shape onboarding cost is lower than
estimated. Future tenants with similar sheet shapes: 0 incremental
YAML authoring (the 4 new YAMLs are shared). Tenants with novel
shapes: ~1.5-2 hr per genuinely-new sheet shape.

## Architectural significance

Part A + Part B together complete the workbook intake redesign:
- Single canonical writer (workbook_persistence)
- YAML-driven deterministic per-MUST binding
- Meta-sheet blacklist filters self-metadata
- Sheet classifier surfaces curation gap
- 100% bind rate achievable on any workbook shape with YAMLs

Symmetry with doc intake (post Direction C) is established:
- Doc pattern: doc_mappings → LLM extract with per-MUST candidates
  + Direction C pass-2
- Workbook pattern: workbook_mappings → deterministic YAML extract
  per row per MUST

Both paths now have YAML as the contract. Telemetry signals the
gap in both directions. Curation extends both deterministically.

## What's still deferred

- **Headline-recompute API response confusion**: approve endpoint
  still returns legacy recommendations vs actual engine effect
- **Dashboard latest-trace fix**: shows worst-case trace per
  upload_id instead of latest
- **CSV workbook intake**: `_extract_structured` still runs for
  CSV files (workbook_persistence doesn't support single-table CSVs)

Each is its own small follow-up; none are MVP-blocking.

## Related

- [[workbook-intake-part-a-2026-06-23]] — the architectural setup
  that enabled this curation work
- [[workbook-importer-bare-annex-a-2026-06-23]] — original gap
  that started the whole arc (RESOLVED by Part A; this entry
  completes the closure)
- [[per-must-recall-direction-c-2026-06-23]] — sibling doc-side
  YAML pattern (doc_mappings)
- [[strategic-arc-2026-06-23]] — arc capstone
