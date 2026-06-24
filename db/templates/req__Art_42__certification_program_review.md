---
leaf_id: req:Art.42:certification_program_review
control_ref: Art.42
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Certification Program Review

> Annual verification — certifications current, surveillance audits passing, renewal on track (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.42:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + executive sponsor)

<<MUST item:Art.42:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Validity audit — every active certification still in validity period; renewal in flight where approaching expiry

<<MUST item:Art.42:rev_validity_audit>>
_Why: Art.42.7_

<<TEXT>>

## 4. Surveillance status — most-recent surveillance audit outcome reviewed

<<MUST item:Art.42:rev_surveillance_status>>
_Why: Lifecycle_

<<TEXT>>

## 5. Business case recheck — certification still providing value (transfer enablement / customer requirement / market position)

<<MUST item:Art.42:rev_business_case_recheck>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.42:rev_next_date>>
_Why: Planning_

<<TEXT>>
