---
leaf_id: req:Art.10:criminal_data_processing_register
control_ref: Art.10
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Criminal Data Processing Register

<<DOC_CONTROL>>

> Per-activity register for every Art.10 processing operation — which Member State law applies, what safeguards, what retention. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.10:criminal_data_processing_register -->
<!-- column: item:Art.10:reg_activity_id -->
<!-- column: item:Art.10:reg_legal_basis -->
<!-- column: item:Art.10:reg_purpose -->
<!-- column: item:Art.10:reg_safeguards -->
<!-- column: item:Art.10:reg_approval -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of all activities involving the processing of criminal data, including which laws apply, what safeguards are in place, and how long you keep the data.

## When to use it

Use this register whenever you process criminal data under GDPR Article 10, especially if your activities are covered by specific Member State laws. Update it about once a year to stay compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours to complete the required sections for each processing activity, with additional time needed for each new activity you add.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.10:criminal_data_processing_register -->
| Reg Activity Id | Reg Legal Basis | Reg Purpose | Reg Safeguards | Reg Approval |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.10:criminal_data_processing_register -->

## Column guidance — what to fill in

### Reg Activity Id

<<MUST item:Art.10:reg_activity_id>>
_Why: Audit defensibility_

> _Standard text:_ Activity identifier per row (links to Art.30 RoPA)

<<GUIDANCE>>

### Reg Legal Basis

<<MUST item:Art.10:reg_legal_basis>>
_Why: Art.10_

> _Standard text:_ Per-row legal basis (official authority OR specific Member State law citation)

<<GUIDANCE>>

### Reg Purpose

<<MUST item:Art.10:reg_purpose>>
_Why: Art.10 — appropriate safeguards_

> _Standard text:_ Per-row purpose (must be narrow — pre-employment screening, sanctions check, regulatory KYC, fraud investigation)

<<GUIDANCE>>

### Reg Safeguards

<<MUST item:Art.10:reg_safeguards>>
_Why: Art.10_

> _Standard text:_ Per-row safeguards (retention limit, access restrictions, separate-system storage)

<<GUIDANCE>>

### Reg Approval

<<MUST item:Art.10:reg_approval>>
_Why: Accountability_

> _Standard text:_ Per-row approval signature + date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Ropa Xref

<<SHOULD item:Art.10:reg_ropa_xref>>
_Why: Cross-article coherence_

> _Standard text:_ Per-row cross-reference to Art.30 RoPA entry

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
