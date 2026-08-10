---
leaf_id: req:A.7.11:utility_register
control_ref: A.7.11
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Per-Site Utility Register

<<DOC_CONTROL>>

> The catalogue of critical utilities per site — feed type, redundancy in place, last test, provider, owner

<!-- TABLE-COLUMNS leaf:req:A.7.11:utility_register -->
<!-- column: item:A.7.11:reg_site_utility -->
<!-- column: item:A.7.11:reg_redundancy_in_place -->
<!-- column: item:A.7.11:reg_provider -->
<!-- column: item:A.7.11:reg_last_test -->
<!-- column: item:A.7.11:reg_next_test -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all critical utilities at each site, including details like provider, owner, and redundancy. It's useful for managing risks and meeting compliance requirements.

## When to use it

Use this register whenever you need to document or review the utilities supporting your environment, and update it whenever there are changes or as often as necessary to keep information current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10–15 minutes per utility per site to gather and enter the required details, so the total time will depend on the number of sites and utilities you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.11:utility_register -->
| Reg Site Utility | Reg Redundancy In Place | Reg Provider | Reg Last Test | Reg Next Test |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.11:utility_register -->

## Column guidance — what to fill in

### Reg Site Utility

<<MUST item:A.7.11:reg_site_utility>>
_Why: 27002:7.11 — supporting utilities_

> _Standard text:_ Per-row site + utility pair

<<GUIDANCE>>

### Reg Redundancy In Place

<<MUST item:A.7.11:reg_redundancy_in_place>>
_Why: 27002:7.11 — protected_

> _Standard text:_ Per-row redundancy in place (matches the policy's required redundancy)

<<GUIDANCE>>

### Reg Provider

<<MUST item:A.7.11:reg_provider>>
_Why: 27002:7.11 — maintenance_

> _Standard text:_ Per-row provider with SLA reference

<<GUIDANCE>>

### Reg Last Test

<<MUST item:A.7.11:reg_last_test>>
_Why: Continuity validation_

> _Standard text:_ Per-row last test date and outcome

<<GUIDANCE>>

### Reg Next Test

<<MUST item:A.7.11:reg_next_test>>
_Why: Planning_

> _Standard text:_ Per-row next-test date scheduled

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Runtime

<<SHOULD item:A.7.11:reg_runtime>>
_Why: Realism check_

> _Standard text:_ Per-row autonomous-runtime stat (UPS minutes, generator fuel days)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
