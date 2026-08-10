---
leaf_id: req:A.8.34:audit_engagement_register
control_ref: A.8.34
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Audit Testing Engagement Register

<<DOC_CONTROL>>

> Per-engagement catalogue — engagement id, tester, scope, dates, outcome, evidence-artefact location

<!-- TABLE-COLUMNS leaf:req:A.8.34:audit_engagement_register -->
<!-- column: item:A.8.34:reg_engagement_id -->
<!-- column: item:A.8.34:reg_tester -->
<!-- column: item:A.8.34:reg_scope -->
<!-- column: item:A.8.34:reg_dates -->
<!-- column: item:A.8.34:reg_outcome -->
<!-- column: item:A.8.34:reg_evidence_loc -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of each audit testing engagement, including who was involved, what was tested, key dates, outcomes, and where to find supporting evidence.

## When to use it

Use this register whenever you conduct an audit testing engagement in your environment, and update it as needed to reflect new or changed engagements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes entering details for a single engagement from scratch, with additional time needed for each new engagement you add.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.34:audit_engagement_register -->
| Reg Engagement Id | Reg Tester | Reg Scope | Reg Dates | Reg Outcome | Reg Evidence Loc |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.34:audit_engagement_register -->

## Column guidance — what to fill in

### Reg Engagement Id

<<MUST item:A.8.34:reg_engagement_id>>
_Why: Identification_

> _Standard text:_ Per-engagement unique identifier

<<GUIDANCE>>

### Reg Tester

<<MUST item:A.8.34:reg_tester>>
_Why: Accountability_

> _Standard text:_ Per-engagement tester identity (internal team / external firm)

<<GUIDANCE>>

### Reg Scope

<<MUST item:A.8.34:reg_scope>>
_Why: 27002:8.34 — agreed_

> _Standard text:_ Per-engagement scope description (systems / data / techniques agreed)

<<GUIDANCE>>

### Reg Dates

<<MUST item:A.8.34:reg_dates>>
_Why: 27002:8.34 — planned_

> _Standard text:_ Per-engagement start / end / time-windows

<<GUIDANCE>>

### Reg Outcome

<<MUST item:A.8.34:reg_outcome>>
_Why: Continuous evidence_

> _Standard text:_ Per-engagement outcome + findings count

<<GUIDANCE>>

### Reg Evidence Loc

<<MUST item:A.8.34:reg_evidence_loc>>
_Why: 27002:8.34 — assessment_

> _Standard text:_ Per-engagement evidence-artefact location reference

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Rollback Invoked

<<SHOULD item:A.8.34:reg_rollback_invoked>>
_Why: Operational defensibility_

> _Standard text:_ Per-engagement rollback-invoked flag where applicable

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
