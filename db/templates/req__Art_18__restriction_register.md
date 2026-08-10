---
leaf_id: req:Art.18:restriction_register
control_ref: Art.18
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Restriction Register

<<DOC_CONTROL>>

> Per-restriction record proving active restrictions are in place with documented grounds. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.18:restriction_register -->
<!-- column: item:Art.18:reg_subject_id -->
<!-- column: item:Art.18:reg_ground -->
<!-- column: item:Art.18:reg_scope -->
<!-- column: item:Art.18:reg_start_date -->
<!-- column: item:Art.18:reg_lift_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of any restrictions you have placed on personal data, along with the reasons for each restriction. It supports your ability to demonstrate compliance with GDPR requirements.

## When to use it

Use this register whenever you need to document restrictions on personal data in your environment. Review and update it about once a year to ensure the information stays current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes to complete the required sections for each restriction you need to record, with additional time if you have multiple restrictions to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.18:restriction_register -->
| Reg Subject Id | Reg Ground | Reg Scope | Reg Start Date | Reg Lift Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.18:restriction_register -->

## Column guidance — what to fill in

### Reg Subject Id

<<MUST item:Art.18:reg_subject_id>>
_Why: Audit_

> _Standard text:_ Subject identifier per row

<<GUIDANCE>>

### Reg Ground

<<MUST item:Art.18:reg_ground>>
_Why: Art.18.1_

> _Standard text:_ Per-row Art.18.1 ground (a-d) cited

<<GUIDANCE>>

### Reg Scope

<<MUST item:Art.18:reg_scope>>
_Why: Implementation_

> _Standard text:_ Per-row scope (which data, which systems are restricted)

<<GUIDANCE>>

### Reg Start Date

<<MUST item:Art.18:reg_start_date>>
_Why: Currency_

> _Standard text:_ Per-row restriction start date

<<GUIDANCE>>

### Reg Lift Status

<<MUST item:Art.18:reg_lift_status>>
_Why: Art.18.3_

> _Standard text:_ Per-row lift status (active / lifted-on-date with reason)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Art19 Xref

<<SHOULD item:Art.18:reg_art19_xref>>
_Why: Cross-article coherence_

> _Standard text:_ Per-row Art.19 notification reference

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
