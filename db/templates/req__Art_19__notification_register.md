---
leaf_id: req:Art.19:notification_register
control_ref: Art.19
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
---

# Recipient Notification Register

> Per-notification record proving Art.19 obligations were met for each Art.16/17/18 event. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row source event id (Art.12 register reference)

<<MUST item:Art.19:reg_event_id>>
_Why: Cross-leaf_

<<TEXT>>

## 2. Per-row recipients notified list

<<MUST item:Art.19:reg_recipient_list>>
_Why: Art.19 — recipients_

<<TEXT>>

## 3. Per-row notification date

<<MUST item:Art.19:reg_notification_date>>
_Why: Currency_

<<TEXT>>

## 4. Per-row omitted recipients with impossibility/disproportionality grounds where applicable

<<MUST item:Art.19:reg_omission_grounds>>
_Why: Art.19 — exception_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row recipient acknowledgement where available

<<SHOULD item:Art.19:reg_ack_received>>
_Why: Closure_

<<TEXT>>
