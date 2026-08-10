---
leaf_id: req:Art.16:rectification_register
control_ref: Art.16
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Rectification Request Register

<<DOC_CONTROL>>

> Per-request record proving every Art.16 request was handled per procedure. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.16:rectification_register -->
<!-- column: item:Art.16:reg_request_id -->
<!-- column: item:Art.16:reg_subject_id -->
<!-- column: item:Art.16:reg_systems_touched -->
<!-- column: item:Art.16:reg_response_date -->
<!-- column: item:Art.16:reg_art19_xref -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every request you receive to correct personal data, showing that you’ve followed the proper steps under GDPR Article 16.

## When to use it

Use this register whenever someone asks you to correct their personal data. Review and update it at least once a year to ensure it stays current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1–1.5 hours setting up the initial register, plus 10–15 minutes for each new rectification request you log.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.16:rectification_register -->
| Reg Request Id | Reg Subject Id | Reg Systems Touched | Reg Response Date | Reg Art19 Xref |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.16:rectification_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:Art.16:reg_request_id>>
_Why: Cross-leaf_

> _Standard text:_ Per-row request id (Art.12 cross-ref)

<<GUIDANCE>>

### Reg Subject Id

<<MUST item:Art.16:reg_subject_id>>
_Why: Audit_

> _Standard text:_ Per-row subject identifier (pseudonymous)

<<GUIDANCE>>

### Reg Systems Touched

<<MUST item:Art.16:reg_systems_touched>>
_Why: Art.16 — across all instances_

> _Standard text:_ Per-row systems where rectification was applied

<<GUIDANCE>>

### Reg Response Date

<<MUST item:Art.16:reg_response_date>>
_Why: Art.12.3_

> _Standard text:_ Per-row response date (Art.12.3 SLA)

<<GUIDANCE>>

### Reg Art19 Xref

<<MUST item:Art.16:reg_art19_xref>>
_Why: Art.19_

> _Standard text:_ Per-row Art.19 notification reference

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Correction Summary

<<SHOULD item:Art.16:reg_correction_summary>>
_Why: Audit clarity_

> _Standard text:_ Per-row summary of correction made

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
