---
leaf_id: req:Art.27:representative_operations_record
control_ref: Art.27
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Representative Operations Record

> Per-interaction record of how the representative actually operates — handled queries from SAs and subjects, escalated to non-EU principal. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row interaction id

<<MUST item:Art.27:reg_interaction_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row originator (data subject / SA / other)

<<MUST item:Art.27:reg_originator>>
_Why: Art.27.4_

<<TEXT>>

## 3. Per-row topic (rights request routing, SA inquiry, breach communication)

<<MUST item:Art.27:reg_topic>>
_Why: Art.27.4_

<<TEXT>>

## 4. Per-row escalation to non-EU principal documented

<<MUST item:Art.27:reg_escalation>>
_Why: Defensibility_

<<TEXT>>

## 5. Per-row resolution date

<<MUST item:Art.27:reg_resolution_date>>
_Why: SLA tracking_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row SLA-met flag (response within Art.12.3 cascade)

<<SHOULD item:Art.27:reg_sla_met>>
_Why: Art.12 cross-link_

<<TEXT>>
