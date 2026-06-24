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
---

# Consent Register

> Per-consent record proving capture for any subject whose data is processed under Art.6.1.a consent. Annual refresh (freshness=365). Auditor's go-to artefact when challenging the lawful basis for a consent-based activity

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Subject identifier per row (pseudonymous or direct identifier)

<<MUST item:Art.7:reg_subject_id>>
_Why: Demonstrability_

<<TEXT>>

## 2. Per-row scope of consent (which activity / purpose)

<<MUST item:Art.7:reg_scope>>
_Why: Art.7.1 — granular_

<<TEXT>>

## 3. Per-row capture timestamp

<<MUST item:Art.7:reg_timestamp>>
_Why: Currency_

<<TEXT>>

## 4. Per-row capture mechanism (checkbox UI version, sign-up event id, etc.)

<<MUST item:Art.7:reg_mechanism>>
_Why: Auditability_

<<TEXT>>

## 5. Per-row withdrawal status (current / withdrawn-on-date)

<<MUST item:Art.7:reg_withdrawal_status>>
_Why: Art.7.3_

<<TEXT>>

## 6. Per-row link to Art.6 lawful basis register entry (Art.6.1.a row)

<<MUST item:Art.7:reg_basis_link>>
_Why: Cross-article coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row consent-text version captured at time of capture (proves what they agreed to)

<<SHOULD item:Art.7:reg_consent_version>>
_Why: Audit defensibility_

<<TEXT>>
