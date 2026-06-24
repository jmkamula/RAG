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
---

# Personnel Authorisation Register

> Per-person authorisation — every person acting under controller authority on personal data, with scope and source of authority. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row person identifier (employee / contractor reference)

<<MUST item:Art.29:reg_person_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row source of authority (which DPA + which controller instructions)

<<MUST item:Art.29:reg_authority_source>>
_Why: Art.29_

<<TEXT>>

## 3. Per-row scope of processing the person is authorised to perform

<<MUST item:Art.29:reg_scope>>
_Why: Art.29 — only on documented instructions_

<<TEXT>>

## 4. Per-row status (active / suspended / revoked-on-date)

<<MUST item:Art.29:reg_status>>
_Why: Lifecycle_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row training completion cross-reference (A.6.3 / 7.3 records)

<<SHOULD item:Art.29:reg_training_xref>>
_Why: Cross-control_

<<TEXT>>
