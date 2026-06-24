---
leaf_id: req:Art.12:rights_request_register
control_ref: Art.12
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Rights Request Register

> Per-request record covering EVERY data subject right exercise (Art.15-22). Centralised log — drives Art.12.3 SLA tracking. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique request identifier per row

<<MUST item:Art.12:reg_request_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-row right type (Art.15 access / Art.16 rectification / Art.17 erasure / Art.18 restriction / Art.20 portability / Art.21 objection / Art.22 automated)

<<MUST item:Art.12:reg_right_type>>
_Why: Cross-article coherence_

<<TEXT>>

## 3. Per-row request received date

<<MUST item:Art.12:reg_request_date>>
_Why: SLA tracking_

<<TEXT>>

## 4. Per-row response sent date (or extension notice date)

<<MUST item:Art.12:reg_response_date>>
_Why: Art.12.3 SLA_

<<TEXT>>

## 5. Per-row outcome (fulfilled / partial / refused with grounds / extended)

<<MUST item:Art.12:reg_outcome>>
_Why: Audit clarity_

<<TEXT>>

## 6. Per-row SLA-met flag (one month or notified extension)

<<MUST item:Art.12:reg_sla_met>>
_Why: Art.12.3 — timeliness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row identity verification method used

<<SHOULD item:Art.12:reg_identity_method>>
_Why: Art.12.6 audit_

<<TEXT>>
