---
leaf_id: req:A.5.30:ict_recovery_record
control_ref: A.5.30
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
table_shape: true
---

# Per-Recovery Event Record

<<DOC_CONTROL>>

> A.5.30 expects recovery to be EVIDENCED — not just promised. The recovery record evidences each event: recovery id, type (real_recovery / scheduled_test / partial_drill), services in scope, RTO/RPO targets, actual recovery time, success status, gaps surfaced, sign-off. HYBRID variant (like A.5.29) — covers BOTH real recovery events AND scheduled tests via type field. Real recoveries cross-reference A.5.29 activation_record (BCP-driven events) and A.5.26 incident_register (incident-driven recovery)

<!-- TABLE-COLUMNS leaf:req:A.5.30:ict_recovery_record -->
<!-- column: item:A.5.30:rec_recovery_id -->
<!-- column: item:A.5.30:rec_type -->
<!-- column: item:A.5.30:rec_services -->
<!-- column: item:A.5.30:rec_rto_target -->
<!-- column: item:A.5.30:rec_actual_time -->
<!-- column: item:A.5.30:rec_success_status -->
<!-- column: item:A.5.30:rec_gaps -->
<!-- column: item:A.5.30:rec_signoff -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document every recovery event, whether it's a real incident or a scheduled test, capturing key details like recovery times, outcomes, and any issues found. It provides clear evidence that your recovery processes are working as expected.

## When to use it

Use this template whenever you complete a recovery event, including both actual recoveries and planned tests or drills. Update it as needed, each time a new recovery event occurs in your environment.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing a new entry from scratch, since each required detail takes 10–15 minutes to document. Additional time may be needed for multiple events.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.30:ict_recovery_record -->
| Rec Recovery Id | Rec Type | Rec Services | Rec Rto Target | Rec Actual Time | Rec Success Status | Rec Gaps | Rec Signoff |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.30:ict_recovery_record -->

## Column guidance — what to fill in

### Rec Recovery Id

<<MUST item:A.5.30:rec_recovery_id>>
_Why: 27002:5.30 — traceability_

> _Standard text:_ Recovery event identifier per record (unique, sequenced)

<<GUIDANCE>>

### Rec Type

<<MUST item:A.5.30:rec_type>>
_Why: 27002:5.30 — coverage taxonomy_

> _Standard text:_ Recovery type per record (real_recovery / scheduled_test / partial_drill / chaos_engineering_test)

<<GUIDANCE>>

### Rec Services

<<MUST item:A.5.30:rec_services>>
_Why: 27002:5.30 + cross-link to register_

> _Standard text:_ Services in scope per record (links to service register entries)

<<GUIDANCE>>

### Rec Rto Target

<<MUST item:A.5.30:rec_rto_target>>
_Why: 27002:5.30 — objectives_

> _Standard text:_ RTO target per record (what was committed)

<<GUIDANCE>>

### Rec Actual Time

<<MUST item:A.5.30:rec_actual_time>>
_Why: 27002:5.30 — objectives verification_

> _Standard text:_ Actual recovery time per record (drives the RTO-met calculation; gap to target if missed)

<<GUIDANCE>>

### Rec Success Status

<<MUST item:A.5.30:rec_success_status>>
_Why: 27002:5.30 — auditor-critical objective achievement proof_

> _Standard text:_ Success status per record (rto_met / rto_missed_with_reason / partial_recovery_acceptable / failed)

<<GUIDANCE>>

### Rec Gaps

<<MUST item:A.5.30:rec_gaps>>
_Why: 27002:5.30 — improvement feedback_

> _Standard text:_ Gaps surfaced per record (where recovery fell short; severity per gap)

<<GUIDANCE>>

### Rec Signoff

<<MUST item:A.5.30:rec_signoff>>
_Why: Accountability_

> _Standard text:_ Signoff per record (recovery owner + BCP-program owner; exec sponsor where critical-service real recovery)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rec Disruption Link

<<SHOULD item:A.5.30:rec_disruption_link>>
_Why: Closing loop with [[A.5.29]]_

> _Standard text:_ Cross-reference to A.5.29 plan_activation_record where this recovery was BCP-driven (closes loop)

<<GUIDANCE>>

### Rec Lessons Feed

<<SHOULD item:A.5.30:rec_lessons_feed>>
_Why: Closing loop with [[A.5.27]]_

> _Standard text:_ Lessons feed per record to A.5.27 lessons register where recovery surfaced patterns worth retaining beyond this control

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
