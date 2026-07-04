---
leaf_id: req:A.7.3.7:third_party_notification_procedure
control_ref: A.7.3.7
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Third-Party Notification Procedure

> §7.3.7 requires informing third parties (recipients of shared PII) when subjects modify consent, withdraw, object, or request correction/erasure/restriction. Bridges to GDPR Art.19.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Recipient inventory — active communication channels with every third party PII has been shared with (link to A.7.5.4 disclosure register)

<<MUST item:A.7.3.7:proc_recipient_inventory>>
_Why: §7.3.7 — determine and maintain active channels_

<<TEXT>>

## 2. Trigger map — which subject events (withdrawal / correction / erasure / restriction / objection) require third-party notification

<<MUST item:A.7.3.7:proc_trigger_map>>
_Why: §7.3.7 — modification, withdrawal or objections_

<<TEXT>>

## 3. Notification format standardised (e.g. structured message with subject ref, event type, expected action)

<<MUST item:A.7.3.7:proc_notification_format>>
_Why: Consistency_

<<TEXT>>

## 4. Acknowledgement of receipt monitored

<<MUST item:A.7.3.7:proc_ack_receipt>>
_Why: §7.3.7 — monitor acknowledgement_

<<TEXT>>

## 5. Impossibility / disproportionate-effort exception documented per Art.19

<<MUST item:A.7.3.7:proc_impossibility_exception>>
_Why: GDPR Art.19 — unless proves impossible or disproportionate effort_

<<TEXT>>

## 6. Subject-disclosure obligation — on request, org informs the subject of recipients notified (Art.19)

<<MUST item:A.7.3.7:proc_subject_disclosure>>
_Why: GDPR Art.19_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Automation where feasible — scripted notification to processors + integrations

<<SHOULD item:A.7.3.7:proc_automation>>
_Why: Reliability_

<<TEXT>>
