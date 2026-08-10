---
leaf_id: req:Art.7:consent_register
control_ref: Art.7
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Consent Register

<<DOC_CONTROL>>

> Per-consent record proving capture for any subject whose data is processed under Art.6.1.a consent. Annual refresh (freshness=365). Auditor's go-to artefact when challenging the lawful basis for a consent-based activity

<!-- TABLE-COLUMNS leaf:req:Art.7:consent_register -->
<!-- column: item:Art.7:reg_subject_id -->
<!-- column: item:Art.7:reg_scope -->
<!-- column: item:Art.7:reg_timestamp -->
<!-- column: item:Art.7:reg_mechanism -->
<!-- column: item:Art.7:reg_withdrawal_status -->
<!-- column: item:Art.7:reg_basis_link -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of every consent you collect from individuals, making it easy to prove you have a valid legal basis for processing their data under GDPR.

## When to use it

Use this register whenever you process personal data based on someone’s consent, and plan to review and update it about once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes to set up the required details for each consent type, with additional time needed as you add more individual consent records.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.7:consent_register -->
| Reg Subject Id | Reg Scope | Reg Timestamp | Reg Mechanism | Reg Withdrawal Status | Reg Basis Link |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.7:consent_register -->

## Column guidance — what to fill in

### Reg Subject Id

<<MUST item:Art.7:reg_subject_id>>
_Why: Demonstrability_

> _Standard text:_ Subject identifier per row (pseudonymous or direct identifier)

<<GUIDANCE>>

### Reg Scope

<<MUST item:Art.7:reg_scope>>
_Why: Art.7.1 — granular_

> _Standard text:_ Per-row scope of consent (which activity / purpose)

<<GUIDANCE>>

### Reg Timestamp

<<MUST item:Art.7:reg_timestamp>>
_Why: Currency_

> _Standard text:_ Per-row capture timestamp

<<GUIDANCE>>

### Reg Mechanism

<<MUST item:Art.7:reg_mechanism>>
_Why: Auditability_

> _Standard text:_ Per-row capture mechanism (checkbox UI version, sign-up event id, etc.)

<<GUIDANCE>>

### Reg Withdrawal Status

<<MUST item:Art.7:reg_withdrawal_status>>
_Why: Art.7.3_

> _Standard text:_ Per-row withdrawal status (current / withdrawn-on-date)

<<GUIDANCE>>

### Reg Basis Link

<<MUST item:Art.7:reg_basis_link>>
_Why: Cross-article coherence_

> _Standard text:_ Per-row link to Art.6 lawful basis register entry (Art.6.1.a row)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Consent Version

<<SHOULD item:Art.7:reg_consent_version>>
_Why: Audit defensibility_

> _Standard text:_ Per-row consent-text version captured at time of capture (proves what they agreed to)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
