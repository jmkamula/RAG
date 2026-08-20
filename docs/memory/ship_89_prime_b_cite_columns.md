---
name: ship-89-prime-b-cite-columns
description: Ship 89'.b — cite_columns YAML field routes workbook hyperlinks into Ship 3' external_evidence_source cite-mode; replaces uncommitted Ship 88 approach
metadata:
  type: project
---

# Ship 89'.b — cite_columns YAML field + cite-mode integration (2026-08-20)

## Framing

Ship 88 (uncommitted) tried to route workbook hyperlinks through a
new `workbook_hyperlink_followup` sibling table, forcing findings to
`partial` with a fabricated `has_hyperlink` corroborating signal.
User pointback: `partial` already means something (YAML's
required/optional discipline — Ship 87'.a discovery, Ship 89'.a
codified in the curator). Hyperlinks should follow the **cited**
routine (Ship 3' `external_evidence_source`), not a parallel
follow-up universe.

Ship 89'.b delivers the cite-mode integration.

## Delivered

**Schema.** `schema_v102_workbook_cite_columns.sql`:
- Adds nullable `external_evidence_source.origin_finding_id` FK to
  `document_findings`. Attribution: "which workbook row cited
  this?" answers via this column.
- `ON DELETE SET NULL` — if the workbook finding is soft-deleted,
  the cite survives (evidence provenance ≠ evidence lifecycle).

**YAML schema.** New declarative `cite_columns:` block alongside
`required_columns` / `optional_columns`:
```yaml
cite_columns:
  - fingerprint: [linked, policies]
    binds_to: "item:6.1.3:soa_reference"
    alternative_fingerprints:
      - [linked, processes]
      - [reference]
    cite_kind: internal_document
    verification_days: 365
```

Fields:
- `fingerprint` + `alternative_fingerprints` — matches column headers
  (same tokenizer as required/optional)
- `binds_to` — MUST id the cite corroborates
- `cite_kind` — `internal_document` | `url` | `external_system`
- `verification_days` — inherits Ship 3' cadence discipline
- `system_hint` (optional) — override for `tenant_external_system.system_name`

**Discovery.** `PassProposal.cite_bindings: dict[str, dict]` — MUST id
→ {header, cite_kind, verification_days, system_hint}. `evaluate_pass`
scans `cite_columns:` and populates this per pass.

**Persistence.** `workbook_persistence.persist_proposals`:
- Returns `finding_id` via `RETURNING id` on document_findings INSERT
- Tracks `finding_id_by_must` per pass so cite emission can attribute
- For each MUST in `pp.cite_bindings`:
  - `_ensure_external_system(cur, tenant, cite_meta)` — find-or-create
    `tenant_external_system` row (idempotent per (tenant, name))
  - `_upsert_cite(...)` — INSERT-or-UPDATE `external_evidence_source`
    row for (tenant, must_id, system_id). The table's UNIQUE
    constraint collapses N cells → 1 cite by construction.

**Engine posture: unchanged.** Workbook finding keeps its YAML-declared
status (present/partial per anchor/corroboration rule). Cite emission
is auditor-visibility only — matches the stored-vs-cited product
principle: cited mode is provenance, stored mode is evidence.

**Ship 88 fully reverted.** No workbook_hyperlink_followup table, no
has_hyperlink corroborating signal, no workbook_link_resolver sweep,
no workbook_link_unresolved notification kind. DB residue cleaned
(213 notifications + 4 sweep_log rows + 9 has_hyperlink signal
values). tenant_notification.kind_check + sweep_log.work_type_check
allowlists restored to pre-Ship-88 shape.

## Row-level HL guard (added mid-arc)

User caught a semantic gap: initial emission fired on **header
presence alone**, so an empty column or a mailto-only column would
still produce a cite. Added `_column_has_real_cite_hyperlink()` in
`workbook_discovery.py` — emission gated on ≥1 hyperlink cell in
the matched column on a data row (row > header_row) AND URL is not
`mailto:`. When `sheet_hyperlinks` is None (unit-test path), the
guard is bypassed for backwards compat.

Threaded through: `doc_pipeline` reads
`doc.extraction_metrics["structured_sheets"]` (Ship 85'.a) →
`discover_workbook(hyperlinks_per_sheet=...)` →
`discover_sheet(sheet_hyperlinks=...)` →
`evaluate_pass(sheet_hyperlinks=..., header_row=...)`.

## Dogfood measurement (full ISO workbook scope)

Added `cite_columns:` blocks to 5 mappings covering all real cite
sheets on the ISO workbook (Access Register PII was legitimately
skipped — 22 mailto-only hyperlinks are owner contacts, not cites):

| Sheet | Hyperlinks | Kind | MUST bound |
|---|---|---|---|
| Statement of Applicability | 149 | relative + http | `item:6.1.3:soa_reference` |
| ISMS Schedule | 43 | http | `item:10.1:reg_trigger_type` |
| Legal & Regul. Compl. Register | 23 (10 mailto + 13 http) | mixed | `item:A.5.31:rev_scope_check` |
| Training & Awarnesse Record | 7 | relative | `item:A.6.3:rev_register_update` |
| Spec Int Engagement log | 6 | http | `item:A.5.6:sigs_listed` |
| Access Register PII Systems | 22 (mailto only) | filtered → skip | — |

Re-extraction on ISO workbook (upload `ebf724de-0629`):

| Signal | Value |
|---|---|
| Total hyperlinks captured (Ship 85'.a) | 250 |
| **external_evidence_source rows emitted** | **5** |
| `origin_finding_id` populated | 5/5 (100% attribution) |
| `tenant_external_system` rows auto-created | 2 (`Internal Documents`, `External URLs`) |
| Access Register mailto-only rows filtered | 22 → 0 cites (guard works) |
| Workbook finding statuses | unchanged from YAML declared |
| Fabricated corroborating_signals | 0 |

The 250→5 collapse is the correct auditor lens: each sheet cites at
most one system per MUST. Per-cell storage was Ship 88's mistake.
The row-level guard ensures we count only real cites — a "Policy
Link" column full of empty cells produces zero cites.

## Unit tests

`tests/test_workbook_cite_columns.py` — 16 assertions across 6 test
functions:
- `evaluate_pass` captures cite_bindings from YAML block
- No binding emitted when column header doesn't match
- Default `cite_kind` = `internal_document`
- **Row-level guard**: empty / header-only / mailto-only / wrong-column
  hyperlinks all produce zero cites; real cite URL emits;
  mixed mailto+http still emits (real cite wins)
- Guard bypassed when `sheet_hyperlinks=None` (unit-test path)
- `_ensure_external_system` idempotent per (tenant, name)

Test #6 is optional (DB-live) — skips when POSTGRES_PASSWORD unset.

## Codified lessons

**Lesson 96: Reuse the destination model, not the mechanism.**
Ship 88 built a workbook-side follow-up mechanism (sweep + resolver
+ notification kind) parallel to Ship 3' cite-mode. The AUDITOR
already has one lens for "we cite external evidence" — cite-mode.
Ship 89'.b delivers the same tenant-facing outcome via the existing
model, adding one FK column instead of a new table + sweep +
notification kind. **When two features look mechanically similar,
consolidate the model before duplicating the mechanism.**

**Lesson 97: UNIQUE constraints encode auditor semantics.**
`external_evidence_source UNIQUE(tenant_id, must_id, system_id)`
is not "we can't have duplicate rows" — it's the auditor lens
"one MUST cites at most one system per tenant." That constraint
collapsed 149 SoA hyperlinks into 1 cite exactly as an auditor would
count them. **Read schema constraints as domain rules, not
optimization artifacts.**

**Lesson 98: cite-mode ≠ engine input.**
Ship 88's auto-promote (`partial → present` on linked-doc verified)
conflated stored-evidence semantics with cite-mode provenance. User
called this out: cite is auditor-visibility only, does not gate
engine posture. Workbook finding's YAML-declared status is what the
engine sees. **Preserve the stored/cited separation at every layer
— posture, notifications, UI.**

**Lesson 99: Header presence is not evidence of citation.**
Initial cite emission fired on column header match alone. User
caught the gap: an empty column or a mailto-only column shouldn't
count as a cite. Row-level guard added mid-arc:
`_column_has_real_cite_hyperlink()` requires ≥1 non-mailto
hyperlink on a data row in the matched column. This connects the
Ship 85'.a hyperlink capture (which had no downstream consumer
until Ship 89'.b) to a real semantic use — hyperlinks now signal
"there IS a cite here." **Reader capture becomes downstream signal
when the downstream code asks the right question — "is this
column real?" rather than "does this column exist?"**

## Files changed

- `db/schema_v102_workbook_cite_columns.sql` (new, replaces reverted
  Ship 88 v102)
- `db/workbook_mappings/statement_of_applicability.yaml` — added
  `cite_columns:` block (dogfood file)
- `rag/intake/workbook_discovery.py` — `PassProposal.cite_bindings`
  field + cite_columns scan in `evaluate_pass`
- `rag/intake/workbook_persistence.py` — cite emission wired into
  `persist_proposals` + new `_ensure_external_system`,
  `_upsert_cite` helpers
- `tests/test_workbook_cite_columns.py` (new, 9 assertions)
- `docs/memory/ship_89_prime_b_cite_columns.md` (this)

## Ship 88 revert (all uncommitted)

- Deleted `db/schema_v102_workbook_hyperlink_followup.sql`
- Deleted `docs/memory/ship_88_prime_arc_retrospective.md`
- Deleted `tests/test_workbook_hyperlinks.py`
- Reverted `rag/intake/doc_pipeline.py`,
  `rag/intake/workbook_discovery.py`,
  `rag/intake/workbook_persistence.py`,
  `rag/scheduler/tick.py` to pre-Ship-88 state
- Dropped `workbook_hyperlink_followup` table
- Deleted 213 `workbook_link_unresolved` notifications + 4 sweep_log rows
- Removed `has_hyperlink` from 9 `document_findings.corroborating_signals`
- Restored `tenant_notification.kind_check` + `sweep_log.work_type_check`
  allowlists to pre-Ship-88 shape

## Deferred to future arcs

- **Ship 90.a**: LLM curator sweep to add `cite_columns:` blocks to
  the ~50 register-shape mappings likely to have citation columns
  (Policy Link, Evidence Link, Doc Ref, Supporting Document). Same
  discipline as Ship 89'.a — curator now knows about the third
  column list.
- **Ship 90.b (optional)**: rule-based backfill script scanning all
  240 YAMLs for cite-shape column fingerprints.
- **Ship 90.c**: auto-verification — when a client_document uploaded
  on this tenant matches the cited URL/filename AND has present
  findings on the same MUST, write an
  `external_evidence_verification_log` row with
  `verification_type='auto_matched'`. Existing Ship 3'
  cadence-driven notifications take over.
- The 8 anti-pattern files with `partial` on `required_columns`
  (from Ship 89'.a audit) — curator sweep to reclassify.

## Related

- [[ship-89-prime-a-curator-fix]] — Ship 86 curator schema + corroboration fix (prerequisite)
- [[curation-phase-b-retrospective]] — YAML catalog history
- Ship 3'-arc cite-mode: `external_evidence_source`, `verification_log`,
  `cite_verification_overdue` — the plumbing Ship 89'.b integrates with
