---
leaf_id: req:A.8.10:deletion_program_review
control_ref: A.8.10
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Deletion Program Review

> Annual verification — retention-triggered deletions completed within window, backup sweeps current, legal holds reviewed, GDPR erasure SLAs met (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.10:rev_date>>
_Why: 27002:8.10 — periodic_

<<TEXT>>

## 2. Reviewer identity (Data Protection + Infrastructure + Legal jointly)

<<MUST item:A.8.10:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Retention-trigger attainment check (deletions completed within configured window)

<<MUST item:A.8.10:rev_trigger_attainment>>
_Why: 27002:8.10 — when no longer required_

<<TEXT>>

## 4. Backup-sweep completeness sample (no orphan copies surviving)

<<MUST item:A.8.10:rev_backup_completeness>>
_Why: Auditor-critical GDPR-defensibility_

<<TEXT>>

## 5. Legal-hold inventory re-confirmed / retired

<<MUST item:A.8.10:rev_legal_hold_inventory>>
_Why: Drift prevention_

<<TEXT>>

## 6. Findings propagated to procedure / scope

<<MUST item:A.8.10:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.10:rev_next_date>>
_Why: Planning_

<<TEXT>>
