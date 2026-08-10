---
leaf_id: req:Art.37:designation_record
control_ref: Art.37
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# DPO Designation Record

<<DOC_CONTROL>>

> Per-DPO designation record (most orgs have 1; group designations may have more). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.37:designation_record -->
<!-- column: item:Art.37:reg_dpo_identity -->
<!-- column: item:Art.37:reg_qualifications_evidence -->
<!-- column: item:Art.37:reg_designation_date -->
<!-- column: item:Art.37:reg_employment_type -->
<!-- column: item:Art.37:reg_publication_evidence -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of your Data Protection Officer (DPO) designation, making it easy to show compliance with GDPR requirements.

## When to use it

Use this template if your organization is required to appoint a DPO under GDPR, or if your business profile matches similar triggers. Plan to review and update it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on how many DPOs or group designations you need to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.37:designation_record -->
| Reg Dpo Identity | Reg Qualifications Evidence | Reg Designation Date | Reg Employment Type | Reg Publication Evidence |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.37:designation_record -->

## Column guidance — what to fill in

### Reg Dpo Identity

<<MUST item:Art.37:reg_dpo_identity>>
_Why: Authenticity_

> _Standard text:_ DPO identity per row

<<GUIDANCE>>

### Reg Qualifications Evidence

<<MUST item:Art.37:reg_qualifications_evidence>>
_Why: Art.37.5_

> _Standard text:_ Per-row qualifications evidence (CV / certifications / professional experience)

<<GUIDANCE>>

### Reg Designation Date

<<MUST item:Art.37:reg_designation_date>>
_Why: Currency_

> _Standard text:_ Per-row designation date

<<GUIDANCE>>

### Reg Employment Type

<<MUST item:Art.37:reg_employment_type>>
_Why: Art.37.6_

> _Standard text:_ Per-row employment type (internal staff / external service contract)

<<GUIDANCE>>

### Reg Publication Evidence

<<MUST item:Art.37:reg_publication_evidence>>
_Why: Art.37.7_

> _Standard text:_ Per-row publication evidence (privacy notice URL + SA notification confirmation)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Contract Link

<<SHOULD item:Art.37:reg_contract_link>>
_Why: Audit defensibility_

> _Standard text:_ Per-row link to employment / service contract document

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
