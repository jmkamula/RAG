---
leaf_id: req:A.7.12:cabling_register
control_ref: A.7.12
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Cabling Run Register

<<DOC_CONTROL>>

> The catalogue of cabling runs (or aggregations) — site, run id, carried traffic class, routing class, last inspection

<!-- TABLE-COLUMNS leaf:req:A.7.12:cabling_register -->
<!-- column: item:A.7.12:reg_run_id -->
<!-- column: item:A.7.12:reg_site -->
<!-- column: item:A.7.12:reg_traffic_class -->
<!-- column: item:A.7.12:reg_routing -->
<!-- column: item:A.7.12:reg_last_inspected -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an organized record of all your cabling runs, including key details like location, identification, and inspection history. It's useful for tracking and managing your network infrastructure efficiently.

## When to use it

Use this register whenever you need to document or update information about your site's cabling runs. It should be maintained at all times and updated whenever changes or inspections occur.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per cabling run to fill in the required details from scratch. The total time depends on how many cabling runs you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.12:cabling_register -->
| Reg Run Id | Reg Site | Reg Traffic Class | Reg Routing | Reg Last Inspected |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.12:cabling_register -->

## Column guidance — what to fill in

### Reg Run Id

<<MUST item:A.7.12:reg_run_id>>
_Why: Audit defensibility_

> _Standard text:_ Per-row run identifier

<<GUIDANCE>>

### Reg Site

<<MUST item:A.7.12:reg_site>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-row site

<<GUIDANCE>>

### Reg Traffic Class

<<MUST item:A.7.12:reg_traffic_class>>
_Why: 27002:7.12 — proportional_

> _Standard text:_ Per-row carried traffic class (drives encryption + tamper-evidence requirements)

<<GUIDANCE>>

### Reg Routing

<<MUST item:A.7.12:reg_routing>>
_Why: 27002:7.12 — protected_

> _Standard text:_ Per-row routing description (conduit / overhead-tray / under-floor / via-shared-corridor)

<<GUIDANCE>>

### Reg Last Inspected

<<MUST item:A.7.12:reg_last_inspected>>
_Why: Drift prevention_

> _Standard text:_ Per-row last-inspected date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Remediation

<<SHOULD item:A.7.12:reg_remediation>>
_Why: Operational discipline_

> _Standard text:_ Per-row remediation log where protection falls short

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
