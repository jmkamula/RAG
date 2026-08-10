---
leaf_id: req:A.7.2.7:joint_controller_register
control_ref: A.7.2.7
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Joint Controller Arrangement Register

<<DOC_CONTROL>>

> Per-arrangement row — the register of joint controller arrangements, the executed document, essence-publication link. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.2.7:joint_controller_register -->
<!-- column: item:A.7.2.7:reg_arrangement_id -->
<!-- column: item:A.7.2.7:reg_co_controller -->
<!-- column: item:A.7.2.7:reg_document_reference -->
<!-- column: item:A.7.2.7:reg_processing_scope -->
<!-- column: item:A.7.2.7:reg_essence_url -->
<!-- column: item:A.7.2.7:reg_effective_dates -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of all your joint controller arrangements, including key details and links to relevant documents, so you can demonstrate compliance with privacy standards.

## When to use it

Use this register whenever you enter into a joint controller arrangement with another party. Review and update it about once a year, or whenever a new arrangement is made.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each arrangement. Completing the register from scratch for one arrangement typically takes around 1 to 1.5 hours.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.7:joint_controller_register -->
| Reg Arrangement Id | Reg Co Controller | Reg Document Reference | Reg Processing Scope | Reg Essence Url | Reg Effective Dates |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.7:joint_controller_register -->

## Column guidance — what to fill in

### Reg Arrangement Id

<<MUST item:A.7.2.7:reg_arrangement_id>>
_Why: Referenceability_

> _Standard text:_ Unique arrangement identifier per row

<<GUIDANCE>>

### Reg Co Controller

<<MUST item:A.7.2.7:reg_co_controller>>
_Why: Traceability_

> _Standard text:_ Co-controller identity per row (legal entity)

<<GUIDANCE>>

### Reg Document Reference

<<MUST item:A.7.2.7:reg_document_reference>>
_Why: §7.2.7 — documented_

> _Standard text:_ Executed arrangement document reference per row

<<GUIDANCE>>

### Reg Processing Scope

<<MUST item:A.7.2.7:reg_processing_scope>>
_Why: Art.26.1_

> _Standard text:_ Processing scope per row (activities + PII categories jointly handled)

<<GUIDANCE>>

### Reg Essence Url

<<MUST item:A.7.2.7:reg_essence_url>>
_Why: Art.26.2_

> _Standard text:_ Essence-of-arrangement URL / publication reference per row

<<GUIDANCE>>

### Reg Effective Dates

<<MUST item:A.7.2.7:reg_effective_dates>>
_Why: Currency_

> _Standard text:_ Effective / termination dates per row

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Contact Point

<<SHOULD item:A.7.2.7:reg_contact_point>>
_Why: Art.26.1_

> _Standard text:_ Subject-facing contact point per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
