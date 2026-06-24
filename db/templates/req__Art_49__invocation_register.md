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
---

# Derogation Invocation Register

> Per-invocation record. Annual refresh (freshness=365). Most orgs should have a sparse register — frequent derogation invocations signal Art.46 should be used instead

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row invocation id

<<MUST item:Art.49:reg_invocation_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row Art.49.1 derogation cited (a-g + second-paragraph)

<<MUST item:Art.49:reg_derogation>>
_Why: Art.49.1_

<<TEXT>>

## 3. Per-row destination + recipient

<<MUST item:Art.49:reg_destination>>
_Why: Cross-leaf with Art.44_

<<TEXT>>

## 4. Per-row data subject count (frequency / volume — non-repetitive test)

<<MUST item:Art.49:reg_subject_count>>
_Why: Art.49.1 second paragraph_

<<TEXT>>

## 5. Per-row supporting documentation (consent capture / contract / claim doc / public-interest determination)

<<MUST item:Art.49:reg_documentation>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row SA notification date where Art.49.1 second-paragraph used

<<SHOULD item:Art.49:reg_sa_notification_date>>
_Why: Art.49.1 second paragraph_

<<TEXT>>
