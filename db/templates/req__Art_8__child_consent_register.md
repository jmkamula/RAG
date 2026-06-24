---
leaf_id: req:Art.8:child_consent_register
control_ref: Art.8
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Child Consent Register

> Per-minor consent record proving the parental-authority path was followed. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Minor's pseudonymous identifier per row

<<MUST item:Art.8:reg_subject_id>>
_Why: Demonstrability_

<<TEXT>>

## 2. Per-row claimed age at registration

<<MUST item:Art.8:reg_claimed_age>>
_Why: Decision trail_

<<TEXT>>

## 3. Per-row consent route (child if age threshold met / parental if below threshold)

<<MUST item:Art.8:reg_route>>
_Why: Art.8.1_

<<TEXT>>

## 4. Per-row parental-authority evidence (where parental route used)

<<MUST item:Art.8:reg_parental_evidence>>
_Why: Art.8.2 — verify_

<<TEXT>>

## 5. Per-row capture timestamp

<<MUST item:Art.8:reg_timestamp>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Re-verification trigger when minor crosses the age threshold (consent transitions from parental to direct)

<<SHOULD item:Art.8:reg_re_verification>>
_Why: Lifecycle_

<<TEXT>>
