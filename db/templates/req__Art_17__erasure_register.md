---
leaf_id: req:Art.17:erasure_register
control_ref: Art.17
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Erasure Request Register

<<DOC_CONTROL>>

> Per-request record proving Art.17 lifecycle (grounds → exception assessment → erasure → notification). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.17:erasure_register -->
<!-- column: item:Art.17:reg_request_id -->
<!-- column: item:Art.17:reg_grounds -->
<!-- column: item:Art.17:reg_exceptions -->
<!-- column: item:Art.17:reg_systems_erased -->
<!-- column: item:Art.17:reg_response_date -->
<!-- column: item:Art.17:reg_art19_xref -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of each data erasure request, showing how you handled it from start to finish. It’s useful for demonstrating compliance with GDPR requirements around data deletion.

## When to use it

Use this register whenever someone asks you to erase their personal data, and update it for each new request. Review and refresh the register about once a year to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes setting up the register for the first time, plus additional time for each new request you log.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.17:erasure_register -->
| Reg Request Id | Reg Grounds | Reg Exceptions | Reg Systems Erased | Reg Response Date | Reg Art19 Xref |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.17:erasure_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:Art.17:reg_request_id>>
_Why: Cross-leaf_

> _Standard text:_ Per-row request id (Art.12 cross-ref)

<<GUIDANCE>>

### Reg Grounds

<<MUST item:Art.17:reg_grounds>>
_Why: Art.17.1_

> _Standard text:_ Per-row Art.17.1 ground (a-f) recorded

<<GUIDANCE>>

### Reg Exceptions

<<MUST item:Art.17:reg_exceptions>>
_Why: Art.17.3_

> _Standard text:_ Per-row Art.17.3 exception assessment (none / cited exception)

<<GUIDANCE>>

### Reg Systems Erased

<<MUST item:Art.17:reg_systems_erased>>
_Why: Art.17.1 — all instances_

> _Standard text:_ Per-row systems where erasure was applied (including backups + replicas)

<<GUIDANCE>>

### Reg Response Date

<<MUST item:Art.17:reg_response_date>>
_Why: Art.12.3_

> _Standard text:_ Per-row response date (Art.12.3 SLA)

<<GUIDANCE>>

### Reg Art19 Xref

<<MUST item:Art.17:reg_art19_xref>>
_Why: Art.19_

> _Standard text:_ Per-row Art.19 notification reference

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Art17 2 Action

<<SHOULD item:Art.17:reg_art17_2_action>>
_Why: Art.17.2_

> _Standard text:_ Per-row Art.17.2 public-disclosure action where applicable

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
