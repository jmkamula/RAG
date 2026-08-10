---
leaf_id: req:7.1:isms_resources_record
control_ref: 7.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# ISMS Resource Allocation Record

<<DOC_CONTROL>>

> Clause 7.1 requires the organisation to determine and provide resources needed for ISMS establishment, implementation, maintenance, and improvement. The record is the canonical artefact — financial, human, infrastructure, technology resources committed. Sibling leaves: determination procedure, applicable resource categories scope, program review. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.1:isms_resources_record -->
<!-- column: item:7.1:financial -->
<!-- column: item:7.1:human -->
<!-- column: item:7.1:infrastructure -->
<!-- column: item:7.1:technology -->
<!-- column: item:7.1:owner -->
<!-- column: item:7.1:approved_by -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you clearly document all the resources—financial, human, infrastructure, and technology—your organization commits to its information security management system. It provides a single, organized record to demonstrate compliance with ISO 27001 requirements.

## When to use it

Use this register whenever you need to show what resources are dedicated to your ISMS, and update it at least once a year to keep your records current and accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this from scratch, depending on the number of resource categories and the detail you provide for each entry.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.1:isms_resources_record -->
| Financial | Human | Infrastructure | Technology | Owner | Approved By |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.1:isms_resources_record -->

## Column guidance — what to fill in

### Financial

<<MUST item:7.1:financial>>
_Why: Clause 7.1 — resources needed_

> _Standard text:_ Financial resources allocated (budget for ISMS activities)

<<GUIDANCE>>

### Human

<<MUST item:7.1:human>>
_Why: Clause 7.1 — resources_

> _Standard text:_ Human resources assigned (headcount, roles, time allocation)

<<GUIDANCE>>

### Infrastructure

<<MUST item:7.1:infrastructure>>
_Why: Clause 7.1 — resources_

> _Standard text:_ Infrastructure provided (premises, equipment, transport)

<<GUIDANCE>>

### Technology

<<MUST item:7.1:technology>>
_Why: Clause 7.1 — resources_

> _Standard text:_ Technology platforms supporting the ISMS (GRC tool, document repo, training platform)

<<GUIDANCE>>

### Owner

<<MUST item:7.1:owner>>
_Why: Accountability_

> _Standard text:_ Named owner of the resources record (typically ISMS Manager with finance partner)

<<GUIDANCE>>

### Approved By

<<MUST item:7.1:approved_by>>
_Why: Clause 7.1 — provide_

> _Standard text:_ Approving authority recorded (top management for budget allocations)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Budget Link

<<SHOULD item:7.1:budget_link>>
_Why: Visibility_

> _Standard text:_ Reference to organisation budget where ISMS spend appears

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
