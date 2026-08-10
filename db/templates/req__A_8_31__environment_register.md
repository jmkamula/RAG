---
leaf_id: req:A.8.31:environment_register
control_ref: A.8.31
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Environment Register

<<DOC_CONTROL>>

> Per-environment catalogue — env id, purpose, data classes permitted, owner, access list reference

<!-- TABLE-COLUMNS leaf:req:A.8.31:environment_register -->
<!-- column: item:A.8.31:reg_env_id -->
<!-- column: item:A.8.31:reg_purpose -->
<!-- column: item:A.8.31:reg_data_allowed -->
<!-- column: item:A.8.31:reg_owner -->
<!-- column: item:A.8.31:reg_access_ref -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of each environment your team manages, including its purpose, who owns it, what data it holds, and who can access it. It’s useful for staying organized and meeting compliance requirements.

## When to use it

Use this register whenever your environment setup matches specific compliance triggers, and update it whenever there are changes to your environments or access permissions.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each environment you need to document, so filling it out from scratch may take around 1-2 hours depending on the number of environments.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.31:environment_register -->
| Reg Env Id | Reg Purpose | Reg Data Allowed | Reg Owner | Reg Access Ref |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.31:environment_register -->

## Column guidance — what to fill in

### Reg Env Id

<<MUST item:A.8.31:reg_env_id>>
_Why: Identification_

> _Standard text:_ Per-row environment unique identifier

<<GUIDANCE>>

### Reg Purpose

<<MUST item:A.8.31:reg_purpose>>
_Why: 27002:8.31 — separated_

> _Standard text:_ Per-row purpose (dev / test / staging / production / sandbox / training)

<<GUIDANCE>>

### Reg Data Allowed

<<MUST item:A.8.31:reg_data_allowed>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row data classes permitted (drives masking obligations from A.8.11)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.8.31:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-row named owner (technology lead with InfoSec partner for production)

<<GUIDANCE>>

### Reg Access Ref

<<MUST item:A.8.31:reg_access_ref>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row access-list reference (cross-link to A.8.3 access matrix)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Audited

<<SHOULD item:A.8.31:reg_last_audited>>
_Why: Drift detection_

> _Standard text:_ Per-row last-audited timestamp

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
