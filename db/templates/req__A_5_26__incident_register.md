---
leaf_id: req:A.5.26:incident_register
control_ref: A.5.26
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 90
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Information Security Incident Register

<<DOC_CONTROL>>

> A.5.26 expects incidents to be tracked from detection through closure, with the trail of actions preserved. The incident register is the live master record — every incident, its severity, status, owner, and the key lifecycle dates (detection, containment, eradication, recovery, closure) — feeding the periodic IR-program review and the per-incident closure records. Fast-data freshness (90d) per Style v2 — an incident register that's a year stale is not a register

<!-- TABLE-COLUMNS leaf:req:A.5.26:incident_register -->
<!-- column: item:A.5.26:reg_incident_id -->
<!-- column: item:A.5.26:reg_severity -->
<!-- column: item:A.5.26:reg_status -->
<!-- column: item:A.5.26:reg_owner -->
<!-- column: item:A.5.26:reg_lifecycle_dates -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, up-to-date record of all information security incidents, tracking each one from discovery to closure. It ensures you have a reliable overview for reviews and audits.

## When to use it

Use this register whenever an information security incident occurs in your environment, and update it at least every three months to keep the information current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes to set up the initial register with all required details, plus additional time for each incident you add as they happen.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.26:incident_register -->
| Reg Incident Id | Reg Severity | Reg Status | Reg Owner | Reg Lifecycle Dates |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.26:incident_register -->

## Column guidance — what to fill in

### Reg Incident Id

<<MUST item:A.5.26:reg_incident_id>>
_Why: 27002:5.26 — recording_

> _Standard text:_ Each incident captured with a unique identifier (links to A.5.25 triage decision)

<<GUIDANCE>>

### Reg Severity

<<MUST item:A.5.26:reg_severity>>
_Why: 27002:5.26 — coordination by severity_

> _Standard text:_ Severity per row (per the classification scale used at triage)

<<GUIDANCE>>

### Reg Status

<<MUST item:A.5.26:reg_status>>
_Why: 27002:5.26e_

> _Standard text:_ Status per row (open / contained / eradicated / recovered / closed)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.5.26:reg_owner>>
_Why: Accountability_

> _Standard text:_ Named Incident Manager / owner per row

<<GUIDANCE>>

### Reg Lifecycle Dates

<<MUST item:A.5.26:reg_lifecycle_dates>>
_Why: 27002:5.26 — log of decisions_

> _Standard text:_ Lifecycle dates per row: detected / contained / eradicated / recovered / closed

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Impact Flag

<<SHOULD item:A.5.26:reg_impact_flag>>
_Why: External notification triggers_

> _Standard text:_ Public-facing or regulator-relevant impact flag per row (drives notification path)

<<GUIDANCE>>

### Reg Evidence Link

<<SHOULD item:A.5.26:reg_evidence_link>>
_Why: Forensic preservation_

> _Standard text:_ Reference to evidence package per row (link to A.5.28 evidence store)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
