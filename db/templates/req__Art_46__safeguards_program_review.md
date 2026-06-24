---
leaf_id: req:Art.46:safeguards_program_review
control_ref: Art.46
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Safeguards Program Review

> Annual verification — SCCs on current version, TIAs current, supplementary measures effective, vendor compliance attested (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.46:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + legal counsel)

<<MUST item:Art.46:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. SCCs version audit — any old-version SCCs identified for migration

<<MUST item:Art.46:rev_sccs_version>>
_Why: Commission Decision 2021/914_

<<TEXT>>

## 4. TIA currency — TIAs refreshed where third-country law has changed materially

<<MUST item:Art.46:rev_tia_currency>>
_Why: Schrems II — ongoing duty_

<<TEXT>>

## 5. Supplementary measures audit — applied measures (encryption keys, pseudonymisation, etc.) actually in place at vendor

<<MUST item:Art.46:rev_supplementary_audit>>
_Why: EDPB 01/2020_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.46:rev_next_date>>
_Why: Planning_

<<TEXT>>
