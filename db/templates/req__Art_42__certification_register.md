---
leaf_id: req:Art.42:certification_register
control_ref: Art.42
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Certification Register

<<DOC_CONTROL>>

> Per-certification record (active + past). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.42:certification_register -->
<!-- column: item:Art.42:reg_certification_id -->
<!-- column: item:Art.42:reg_scheme -->
<!-- column: item:Art.42:reg_scope -->
<!-- column: item:Art.42:reg_valid_until -->
<!-- column: item:Art.42:reg_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all your certifications, both current and past, in one place. It’s useful for tracking compliance and demonstrating your adherence to GDPR requirements.

## When to use it

Use this register when your organization’s activities or profile require you to document certifications, especially under GDPR Article 42. Plan to review and update it about once a year to keep information current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes to complete the required sections for each certification entry. The total time will increase if you have multiple certifications to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.42:certification_register -->
| Reg Certification Id | Reg Scheme | Reg Scope | Reg Valid Until | Reg Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.42:certification_register -->

## Column guidance — what to fill in

### Reg Certification Id

<<MUST item:Art.42:reg_certification_id>>
_Why: Audit_

> _Standard text:_ Per-row certification identifier

<<GUIDANCE>>

### Reg Scheme

<<MUST item:Art.42:reg_scheme>>
_Why: Art.42.5_

> _Standard text:_ Per-row scheme + Art.43 body

<<GUIDANCE>>

### Reg Scope

<<MUST item:Art.42:reg_scope>>
_Why: Art.42.7_

> _Standard text:_ Per-row processing scope covered

<<GUIDANCE>>

### Reg Valid Until

<<MUST item:Art.42:reg_valid_until>>
_Why: Art.42.7_

> _Standard text:_ Per-row validity end date (max 3 years from issue)

<<GUIDANCE>>

### Reg Status

<<MUST item:Art.42:reg_status>>
_Why: Lifecycle_

> _Standard text:_ Per-row status (active / under renewal / withdrawn)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Surveillance Dates

<<SHOULD item:Art.42:reg_surveillance_dates>>
_Why: Cadence_

> _Standard text:_ Per-row surveillance audit dates

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
