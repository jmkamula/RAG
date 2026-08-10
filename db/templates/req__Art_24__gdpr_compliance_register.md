---
leaf_id: req:Art.24:gdpr_compliance_register
control_ref: Art.24
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# GDPR Compliance Register

<<DOC_CONTROL>>

> Per-obligation register tracking the org's posture against every GDPR article in scope. Annual refresh (freshness=365). Distinct from the Art.30 RoPA (activities) and the lawful-basis register (Art.6 per-activity): this is the meta-tracker of compliance posture per article

<!-- TABLE-COLUMNS leaf:req:Art.24:gdpr_compliance_register -->
<!-- column: item:Art.24:reg_article_id -->
<!-- column: item:Art.24:reg_applicability -->
<!-- column: item:Art.24:reg_implementing_artefact -->
<!-- column: item:Art.24:reg_status -->
<!-- column: item:Art.24:reg_owner -->
<!-- column: item:Art.24:reg_last_assessed -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you track your organization's compliance with each relevant article of the GDPR, giving you a clear overview of your current status and any gaps that need attention.

## When to use it

Use this register if your organization is subject to GDPR and you want to monitor your compliance posture for each article. Update it about once a year to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1–2 hours setting up this register from scratch, depending on the number of GDPR articles in scope and the detail required for each entry.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.24:gdpr_compliance_register -->
| Reg Article Id | Reg Applicability | Reg Implementing Artefact | Reg Status | Reg Owner | Reg Last Assessed |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.24:gdpr_compliance_register -->

## Column guidance — what to fill in

### Reg Article Id

<<MUST item:Art.24:reg_article_id>>
_Why: Coverage_

> _Standard text:_ Per-row GDPR article identifier

<<GUIDANCE>>

### Reg Applicability

<<MUST item:Art.24:reg_applicability>>
_Why: Defensibility_

> _Standard text:_ Per-row applicability assessment (in scope / N/A with reason)

<<GUIDANCE>>

### Reg Implementing Artefact

<<MUST item:Art.24:reg_implementing_artefact>>
_Why: Demonstrability_

> _Standard text:_ Per-row link to the implementing artefact (procedure / policy / register / DPA / certification)

<<GUIDANCE>>

### Reg Status

<<MUST item:Art.24:reg_status>>
_Why: Status visibility_

> _Standard text:_ Per-row implementation status (implemented / partial / planned / N/A)

<<GUIDANCE>>

### Reg Owner

<<MUST item:Art.24:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-row owner

<<GUIDANCE>>

### Reg Last Assessed

<<MUST item:Art.24:reg_last_assessed>>
_Why: Currency_

> _Standard text:_ Per-row last-assessed date (drives staleness)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Residual Risk

<<SHOULD item:Art.24:reg_residual_risk>>
_Why: Risk visibility_

> _Standard text:_ Per-row residual risk where status is partial

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
