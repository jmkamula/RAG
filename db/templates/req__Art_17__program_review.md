---
leaf_id: req:Art.17:program_review
control_ref: Art.17
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Art.17 Erasure Program Review

> Annual verification — SLAs met, backup erasure handled, Art.17.3 exception claims defensible, Art.17.2 public-disclosure actions taken where applicable (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.17:rev_date>>
_Why: Periodic_

<<TEXT>>

## 2. Reviewer identity (DPO + ops lead)

<<MUST item:Art.17:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. SLA compliance (Art.12.3 one-month)

<<MUST item:Art.17:rev_sla_compliance>>
_Why: Art.12.3_

<<TEXT>>

## 4. Backup-handling sample — backups actually purged on cycle, immutable records correctly flagged-not-erased

<<MUST item:Art.17:rev_backup_handling>>
_Why: Art.17.1_

<<TEXT>>

## 5. Art.17.3 exception sample — refused requests have defensible exception grounds

<<MUST item:Art.17:rev_exception_defensibility>>
_Why: Art.17.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.17:rev_next_date>>
_Why: Planning_

<<TEXT>>
