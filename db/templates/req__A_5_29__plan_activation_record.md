---
leaf_id: req:A.5.29:plan_activation_record
control_ref: A.5.29
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
table_shape: true
---

# Per-Activation Plan Record

> A.5.29 expects the plan to be ACTIVATED — not just written. The activation record evidences each invocation: activation id, type (real_disruption / scheduled_test / partial_drill), scenario triggered, scope of degradation, duration, gaps surfaced, restoration status, sign-off. One record per activation, covering BOTH real disruptions AND scheduled tests (type field distinguishes). Real activations cross-reference A.5.26 incident_register where the disruption was incident-driven

<!-- TABLE-COLUMNS leaf:req:A.5.29:plan_activation_record -->
<!-- column: item:A.5.29:act_activation_id -->
<!-- column: item:A.5.29:act_type -->
<!-- column: item:A.5.29:act_scenario_ref -->
<!-- column: item:A.5.29:act_scope -->
<!-- column: item:A.5.29:act_duration -->
<!-- column: item:A.5.29:act_gaps -->
<!-- column: item:A.5.29:act_restoration -->
<!-- column: item:A.5.29:act_signoff -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.29:plan_activation_record -->
| Act Activation Id | Act Type | Act Scenario Ref | Act Scope | Act Duration | Act Gaps | Act Restoration | Act Signoff |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.29:plan_activation_record -->

## Column guidance — what to fill in

### Act Activation Id

<<MUST item:A.5.29:act_activation_id>>
_Why: 27002:5.29 — traceability_

> _Standard text:_ Activation identifier per record (unique, sequenced)

### Act Type

<<MUST item:A.5.29:act_type>>
_Why: 27002:5.29 — coverage taxonomy_

> _Standard text:_ Activation type per record (real_disruption / scheduled_test / partial_drill / regulator_led_exercise)

### Act Scenario Ref

<<MUST item:A.5.29:act_scenario_ref>>
_Why: 27002:5.29 + cross-link to register_

> _Standard text:_ Triggered scenario reference per record (links to scenario register entry)

### Act Scope

<<MUST item:A.5.29:act_scope>>
_Why: 27002:5.29 — appropriate level verification_

> _Standard text:_ Scope of degradation per record (which controls dropped to fallback; which held at full; expected vs actual)

### Act Duration

<<MUST item:A.5.29:act_duration>>
_Why: 27002:5.29 — timeline_

> _Standard text:_ Duration per record (start time, end time, restoration time)

### Act Gaps

<<MUST item:A.5.29:act_gaps>>
_Why: 27002:5.29 — improvement feedback_

> _Standard text:_ Gaps surfaced per record (where the plan or controls fell short; severity per gap)

### Act Restoration

<<MUST item:A.5.29:act_restoration>>
_Why: 27002:5.29 — maintain after disruption ends_

> _Standard text:_ Restoration status per record (all controls back to normal; outstanding remediation items tracked)

### Act Signoff

<<MUST item:A.5.29:act_signoff>>
_Why: Accountability_

> _Standard text:_ Signoff per record (activation-authority + CISO; exec sponsor where tier-1 disruption)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Act Incident Link

<<SHOULD item:A.5.29:act_incident_link>>
_Why: Closing loop with [[A.5.26]]_

> _Standard text:_ Cross-reference to A.5.26 incident register where the activation was incident-driven (real disruptions tied to incidents)

### Act Lessons Feed

<<SHOULD item:A.5.29:act_lessons_feed>>
_Why: Closing loop with [[A.5.27]]_

> _Standard text:_ Lessons feed per record to A.5.27 lessons register where the activation surfaced patterns worth retaining beyond this control
