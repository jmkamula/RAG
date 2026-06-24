---
leaf_id: req:Art.10:criminal_data_program_review
control_ref: Art.10
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Criminal Data Program Review

> Annual verification that every Art.10 activity still has a current Member State law basis, safeguards remain in force, retention limits are being honoured (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.10:rev_date>>
_Why: Periodic accountability_

<<TEXT>>

## 2. Reviewer identity (DPO + legal counsel)

<<MUST item:Art.10:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Member State law currency — every cited law still in force; any new MS authorisations swept in

<<MUST item:Art.10:rev_law_currency>>
_Why: Currency_

<<TEXT>>

## 4. Retention audit — past-retention-limit records purged

<<MUST item:Art.10:rev_retention_audit>>
_Why: Art.10 — appropriate safeguards_

<<TEXT>>

## 5. Access audit — restricted-access requirements being enforced (no broad access to criminal-data stores)

<<MUST item:Art.10:rev_access_audit>>
_Why: Art.10_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.10:rev_next_date>>
_Why: Planning_

<<TEXT>>
