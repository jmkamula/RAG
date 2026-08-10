---
leaf_id: req:10.2:nonconformity_register
control_ref: 10.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 8
should_count: 1
table_shape: true
---

# Nonconformity Register

<<DOC_CONTROL>>

> Per-NC record tracking the full lifecycle: identification → root cause → corrective action → effectiveness check → closure. The auditor's most-scrutinised register: an open NC with no closure timeline signals a broken ISMS. Annual refresh (freshness=365). Cross-link to A.5.36 nonconformity register for compliance-with-rules NCs

<!-- TABLE-COLUMNS leaf:req:10.2:nonconformity_register -->
<!-- column: item:10.2:reg_nc_id -->
<!-- column: item:10.2:reg_source -->
<!-- column: item:10.2:reg_nature -->
<!-- column: item:10.2:reg_react -->
<!-- column: item:10.2:reg_root_cause -->
<!-- column: item:10.2:reg_corrective_action -->
<!-- column: item:10.2:reg_effectiveness_check -->
<!-- column: item:10.2:reg_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you track every nonconformity from discovery through resolution, ensuring nothing falls through the cracks and your compliance program stays audit-ready.

## When to use it

Use this register whenever a nonconformity is identified in your environment, and review or update it at least once a year to keep records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours to complete all required elements for a single nonconformity entry; more time will be needed as you add additional records.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:10.2:nonconformity_register -->
| Reg Nc Id | Reg Source | Reg Nature | Reg React | Reg Root Cause | Reg Corrective Action | Reg Effectiveness Check | Reg Status |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:10.2:nonconformity_register -->

## Column guidance — what to fill in

### Reg Nc Id

<<MUST item:10.2:reg_nc_id>>
_Why: Audit defensibility_

> _Standard text:_ Unique NC identifier per row

<<GUIDANCE>>

### Reg Source

<<MUST item:10.2:reg_source>>
_Why: Cross-clause traceability_

> _Standard text:_ Per-row source (9.2 internal audit, surveillance audit, incident lesson, regulator finding, party complaint)

<<GUIDANCE>>

### Reg Nature

<<MUST item:10.2:reg_nature>>
_Why: Clause 10.2 — nature_

> _Standard text:_ Per-row nature of NC (what failed against what requirement)

<<GUIDANCE>>

### Reg React

<<MUST item:10.2:reg_react>>
_Why: Clause 10.2 a)_

> _Standard text:_ Per-row immediate-reaction record (containment / correction)

<<GUIDANCE>>

### Reg Root Cause

<<MUST item:10.2:reg_root_cause>>
_Why: Clause 10.2 b)_

> _Standard text:_ Per-row root cause analysis record (5-whys, fishbone, or equivalent)

<<GUIDANCE>>

### Reg Corrective Action

<<MUST item:10.2:reg_corrective_action>>
_Why: Clause 10.2 c)_

> _Standard text:_ Per-row corrective action(s) with owner + target date

<<GUIDANCE>>

### Reg Effectiveness Check

<<MUST item:10.2:reg_effectiveness_check>>
_Why: Clause 10.2 d)_

> _Standard text:_ Per-row effectiveness verification (did the action prevent recurrence?)

<<GUIDANCE>>

### Reg Status

<<MUST item:10.2:reg_status>>
_Why: Tracking_

> _Standard text:_ Per-row status (open / in-progress / closed / re-opened)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Isms Change Xref

<<SHOULD item:10.2:reg_isms_change_xref>>
_Why: Clause 10.2 e)_

> _Standard text:_ Per-row ISMS-change cross-reference (link to 6.3 change record when the NC drove an ISMS amendment)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
