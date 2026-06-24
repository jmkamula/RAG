---
leaf_id: req:Art.12:transparency_program_review
control_ref: Art.12
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Transparency Program Review

> Annual verification that SLAs are being met, the register reflects all requests, refusal grounds are being applied consistently (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.12:rev_date>>
_Why: Periodic accountability_

<<TEXT>>

## 2. Reviewer identity (DPO + ops lead)

<<MUST item:Art.12:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. SLA compliance check — one-month response rate against in-scope requests

<<MUST item:Art.12:rev_sla_compliance>>
_Why: Art.12.3_

<<TEXT>>

## 4. Refusal-grounds audit — refused requests sampled for legitimate Art.12.5 grounds

<<MUST item:Art.12:rev_refusal_audit>>
_Why: Art.12.5 — defensibility_

<<TEXT>>

## 5. Channel coverage check — every in-scope channel is reaching the procedure (no orphan requests)

<<MUST item:Art.12:rev_channel_coverage>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.12:rev_next_date>>
_Why: Planning_

<<TEXT>>
