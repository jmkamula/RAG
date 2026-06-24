---
leaf_id: req:Art.45:adequacy_register
control_ref: Art.45
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
---

# Adequacy Reliance Register

> Per-transfer record proving adequacy reliance is current and recipient is eligible. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row transfer id (Art.44 register cross-ref)

<<MUST item:Art.45:reg_transfer_id>>
_Why: Cross-leaf_

<<TEXT>>

## 2. Per-row adequacy decision cited (Commission decision reference + effective date)

<<MUST item:Art.45:reg_adequacy_decision>>
_Why: Art.45.3_

<<TEXT>>

## 3. Per-row recipient-eligibility status (e.g. US-DPF active certification verified)

<<MUST item:Art.45:reg_recipient_eligible>>
_Why: Art.45.3 partial_

<<TEXT>>

## 4. Per-row last-verified date

<<MUST item:Art.45:reg_last_verified>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row invalidation-watch flag (active CJEU challenges / Commission review status)

<<SHOULD item:Art.45:reg_invalidation_watch>>
_Why: Schrems-style risk_

<<TEXT>>
