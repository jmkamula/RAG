---
leaf_id: req:A.8.11:masking_register
control_ref: A.8.11
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Per-Dataset Masking Register

<<DOC_CONTROL>>

> Per-dataset application of masking — which production datasets feed which non-production environments via what technique, when last refreshed

<!-- TABLE-COLUMNS leaf:req:A.8.11:masking_register -->
<!-- column: item:A.8.11:reg_dataset -->
<!-- column: item:A.8.11:reg_target_env -->
<!-- column: item:A.8.11:reg_technique -->
<!-- column: item:A.8.11:reg_pii_classes -->
<!-- column: item:A.8.11:reg_last_refreshed -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you track which production datasets are shared with non-production environments, how they are masked, and when they were last updated. It's useful for maintaining clear records and supporting compliance with data protection standards.

## When to use it

Use this register whenever your environment handles production data that is copied or shared with non-production systems. Update it as needed whenever datasets, masking techniques, or refresh dates change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per dataset entry, with additional time for each required detail. Completing the register from scratch may take 1-2 hours depending on the number of datasets you manage.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.11:masking_register -->
| Reg Dataset | Reg Target Env | Reg Technique | Reg Pii Classes | Reg Last Refreshed |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.11:masking_register -->

## Column guidance — what to fill in

### Reg Dataset

<<MUST item:A.8.11:reg_dataset>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row source dataset identifier (from A.5.9 + A.5.34 PII inventory)

<<GUIDANCE>>

### Reg Target Env

<<MUST item:A.8.11:reg_target_env>>
_Why: Identification_

> _Standard text:_ Per-row target non-production environment

<<GUIDANCE>>

### Reg Technique

<<MUST item:A.8.11:reg_technique>>
_Why: 27002:8.11 — applicable techniques_

> _Standard text:_ Per-row masking technique applied (from procedure's approved-techniques list)

<<GUIDANCE>>

### Reg Pii Classes

<<MUST item:A.8.11:reg_pii_classes>>
_Why: GDPR Art.32 alignment_

> _Standard text:_ Per-row PII classes present (drives technique selection — strong pseudonymisation for special-category PII)

<<GUIDANCE>>

### Reg Last Refreshed

<<MUST item:A.8.11:reg_last_refreshed>>
_Why: Drift detection_

> _Standard text:_ Per-row last refresh timestamp (drives stale-mask detection)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Verification Sample

<<SHOULD item:A.8.11:reg_verification_sample>>
_Why: Audit defensibility_

> _Standard text:_ Per-row verification-sample link (re-identification residual-risk sample retained)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
