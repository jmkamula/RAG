---
name: workbook-yaml-vocab-refresh-2026-06-11
description: "SHIPPED 2026-06-11 (31366e1 + 78b8f27 + 4e6d1f1): full arc on 7.2/9.1/7.4 register-leaf coverage. F1 broadened YAML vocab (3 orphan sheets 0→16 findings). G1 dropped spurious coverage:partial flags (9.1 leaf 0/6→6/6 → NC→OFI). G2 downgraded 2 ChecklistItem MUSTs to SHOULDs (gap_actions + reg_sender) — 7.2 + 7.4 leaves became fully-satisfiable from register evidence alone, both flipped NC→OFI. Three end-to-end OFI flips in one session driven by workbook evidence."
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

## 2026-06-11 PM — G1 coverage-flag fix (78b8f27)

After the vocab broadening landed and the user approved 16
findings, posture for 7.2/7.4/9.1 stayed at NC despite all the
register evidence. Investigation revealed two compounding issues:

**1. Bulk-generator default was over-conservative.** All items in
`optional_columns` were given `coverage: partial`. The flag means
"column found but only weak/indirect evidence" — but for genuine
register columns (a real Owner column, a real Date column), the
column IS the evidence. The flag was actively wrong, not just
conservative.

**2. The engine drops partial findings.** `leaf_evaluators.py:177`
filters on `df.status = 'present'`. Items with
`status='partial'` (which is what `coverage: partial` produces
in the workbook persistence path) **don't reach `items_recognised`
at all** — the engine never sees them. So the YAML's spurious
partial flag was hiding evidence the workbook contained.

Removing the `coverage: partial` flag where the column genuinely
provides full evidence:

  - **9.1 measurement_record**: 0/6 → 6/6 recognised → leaf
    fully satisfied → engine flips 9.1 from NC → **OFI** as a
    Stage-2 proposal (live still NC until tenant approves the
    flip).
  - **7.2 competence_record**: 2/6 → 5/6 recognised; `gap_actions`
    genuinely missing in tenant's sheet (no Development Plan
    column). G2 candidate (should this MUST stay a MUST?).
  - **7.4 communication_event_register**: 2/6 → 5/6 recognised;
    `reg_sender` genuinely missing (sheet is a matrix not an
    event log). G2 candidate.

## Operational pattern: in-place finding-status correction

When a YAML-coverage fix changes how an item should be classified
*after* findings have already been approved, prefer:

  `UPDATE document_findings SET status='present', confidence='high'
   WHERE workbook_proposal_id IN (...) AND status='partial';`

over supersede-and-re-persist. The in-place update preserves the
tenant's existing approval (`review_status='approved'`, `reviewed_at`,
`reviewed_by`) — they already approved this evidence, we're just
correcting how the engine reads it.

Then call `load_posture(pg, tenant_id)` to recompute engine
verdicts and write new Stage-2 proposals.

## G1 lever (shipped) and G2 lever (shipped)

  - **G1 — YAML accounting fix.** Move bindings out of
    `optional_columns: coverage: partial` when the column
    actually provides full evidence. Mechanical, low-risk.
    SHIPPED 2026-06-11.
  - **G2 — curation review.** Audited whether items marked
    MUST_CONTAIN in the spec should remain mandatory:

      - `item:7.2:gap_actions` MUST → SHOULD. ISO 27001 7.2 c)
        is conditional ("where applicable, take actions to
        acquire the necessary competence"). Orgs commonly track
        gap actions in separate Development Plan docs. Kept as
        SHOULD so chat still surfaces it.
      - `item:7.4:reg_sender` MUST → SHOULD. No clause requires
        per-row sender. Matrix-shape registers (per-risk comms
        plan) can't naturally provide it — sender is implicit
        for the organisation. Log-shape registers still benefit.

    SHIPPED 2026-06-11 (4e6d1f1). Loader at
    `enrichment/documents/load_to_neo4j.py` pruned 2 stale
    MUST_CONTAIN edges cleanly via declarative sweep — no
    orphan ERs/items left. Engine sweep after the spec change
    saw 7.2 + 7.4 leaves fully satisfied → proposed OFI on
    both → tenant approved → live OFI.

## Three OFI flips in one arc

  - 9.1 NC → OFI (after G1 coverage-flag fix)
  - 7.2 NC → OFI (after G2 gap_actions downgrade)
  - 7.4 NC → OFI (after G2 reg_sender downgrade)

Same end-to-end shape for each: workbook → satisfied leaf
(via item-level checklist_item_id) → engine proposes OFI →
tenant approves Stage-2 → live posture flips. This was the
first time the full pipeline carried workbook intake through
to posture progression.

## Eval after the full arc

Eval 192/198 post-G2 — all 6 fails in the known-stochastic set
(#2, #16, #21, #24, #25, #26). No new failure shapes from the
spec change or the three live OFI flips. Three flipped controls
are ISMS clauses (7.2 / 7.4 / 9.1); the eval suite's NC-focused
cases are largely on Annex A controls and unaffected.

## Principle

**Reserve `coverage: partial` for genuinely weak signals — not
as a default for non-required columns.** Bulk-generator should
treat absence-of-required as "missing" and presence-of-mapped
as "full coverage" unless the column type is inherently
ambiguous (a free-text "Notes" column, an undated "Status"
column where no semantics are enforced, etc).

## Related

- [[workbook-intake-corpus-v1-complete]] — the original corpus.
  This refresh narrows the vocab gap surfaced by real tenant data.
- [[feedback-workbook-yamls-semantic-class]] — the principle as a
  reusable rule for future YAML authoring.
