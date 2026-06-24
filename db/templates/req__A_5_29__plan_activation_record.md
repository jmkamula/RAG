---
leaf_id: req:A.5.29:plan_activation_record
control_ref: A.5.29
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
---

# Per-Activation Plan Record

> A.5.29 expects the plan to be ACTIVATED — not just written. The activation record evidences each invocation: activation id, type (real_disruption / scheduled_test / partial_drill), scenario triggered, scope of degradation, duration, gaps surfaced, restoration status, sign-off. One record per activation, covering BOTH real disruptions AND scheduled tests (type field distinguishes). Real activations cross-reference A.5.26 incident_register where the disruption was incident-driven

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Activation identifier per record (unique, sequenced)

<<MUST item:A.5.29:act_activation_id>>
_Why: 27002:5.29 — traceability_

<<TEXT>>

## 2. Activation type per record (real_disruption / scheduled_test / partial_drill / regulator_led_exercise)

<<MUST item:A.5.29:act_type>>
_Why: 27002:5.29 — coverage taxonomy_

<<TEXT>>

## 3. Triggered scenario reference per record (links to scenario register entry)

<<MUST item:A.5.29:act_scenario_ref>>
_Why: 27002:5.29 + cross-link to register_

<<TEXT>>

## 4. Scope of degradation per record (which controls dropped to fallback; which held at full; expected vs actual)

<<MUST item:A.5.29:act_scope>>
_Why: 27002:5.29 — appropriate level verification_

<<TEXT>>

## 5. Duration per record (start time, end time, restoration time)

<<MUST item:A.5.29:act_duration>>
_Why: 27002:5.29 — timeline_

<<TEXT>>

## 6. Gaps surfaced per record (where the plan or controls fell short; severity per gap)

<<MUST item:A.5.29:act_gaps>>
_Why: 27002:5.29 — improvement feedback_

<<TEXT>>

## 7. Restoration status per record (all controls back to normal; outstanding remediation items tracked)

<<MUST item:A.5.29:act_restoration>>
_Why: 27002:5.29 — maintain after disruption ends_

<<TEXT>>

## 8. Signoff per record (activation-authority + CISO; exec sponsor where tier-1 disruption)

<<MUST item:A.5.29:act_signoff>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-reference to A.5.26 incident register where the activation was incident-driven (real disruptions tied to incidents)

<<SHOULD item:A.5.29:act_incident_link>>
_Why: Closing loop with [[A.5.26]]_

<<TEXT>>

### 2. Lessons feed per record to A.5.27 lessons register where the activation surfaced patterns worth retaining beyond this control

<<SHOULD item:A.5.29:act_lessons_feed>>
_Why: Closing loop with [[A.5.27]]_

<<TEXT>>
