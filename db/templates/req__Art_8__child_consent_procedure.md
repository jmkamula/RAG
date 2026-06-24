---
leaf_id: req:Art.8:child_consent_procedure
control_ref: Art.8
standard_id: GDPR:2016/679
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Child Consent and Age-Verification Procedure

> Art.8 requires that when offering information-society services directly to a child, consent is only lawful if the child is at least 16 (or as low as 13 per Member State law) OR parental consent is obtained. The procedure is the canonical artefact. Sibling leaves: child consent register, applicable services scope, program review

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Age threshold stated per applicable Member State (16 default; some MS lower it to 13/14/15)

<<MUST item:Art.8:proc_age_threshold>>
_Why: Art.8.1_

<<TEXT>>

## 2. Age-verification mechanism (self-declaration with reasonable-effort cross-check; not relying on self-declaration alone in higher-risk cases)

<<MUST item:Art.8:proc_age_verification>>
_Why: Art.8.2 — reasonable efforts_

<<TEXT>>

## 3. Parental-consent capture route (when subject is under threshold) — verifiable parental authority

<<MUST item:Art.8:proc_parental_route>>
_Why: Art.8.1_

<<TEXT>>

## 4. Information presentation adapted for children (plain language where minors will read it)

<<MUST item:Art.8:proc_information>>
_Why: Art.12.1 — concise + accessible + clear_

<<TEXT>>

## 5. Named owner of the procedure

<<MUST item:Art.8:proc_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Dispute-handling pathway when claimed age differs from verified evidence

<<SHOULD item:Art.8:proc_age_dispute>>
_Why: Operational discipline_

<<TEXT>>
