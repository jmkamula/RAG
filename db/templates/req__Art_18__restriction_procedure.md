---
leaf_id: req:Art.18:restriction_procedure
control_ref: Art.18
standard_id: GDPR:2016/679
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Restriction of Processing Procedure

<<DOC_CONTROL>>

> Art.18 gives subjects the right to restrict processing in 4 specific grounds (accuracy contested, unlawful but no erasure, no longer needed but subject needs for claims, objection pending). Procedure as primary; restriction register, applicable grounds scope, program review are siblings

## What this template gives you

This template helps you document how your organization handles requests from individuals to restrict the processing of their personal data, ensuring you meet GDPR Article 18 requirements.

## When to use it

Use this whenever you process personal data and need a clear, up-to-date procedure for handling restriction requests, especially as these obligations always apply and should be reviewed whenever your practices change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the complexity of your data processing and the number of restriction cases you need to record.

## 1. Intake channel via Art.12 procedure (rights portal)

<<MUST item:Art.18:intake_channel>>
_Why: Art.12.2_

<<GUIDANCE>>

<<TEXT>>

## 2. Assessment of which Art.18.1 ground applies (a-d) recorded per request

<<MUST item:Art.18:grounds_assessment>>
_Why: Art.18.1_

<<GUIDANCE>>

<<TEXT>>

## 3. Technical restriction mechanism (flag in data store / move to restricted partition / temporary access lock)

<<MUST item:Art.18:restriction_mechanism>>
_Why: Art.18.2 — only store, lawful claims, public interest_

<<GUIDANCE>>

<<TEXT>>

## 4. Pre-lift communication to subject before restriction is lifted (Art.18.3)

<<MUST item:Art.18:lift_communication>>
_Why: Art.18.3_

<<GUIDANCE>>

<<TEXT>>

## 5. Notification to recipients per Art.19

<<MUST item:Art.18:recipient_notification>>
_Why: Art.19_

<<GUIDANCE>>

<<TEXT>>

## 6. One-month response deadline

<<MUST item:Art.18:response_deadline>>
_Why: Art.12.3_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Audit trail proving restricted records are stored-only (no further processing other than the Art.18.2 exceptions)

<<SHOULD item:Art.18:storage_only_audit>>
_Why: Art.18.2_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
