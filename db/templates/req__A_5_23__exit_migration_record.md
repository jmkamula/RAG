---
leaf_id: req:A.5.23:exit_migration_record
control_ref: A.5.23
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Cloud Service Exit / Migration Records

> A.5.23 requires exit strategies for cloud services and the CSP must support transition + data handover on termination. The exit-migration record evidences the actual execution: trigger captured, migration plan executed, data export and deletion confirmed, transition completed, with authoriser

<!-- TABLE-COLUMNS leaf:req:A.5.23:exit_migration_record -->
<!-- column: item:A.5.23:exit_trigger -->
<!-- column: item:A.5.23:exit_migration_plan -->
<!-- column: item:A.5.23:exit_data_deletion -->
<!-- column: item:A.5.23:exit_handover -->
<!-- column: item:A.5.23:exit_authoriser -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.23:exit_migration_record -->
| Exit Trigger | Exit Migration Plan | Exit Data Deletion | Exit Handover | Exit Authoriser |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.23:exit_migration_record -->

## Column guidance — what to fill in

### Exit Trigger

<<MUST item:A.5.23:exit_trigger>>
_Why: 27002:5.23h_

> _Standard text:_ Exit trigger captured (termination / replacement / CSP failure / business change)

### Exit Migration Plan

<<MUST item:A.5.23:exit_migration_plan>>
_Why: 27002:5.23h — transition_

> _Standard text:_ Migration plan executed (data export, dependency-rewiring, replacement service stood up)

### Exit Data Deletion

<<MUST item:A.5.23:exit_data_deletion>>
_Why: 27002:5.23 — handover_

> _Standard text:_ Data deletion confirmation from the CSP (attestation, log, or audit-trail evidence)

### Exit Handover

<<MUST item:A.5.23:exit_handover>>
_Why: 27002:5.23 — backup/handover_

> _Standard text:_ Handover of configuration + data evidence (backup downloaded, config preserved)

### Exit Authoriser

<<MUST item:A.5.23:exit_authoriser>>
_Why: Accountability_

> _Standard text:_ Authoriser of the exit (or of the delay + risk acceptance)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Exit Drill

<<SHOULD item:A.5.23:exit_drill>>
_Why: Continuity preparedness_

> _Standard text:_ Rolling exit-readiness drill (test exits without actually exiting, for critical services)

### Exit Plan Freshness

<<SHOULD item:A.5.23:exit_plan_freshness>>
_Why: Drift control_

> _Standard text:_ Per-service exit plan freshness target (re-test on agreement renewal or major service change)
