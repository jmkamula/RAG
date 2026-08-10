---
leaf_id: req:10.1:improvement_action_register
control_ref: 10.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 2
must_count: 7
should_count: 1
freshness_days: 365
table_shape: true
---

# Improvement Action Register

<<DOC_CONTROL>>

## What this template gives you

The **live ledger** where every improvement opportunity — audit
finding, monitoring gap, lessons-learned outcome, party feedback,
management-review decision — gets a row, an owner, and a target
date. Auditors trace findings IN (from 9.2/9.3) → register → closure
with effectiveness check. A clean register is the operating heartbeat
of a continually-improving ISMS.

## When to use it

Standing artefact required by **ISO/IEC 27001:2022 Clause 10.1**. This is a **register** (spreadsheet, ticketing-system view, or
table) not a one-off document — it's referenced constantly.

## Prerequisites

<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

**1-2 hours** to design the register structure for v1; **ongoing operational cost** of updating per finding.

---

<!-- TABLE-COLUMNS leaf:req:10.1:improvement_action_register -->
<!-- column: item:10.1:reg_action_id -->
<!-- column: item:10.1:reg_trigger_type -->
<!-- column: item:10.1:reg_dimension -->
<!-- column: item:10.1:reg_owner -->
<!-- column: item:10.1:reg_target_date -->
<!-- column: item:10.1:reg_status -->
<!-- column: item:10.1:reg_effectiveness -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per improvement action. Each column maps to a MUST item
the auditor will check — empty columns count as unsatisfied. Add as
many rows as you need.

<!-- EDIT-ZONE-START leaf:req:10.1:improvement_action_register -->
| Action ID | Trigger | Dimension | Owner | Target Date | Status | Effectiveness |
|---|---|---|---|---|---|---|
|           |         |           |       |             |        |               |
|           |         |           |       |             |        |               |
|           |         |           |       |             |        |               |
<!-- EDIT-ZONE-END leaf:req:10.1:improvement_action_register -->

## Column guidance — what to fill in

### Action ID

<<MUST item:10.1:reg_action_id>>

> _Standard text:_ Unique action identifier per row

Stable prefix + numeric sequence. Avoid recycling IDs after closure
— keep closed rows in the historical view with their IDs intact.

**✓ Good**: `AC-001`, `AC-117`, `AC-2026-042`

**✗ Avoid**: Free-text descriptions as IDs ("RBAC slip") — auditor
needs a stable handle to reference across status changes.

<<GUIDANCE>>

### Trigger

<<MUST item:10.1:reg_trigger_type>>

> _Standard text:_ Per-row trigger type (audit finding / measurement
> gap / opportunity / party feedback / mgmt review output)

Discrete value: `audit_finding`, `measurement_gap`,
`mgmt_review_decision`, `lessons_learned`, `party_feedback`,
`risk_treatment`, `opportunity`. Auditor pivots the register by
trigger to see flow rate from each source.

**✓ Good**: `audit_finding (Q1 internal)`, `lessons_learned (INC-042)`

**✗ Avoid**: Mixing the trigger value with the reasoning narrative —
keep this column to the discrete category.

<<GUIDANCE>>

### Dimension

<<MUST item:10.1:reg_dimension>>

> _Standard text:_ Per-row improvement dimension (suitability /
> adequacy / effectiveness)

ISO 27001 distinguishes three. **Suitability** (is the control right for the situation?). **Adequacy** (is it complete?). **Effectiveness**
(does it actually work?). Categorising helps the review process —
different remedies apply.

**✓ Good**: `effectiveness` (tighten cadence on existing control),
`adequacy` (control was incomplete), `suitability` (wrong control)

**✗ Avoid**: "Improvement" or "Fix" — both are not values from the
ISO triad.

<<GUIDANCE>>

### Owner

<<MUST item:10.1:reg_owner>>

> _Standard text:_ Per-row owner

Named individual or role with authority to deliver the action — not
"IT" or "the security team". Role-holder accountable for delivering
by target date. Re-assignment must be explicit (recorded in row
history).

**✓ Good**: `<<ISMS_MANAGER_NAME>>`, `VP Engineering`, `DPO`

**✗ Avoid**: "TBD" or unassigned — an action without an owner drifts.

<<GUIDANCE>>

### Target Date

<<MUST item:10.1:reg_target_date>>

> _Standard text:_ Per-row target completion date

Each row gets a target date. Slippage is OK — but it must be visible
(date moves with reason captured), not hidden. A slip beyond 60 days
should re-trigger management review approval.

**✓ Good**: `2026-09-30 (slipped from 2026-06-30: vendor dependency)`

**✗ Avoid**: "When possible" or "Q3" without a specific date.

<<GUIDANCE>>

### Status

<<MUST item:10.1:reg_status>>

> _Standard text:_ Per-row status (proposed / approved / in-progress /
> closed / superseded)

Discrete lifecycle: `proposed` → `approved` → `in_progress` → `closed`
/ `superseded` / `rejected`. Each transition records who + when in
the row history.

**✓ Good**: `in_progress`, `closed (2026-06-14)`, `superseded by AC-203`

**✗ Avoid**: Status that doesn't reset on slip — owner says "still
in progress" 18 months later without a refreshed target date.

<<GUIDANCE>>

### Effectiveness

<<MUST item:10.1:reg_effectiveness>>

> _Standard text:_ Per-row effectiveness assessment captured on
> closure (did the improvement work?)

When a row moves to `closed`, record **did it work?** — measurable
before/after, sample evidence, signoff. Without this, "closed" rows
are theatre.

**✓ Good**: `100% SBOM coverage (0/127 → 127/127), verified by SecOps
Manager 2026-06-15` — measurable outcome + verifier identity.

**✗ Avoid**: "Done" — no measurable evidence; auditor will reopen.

---

<<GUIDANCE>>

## Recommended additional columns

_These strengthen the register but aren't strictly required for the
MUST checks. Add them as extra columns in the table if they apply._

### Source Reference

<<SHOULD item:10.1:reg_source_xref>>

> _Standard text:_ Per-row source cross-reference (audit report ID /
> management-review minutes date / incident PIR doc)

Closes the loop: row points back to its originating finding /
decision / review. Auditor can navigate in either direction.

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
