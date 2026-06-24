---
leaf_id: req:Art.33:breach_notification
control_ref: Art.33
standard_id: GDPR:2016/679
evidence_type: breach_notification
trigger_type: operational
template_version: 1
must_count: 5
should_count: 1
---

# Personal Data Breach Notification to Supervisory Authority

> Art.33 requires notification to supervisory authority within 72 hours of becoming aware of a breach. Per-breach notification record is the canonical artefact. Sibling leaves: notification procedure (the how), applicable triggers scope, program review

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Nature of the breach including categories and approximate number of data subjects

<<MUST item:Art.33:nature>>
_Why: Art.33.3a_

<<TEXT>>

## 2. Contact details of DPO or other contact point

<<MUST item:Art.33:dpo_contact>>
_Why: Art.33.3b_

<<TEXT>>

## 3. Likely consequences of the breach

<<MUST item:Art.33:consequences>>
_Why: Art.33.3c_

<<TEXT>>

## 4. Measures taken or proposed to address the breach

<<MUST item:Art.33:measures>>
_Why: Art.33.3d_

<<TEXT>>

## 5. Notified within 72 hours of becoming aware

<<MUST item:Art.33:timing>>
_Why: Art.33.1_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. If phased, reasons for delay and information provided in phases

<<SHOULD item:Art.33:phased>>
_Why: Art.33.4_

<<TEXT>>
