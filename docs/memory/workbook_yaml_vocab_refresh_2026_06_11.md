---
name: workbook-yaml-vocab-refresh-2026-06-11
description: "SHIPPED 2026-06-11 (31366e1): three workbook_mappings YAMLs (7.2/9.1/7.4) had narrow standard-jargon fingerprints. Broadened to semantic-class vocabulary. Arion's 3 orphan sheets ('Competence Records', 'Monitoring Log', 'Risk Comms Matrix') went from 0 → 16 findings (6 satisfied + 10 partial)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Follow-up to [[workbook-intake-corpus-v1-complete]]: among the 38
Arion workbook sheets, 6 had matched a YAML mapping at discovery
time but produced ZERO `document_findings` rows. Root cause:
`matched_columns: {}` — the YAML recognised the sheet by name but
couldn't match any DATA columns to MUST items. The bulk-generated
Tier-3 YAMLs used standard-jargon vocabulary (`[required,
competence]`, `[event, id]`, `[metric, id]`) that tenants rarely
type verbatim.

## Three YAMLs refreshed

  - `iso27001_2022_7_2_competence_record.yaml` — broadened to
    accept competence/competency/skill/training/qualification/
    certification/education/experience as the basis dimension.
  - `iso27001_2022_9_1_measurement_record.yaml` — broadened to
    accept metric/measurement/KPI/indicator as the id dimension;
    value/result/actual/reading as the value; target/threshold/
    benchmark/criteria as the threshold.
  - `iso27001_2022_7_4_communication_event_register.yaml` —
    broadened to accept event/communication/risk/item as the id
    dimension; topic/subject/message/risk-description as the
    "what is being communicated"; audience/recipient/interested-
    party/stakeholder as audience; channel/method/medium as
    channel.

## The general principle

Fingerprints should match the **semantic class** of column any
tenant would use for that evidence type — not a tenant-specific
phrase. Arion is just the validation case. Other tenants will
call the same column "Skill" or "Person" or "KPI Code" or "Stake-
holder". The YAML's job is to recognise the *role* the column
plays in the register, not to memorise one wording.

Implementation: multiple fingerprints binding to the same
`item:X.Y:id` is the pattern. The matcher (subset_match in
workbook_discovery) picks any one that matches; the others act
as alternates.

## Supersedure of stale proposals

When refreshing YAMLs that had previously produced 0-finding
"orphan" proposals, mark the old proposals as `status='superseded'`
with `superseded_at=NOW()` and a `decision_note` before running
persist_proposals again. Otherwise Stage-1 shows two pending
proposals for the same sheet (one with `matched_columns: {}`, one
real). Constraint `workbook_intake_proposal_status_check` allows
only {'pending', 'superseded'}; `superseded_consistency` requires
`superseded_at IS NOT NULL` when status='superseded'.

The discover_workbook.py CLI does NOT do this supersedure
automatically. Manual SQL UPDATE is required for now (one-off cost,
acceptable for the rare YAML-refresh path).

## Verification on Arion

After refresh + re-persist:

| sheet | proposal_id | findings (high + partial) |
|---|---|---|
| Competence Records (7.2) | 55 | 2 + 3 |
| Monitoring Log (9.1) | 53 | 2 + 4 |
| Risk Comms Matrix (7.4) | 54 | 2 + 3 |

All 16 in `review_status='pending'` for tenant Stage-1 approval.
Eval 192/198 — known-stochastic only, no regressions. The chat
eval doesn't exercise workbook intake directly, so the workbook
YAMLs being isolated from chat behaviour is expected.

## 3 remaining orphan sheets (deferred)

  - **Business Partners Assessment** — sheet has narrative header
    (purpose / scope / frequency) on rows 1-5; actual tabular
    data starts below. header_row_hints don't reach deep enough.
  - **Internal&External Parties** — semantically a 4.2 interested-
    parties matrix, not the 4.1 issues register the YAML targets.
    Sheet has Category column with Internal/External as ROW values,
    not separate columns. Already-covered by "Interested Parties"
    sheet → 4.2 mapping (no value-add to bind to 4.1).
  - **This Doc Chng Control** — front-matter sign-off block (Title/
    Owner/Date), not a change-log per se. May be no-op evidence.

These are F2 candidates; structural mismatches, not vocab gaps.

## Related

- [[workbook-intake-corpus-v1-complete]] — the original corpus.
  This refresh narrows the vocab gap surfaced by real tenant data.
- [[feedback-workbook-yamls-semantic-class]] — the principle as a
  reusable rule for future YAML authoring.
