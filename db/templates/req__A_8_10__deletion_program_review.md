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
table_shape: true
---

# Periodic Deletion Program Review

> Annual verification — retention-triggered deletions completed within window, backup sweeps current, legal holds reviewed, GDPR erasure SLAs met (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.10:deletion_program_review -->
<!-- column: item:A.8.10:rev_date -->
<!-- column: item:A.8.10:rev_reviewer -->
<!-- column: item:A.8.10:rev_trigger_attainment -->
<!-- column: item:A.8.10:rev_backup_completeness -->
<!-- column: item:A.8.10:rev_legal_hold_inventory -->
<!-- column: item:A.8.10:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.10:deletion_program_review -->
| Rev Date | Rev Reviewer | Rev Trigger Attainment | Rev Backup Completeness | Rev Legal Hold Inventory | Rev Register Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.10:deletion_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.10:rev_date>>
_Why: 27002:8.10 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.8.10:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Data Protection + Infrastructure + Legal jointly)

### Rev Trigger Attainment

<<MUST item:A.8.10:rev_trigger_attainment>>
_Why: 27002:8.10 — when no longer required_

> _Standard text:_ Retention-trigger attainment check (deletions completed within configured window)

### Rev Backup Completeness

<<MUST item:A.8.10:rev_backup_completeness>>
_Why: Auditor-critical GDPR-defensibility_

> _Standard text:_ Backup-sweep completeness sample (no orphan copies surviving)

### Rev Legal Hold Inventory

<<MUST item:A.8.10:rev_legal_hold_inventory>>
_Why: Drift prevention_

> _Standard text:_ Legal-hold inventory re-confirmed / retired

### Rev Register Update

<<MUST item:A.8.10:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / scope

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.10:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
