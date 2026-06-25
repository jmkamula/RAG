---
leaf_id: req:A.8.13:backup_program_review
control_ref: A.8.13
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Backup Program Review

> Annual verification — restore-test attainment per RPO tier, scope completeness, encryption + immutability posture (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.13:backup_program_review -->
<!-- column: item:A.8.13:rev_date -->
<!-- column: item:A.8.13:rev_reviewer -->
<!-- column: item:A.8.13:rev_test_attainment -->
<!-- column: item:A.8.13:rev_scope_completeness -->
<!-- column: item:A.8.13:rev_threat_posture -->
<!-- column: item:A.8.13:rev_procedure_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.13:backup_program_review -->
| Rev Date | Rev Reviewer | Rev Test Attainment | Rev Scope Completeness | Rev Threat Posture | Rev Procedure Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.13:backup_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.13:rev_date>>
_Why: 27002:8.13 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.8.13:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Backup Operations + Infrastructure + InfoSec)

### Rev Test Attainment

<<MUST item:A.8.13:rev_test_attainment>>
_Why: 27002:8.13 — regularly tested_

> _Standard text:_ Restore-test attainment per tier (cadence met, RPO met)

### Rev Scope Completeness

<<MUST item:A.8.13:rev_scope_completeness>>
_Why: 27002:8.13 — maintained_

> _Standard text:_ Scope-completeness check (new in-scope system covered)

### Rev Threat Posture

<<MUST item:A.8.13:rev_threat_posture>>
_Why: Modern resilience_

> _Standard text:_ Threat-posture review (ransomware-resilience: immutability / air-gap / 3-2-1 still adequate)

### Rev Procedure Update

<<MUST item:A.8.13:rev_procedure_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / scope

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.13:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
