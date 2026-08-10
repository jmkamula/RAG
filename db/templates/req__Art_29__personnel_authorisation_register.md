---
leaf_id: req:Art.29:personnel_authorisation_register
control_ref: Art.29
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Personnel Authorisation Register

<<DOC_CONTROL>>

> Per-person authorisation — every person acting under controller authority on personal data, with scope and source of authority. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.29:personnel_authorisation_register -->
<!-- column: item:Art.29:reg_person_id -->
<!-- column: item:Art.29:reg_authority_source -->
<!-- column: item:Art.29:reg_scope -->
<!-- column: item:Art.29:reg_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of who in your organisation is authorised to handle personal data, including what they can do and where their authority comes from.

## When to use it

Use this register whenever you need to document and review which staff members are allowed to access personal data, and update it about once a year to stay compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per person listed, so the total time will depend on the number of people you need to include.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.29:personnel_authorisation_register -->
| Reg Person Id | Reg Authority Source | Reg Scope | Reg Status |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.29:personnel_authorisation_register -->

## Column guidance — what to fill in

### Reg Person Id

<<MUST item:Art.29:reg_person_id>>
_Why: Audit_

> _Standard text:_ Per-row person identifier (employee / contractor reference)

<<GUIDANCE>>

### Reg Authority Source

<<MUST item:Art.29:reg_authority_source>>
_Why: Art.29_

> _Standard text:_ Per-row source of authority (which DPA + which controller instructions)

<<GUIDANCE>>

### Reg Scope

<<MUST item:Art.29:reg_scope>>
_Why: Art.29 — only on documented instructions_

> _Standard text:_ Per-row scope of processing the person is authorised to perform

<<GUIDANCE>>

### Reg Status

<<MUST item:Art.29:reg_status>>
_Why: Lifecycle_

> _Standard text:_ Per-row status (active / suspended / revoked-on-date)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Training Xref

<<SHOULD item:Art.29:reg_training_xref>>
_Why: Cross-control_

> _Standard text:_ Per-row training completion cross-reference (A.6.3 / 7.3 records)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
