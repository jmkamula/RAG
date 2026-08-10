---
leaf_id: req:Art.31:interaction_register
control_ref: Art.31
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# SA Interaction Register

<<DOC_CONTROL>>

> Per-interaction record of all SA engagements (inquiry / investigation / audit / consultation). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.31:interaction_register -->
<!-- column: item:Art.31:reg_interaction_id -->
<!-- column: item:Art.31:reg_sa -->
<!-- column: item:Art.31:reg_topic -->
<!-- column: item:Art.31:reg_received_date -->
<!-- column: item:Art.31:reg_response_date -->
<!-- column: item:Art.31:reg_outcome -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every interaction you have with supervisory authorities, including inquiries, audits, and consultations. It’s designed to support GDPR compliance and make annual reviews easier.

## When to use it

Use this register whenever you engage with a supervisory authority, such as during an investigation or audit. Plan to review and update it at least once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes to set up the initial register, plus additional time for each new interaction you record throughout the year.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.31:interaction_register -->
| Reg Interaction Id | Reg Sa | Reg Topic | Reg Received Date | Reg Response Date | Reg Outcome |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.31:interaction_register -->

## Column guidance — what to fill in

### Reg Interaction Id

<<MUST item:Art.31:reg_interaction_id>>
_Why: Audit_

> _Standard text:_ Per-row interaction id

<<GUIDANCE>>

### Reg Sa

<<MUST item:Art.31:reg_sa>>
_Why: Defining the relationship_

> _Standard text:_ Per-row supervisory authority identifier (which MS + which SA)

<<GUIDANCE>>

### Reg Topic

<<MUST item:Art.31:reg_topic>>
_Why: Art.31 + Art.36_

> _Standard text:_ Per-row topic (inquiry / complaint investigation / on-site audit / Art.36 consultation)

<<GUIDANCE>>

### Reg Received Date

<<MUST item:Art.31:reg_received_date>>
_Why: Currency_

> _Standard text:_ Per-row received date

<<GUIDANCE>>

### Reg Response Date

<<MUST item:Art.31:reg_response_date>>
_Why: SLA tracking_

> _Standard text:_ Per-row response date or status (open / in-progress / closed)

<<GUIDANCE>>

### Reg Outcome

<<MUST item:Art.31:reg_outcome>>
_Why: Audit clarity_

> _Standard text:_ Per-row outcome (no-action / corrective measures / fine / ongoing)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Lessons

<<SHOULD item:Art.31:reg_lessons>>
_Why: Cross-clause_

> _Standard text:_ Per-row lessons / actions feeding into 10.1 continual improvement

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
