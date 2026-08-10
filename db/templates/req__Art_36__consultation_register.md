---
leaf_id: req:Art.36:consultation_register
control_ref: Art.36
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Prior Consultation Register

<<DOC_CONTROL>>

> Per-consultation record. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.36:consultation_register -->
<!-- column: item:Art.36:reg_consultation_id -->
<!-- column: item:Art.36:reg_dpia_xref -->
<!-- column: item:Art.36:reg_submission_date -->
<!-- column: item:Art.36:reg_sa -->
<!-- column: item:Art.36:reg_outcome -->
<!-- column: item:Art.36:reg_decision_to_proceed -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of each time you consult with data protection authorities, making it easier to demonstrate compliance with GDPR requirements.

## When to use it

Use this register whenever your activities require prior consultation under GDPR Article 36, and plan to review and update it about once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours for each consultation entry, as each required detail takes 10-15 minutes to complete; more consultations will increase the total time needed.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.36:consultation_register -->
| Reg Consultation Id | Reg Dpia Xref | Reg Submission Date | Reg Sa | Reg Outcome | Reg Decision To Proceed |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.36:consultation_register -->

## Column guidance — what to fill in

### Reg Consultation Id

<<MUST item:Art.36:reg_consultation_id>>
_Why: Audit_

> _Standard text:_ Per-row consultation id

<<GUIDANCE>>

### Reg Dpia Xref

<<MUST item:Art.36:reg_dpia_xref>>
_Why: Cross-article_

> _Standard text:_ Per-row DPIA cross-reference (Art.35 register entry)

<<GUIDANCE>>

### Reg Submission Date

<<MUST item:Art.36:reg_submission_date>>
_Why: Currency_

> _Standard text:_ Per-row submission date to SA

<<GUIDANCE>>

### Reg Sa

<<MUST item:Art.36:reg_sa>>
_Why: Art.55-56_

> _Standard text:_ Per-row supervisory authority engaged

<<GUIDANCE>>

### Reg Outcome

<<MUST item:Art.36:reg_outcome>>
_Why: Art.36.2_

> _Standard text:_ Per-row outcome (approved / approved-with-conditions / advised-against)

<<GUIDANCE>>

### Reg Decision To Proceed

<<MUST item:Art.36:reg_decision_to_proceed>>
_Why: Defensibility_

> _Standard text:_ Per-row controller decision after SA advice (proceed / modify / abandon)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Response Date

<<SHOULD item:Art.36:reg_response_date>>
_Why: Audit clarity_

> _Standard text:_ Per-row SA response date

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
