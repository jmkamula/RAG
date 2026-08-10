---
leaf_id: req:Art.49:invocation_register
control_ref: Art.49
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Derogation Invocation Register

<<DOC_CONTROL>>

> Per-invocation record. Annual refresh (freshness=365). Most orgs should have a sparse register — frequent derogation invocations signal Art.46 should be used instead

<!-- TABLE-COLUMNS leaf:req:Art.49:invocation_register -->
<!-- column: item:Art.49:reg_invocation_id -->
<!-- column: item:Art.49:reg_derogation -->
<!-- column: item:Art.49:reg_destination -->
<!-- column: item:Art.49:reg_subject_count -->
<!-- column: item:Art.49:reg_documentation -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record each time you rely on a GDPR derogation for international data transfers. It’s designed to show regulators you’re tracking these rare exceptions properly.

## When to use it

Use this register whenever you invoke a GDPR derogation for a data transfer, especially if your situation matches specific triggers. Review and update it at least once a year to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours to complete the initial setup, plus additional time for each new derogation event you record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.49:invocation_register -->
| Reg Invocation Id | Reg Derogation | Reg Destination | Reg Subject Count | Reg Documentation |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.49:invocation_register -->

## Column guidance — what to fill in

### Reg Invocation Id

<<MUST item:Art.49:reg_invocation_id>>
_Why: Audit_

> _Standard text:_ Per-row invocation id

<<GUIDANCE>>

### Reg Derogation

<<MUST item:Art.49:reg_derogation>>
_Why: Art.49.1_

> _Standard text:_ Per-row Art.49.1 derogation cited (a-g + second-paragraph)

<<GUIDANCE>>

### Reg Destination

<<MUST item:Art.49:reg_destination>>
_Why: Cross-leaf with Art.44_

> _Standard text:_ Per-row destination + recipient

<<GUIDANCE>>

### Reg Subject Count

<<MUST item:Art.49:reg_subject_count>>
_Why: Art.49.1 second paragraph_

> _Standard text:_ Per-row data subject count (frequency / volume — non-repetitive test)

<<GUIDANCE>>

### Reg Documentation

<<MUST item:Art.49:reg_documentation>>
_Why: Defensibility_

> _Standard text:_ Per-row supporting documentation (consent capture / contract / claim doc / public-interest determination)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Sa Notification Date

<<SHOULD item:Art.49:reg_sa_notification_date>>
_Why: Art.49.1 second paragraph_

> _Standard text:_ Per-row SA notification date where Art.49.1 second-paragraph used

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
