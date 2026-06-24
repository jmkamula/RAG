---
leaf_id: req:Art.85:national_law_derogation_register
control_ref: Art.85
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Per-Jurisdiction Art.85 National Law Derogation Register

> Per-jurisdiction record of the national-law provisions invoked for Art.85 derogations. One row per (Member State × derogated GDPR provision × activity scope) tuple. Refreshed at the national-law currency cadence — annual review minimum (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Named owner of the register

<<MUST item:Art.85:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 2. Per-row Member State whose national law is being invoked

<<MUST item:Art.85:reg_member_state>>
_Why: Art.85.2 — Member State law_

<<TEXT>>

## 3. Per-row specific national-law citation (statute + section + as-of date)

<<MUST item:Art.85:reg_national_provision>>
_Why: Demonstrability_

<<TEXT>>

## 4. Per-row enumeration of GDPR articles being derogated (must be from Chapter II/III/IV/V/VI/VII/IX)

<<MUST item:Art.85:reg_derogated_articles>>
_Why: Art.85.2 — scope of permissible derogations_

<<TEXT>>

## 5. Per-row activity scope (which processing this derogation covers — journalism / academic / artistic / literary)

<<MUST item:Art.85:reg_activity_scope>>
_Why: Art.85.1_

<<TEXT>>

## 6. Per-row as-of-date of the national-law citation (proves the law cited is still in force)

<<MUST item:Art.85:reg_currency_date>>
_Why: Art.85.2 — current state of law_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Reference to Member State notification to Commission per Art.85.3 (where available)

<<SHOULD item:Art.85:reg_commission_notification>>
_Why: Art.85.3 — Commission notification_

<<TEXT>>

### 2. Per-row next planned review date

<<SHOULD item:Art.85:reg_review_date>>
_Why: Currency_

<<TEXT>>
