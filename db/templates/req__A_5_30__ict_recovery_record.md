---
leaf_id: req:A.5.30:ict_recovery_record
control_ref: A.5.30
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
---

# Per-Recovery Event Record

> A.5.30 expects recovery to be EVIDENCED — not just promised. The recovery record evidences each event: recovery id, type (real_recovery / scheduled_test / partial_drill), services in scope, RTO/RPO targets, actual recovery time, success status, gaps surfaced, sign-off. HYBRID variant (like A.5.29) — covers BOTH real recovery events AND scheduled tests via type field. Real recoveries cross-reference A.5.29 activation_record (BCP-driven events) and A.5.26 incident_register (incident-driven recovery)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Recovery event identifier per record (unique, sequenced)

<<MUST item:A.5.30:rec_recovery_id>>
_Why: 27002:5.30 — traceability_

<<TEXT>>

## 2. Recovery type per record (real_recovery / scheduled_test / partial_drill / chaos_engineering_test)

<<MUST item:A.5.30:rec_type>>
_Why: 27002:5.30 — coverage taxonomy_

<<TEXT>>

## 3. Services in scope per record (links to service register entries)

<<MUST item:A.5.30:rec_services>>
_Why: 27002:5.30 + cross-link to register_

<<TEXT>>

## 4. RTO target per record (what was committed)

<<MUST item:A.5.30:rec_rto_target>>
_Why: 27002:5.30 — objectives_

<<TEXT>>

## 5. Actual recovery time per record (drives the RTO-met calculation; gap to target if missed)

<<MUST item:A.5.30:rec_actual_time>>
_Why: 27002:5.30 — objectives verification_

<<TEXT>>

## 6. Success status per record (rto_met / rto_missed_with_reason / partial_recovery_acceptable / failed)

<<MUST item:A.5.30:rec_success_status>>
_Why: 27002:5.30 — auditor-critical objective achievement proof_

<<TEXT>>

## 7. Gaps surfaced per record (where recovery fell short; severity per gap)

<<MUST item:A.5.30:rec_gaps>>
_Why: 27002:5.30 — improvement feedback_

<<TEXT>>

## 8. Signoff per record (recovery owner + BCP-program owner; exec sponsor where critical-service real recovery)

<<MUST item:A.5.30:rec_signoff>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-reference to A.5.29 plan_activation_record where this recovery was BCP-driven (closes loop)

<<SHOULD item:A.5.30:rec_disruption_link>>
_Why: Closing loop with [[A.5.29]]_

<<TEXT>>

### 2. Lessons feed per record to A.5.27 lessons register where recovery surfaced patterns worth retaining beyond this control

<<SHOULD item:A.5.30:rec_lessons_feed>>
_Why: Closing loop with [[A.5.27]]_

<<TEXT>>
