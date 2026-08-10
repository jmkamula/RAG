---
leaf_id: req:Art.38:position_evidence_register
control_ref: Art.38
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# DPO Position Evidence Register

<<DOC_CONTROL>>

> Per-period record of position-guarantee evidence (board attendance, budget approval, independence demonstrations). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.38:position_evidence_register -->
<!-- column: item:Art.38:reg_period -->
<!-- column: item:Art.38:reg_board_attendance -->
<!-- column: item:Art.38:reg_budget_approval -->
<!-- column: item:Art.38:reg_independence_signal -->
<!-- column: item:Art.38:reg_coi_attestation -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record showing your Data Protection Officer’s role is properly supported and independent, as required under GDPR. It’s useful for demonstrating compliance during audits or reviews.

## When to use it

Use this register if your organization is required to appoint a Data Protection Officer under GDPR. Update it about once a year, or whenever there are changes to your DPO’s position or supporting evidence.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this register from scratch, depending on how easily you can gather the necessary evidence for each required element.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.38:position_evidence_register -->
| Reg Period | Reg Board Attendance | Reg Budget Approval | Reg Independence Signal | Reg Coi Attestation |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.38:position_evidence_register -->

## Column guidance — what to fill in

### Reg Period

<<MUST item:Art.38:reg_period>>
_Why: Cadence_

> _Standard text:_ Per-row reporting period (typically quarterly)

<<GUIDANCE>>

### Reg Board Attendance

<<MUST item:Art.38:reg_board_attendance>>
_Why: Art.38.3 — reporting line_

> _Standard text:_ Per-row board / management forum attendance evidence

<<GUIDANCE>>

### Reg Budget Approval

<<MUST item:Art.38:reg_budget_approval>>
_Why: Art.38.2_

> _Standard text:_ Per-row budget approval / spend evidence (Art.38.2 resources)

<<GUIDANCE>>

### Reg Independence Signal

<<MUST item:Art.38:reg_independence_signal>>
_Why: Art.38.3_

> _Standard text:_ Per-row independence signals (no overruled DPO opinion; if overruled, formal record + escalation)

<<GUIDANCE>>

### Reg Coi Attestation

<<MUST item:Art.38:reg_coi_attestation>>
_Why: Art.38.6_

> _Standard text:_ Per-row conflict-of-interest re-attestation (Art.38.6)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Training

<<SHOULD item:Art.38:reg_training>>
_Why: Cross-article_

> _Standard text:_ Per-row training / development hours (sustains expertise per Art.37.5)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
