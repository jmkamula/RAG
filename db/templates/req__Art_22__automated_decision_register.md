---
leaf_id: req:Art.22:automated_decision_register
control_ref: Art.22
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Automated Decision-Making Register

<<DOC_CONTROL>>

> Per-decision-system record (NOT per individual decision) for every solely-automated decision system in scope. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.22:automated_decision_register -->
<!-- column: item:Art.22:reg_system_id -->
<!-- column: item:Art.22:reg_decisions_made -->
<!-- column: item:Art.22:reg_art22_2_basis -->
<!-- column: item:Art.22:reg_safeguards -->
<!-- column: item:Art.22:reg_dpia_link -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every system you use that makes decisions automatically, without human involvement. It supports your compliance with GDPR requirements for automated decision-making.

## When to use it

Use this register whenever you have a system that makes decisions entirely on its own, and update it about once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50–75 minutes to complete the required sections for each automated decision system you have, with additional time needed for each system you add.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.22:automated_decision_register -->
| Reg System Id | Reg Decisions Made | Reg Art22 2 Basis | Reg Safeguards | Reg Dpia Link |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.22:automated_decision_register -->

## Column guidance — what to fill in

### Reg System Id

<<MUST item:Art.22:reg_system_id>>
_Why: Audit defensibility_

> _Standard text:_ System / model identifier per row

<<GUIDANCE>>

### Reg Decisions Made

<<MUST item:Art.22:reg_decisions_made>>
_Why: Defining scope_

> _Standard text:_ Decision categories made (loan approval, employment screening, pricing, etc.)

<<GUIDANCE>>

### Reg Art22 2 Basis

<<MUST item:Art.22:reg_art22_2_basis>>
_Why: Art.22.2_

> _Standard text:_ Art.22.2 basis cited per row (contract / MS law / explicit consent)

<<GUIDANCE>>

### Reg Safeguards

<<MUST item:Art.22:reg_safeguards>>
_Why: Art.22.3_

> _Standard text:_ Per-row Art.22.3 safeguards in place (human intervention queue, contest UI, model explanation)

<<GUIDANCE>>

### Reg Dpia Link

<<MUST item:Art.22:reg_dpia_link>>
_Why: Art.35.3.a_

> _Standard text:_ Per-row DPIA reference (Art.35 nearly always triggered for Art.22)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Objection Count

<<SHOULD item:Art.22:reg_objection_count>>
_Why: Operational visibility_

> _Standard text:_ Per-row objection count (Art.22-related rights requests this period)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
