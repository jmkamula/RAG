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

<<DOC_CONTROL>>

> Art.33 requires notification to supervisory authority within 72 hours of becoming aware of a breach. Per-breach notification record is the canonical artefact. Sibling leaves: notification procedure (the how), applicable triggers scope, program review

## What this template gives you

This template helps you quickly prepare a formal notification to your data protection authority if you experience a personal data breach, ensuring you meet GDPR requirements and keep a clear record of each incident.

## When to use it

Use this document as soon as you become aware of a personal data breach, and submit it within 72 hours. Update or refresh the notification if new information becomes available.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this notification from scratch, as each required section takes around 10-15 minutes to fill in thoroughly.

## 1. Nature of the breach including categories and approximate number of data subjects

<<MUST item:Art.33:nature>>
_Why: Art.33.3a_

<<GUIDANCE>>

<<TEXT>>

## 2. Contact details of DPO or other contact point

<<MUST item:Art.33:dpo_contact>>
_Why: Art.33.3b_

<<GUIDANCE>>

<<TEXT>>

## 3. Likely consequences of the breach

<<MUST item:Art.33:consequences>>
_Why: Art.33.3c_

<<GUIDANCE>>

<<TEXT>>

## 4. Measures taken or proposed to address the breach

<<MUST item:Art.33:measures>>
_Why: Art.33.3d_

<<GUIDANCE>>

<<TEXT>>

## 5. Notified within 72 hours of becoming aware

<<MUST item:Art.33:timing>>
_Why: Art.33.1_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. If phased, reasons for delay and information provided in phases

<<SHOULD item:Art.33:phased>>
_Why: Art.33.4_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
