---
leaf_id: req:A.5.24:framework_exercise_record
control_ref: A.5.24
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Per-Exercise Framework Activation Record

> A.5.24 expects the framework to be exercised, not just written. The exercise record evidences each tabletop, simulation, live drill, or regulator-led exercise: exercise id, type, scenario, participants (link to IR team register), gaps identified, remediation actions, sign-off. One record per exercise, distinct from A.5.26's incident_closure_record (which tracks REAL incidents). This is per-DRILL evidence — the readiness proof

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Exercise identifier per record (unique, sequenced)

<<MUST item:A.5.24:ex_exercise_id>>
_Why: 27002:5.24 — traceability_

<<TEXT>>

## 2. Exercise type per record (tabletop / live_simulation / red_team_drill / regulator_led / partial_segment)

<<MUST item:A.5.24:ex_type>>
_Why: 27002:5.24 — preparation taxonomy_

<<TEXT>>

## 3. Scenario per record (what was simulated; severity; in-scope assets; threat-actor archetype)

<<MUST item:A.5.24:ex_scenario>>
_Why: 27002:5.24 — preparation depth_

<<TEXT>>

## 4. Participant list per record (links to IR team register entries; observers noted separately)

<<MUST item:A.5.24:ex_participants>>
_Why: 27002:5.24 + cross-link to register_

<<TEXT>>

## 5. Gaps identified per record (where the framework or team fell short; severity per gap)

<<MUST item:A.5.24:ex_gaps>>
_Why: 27002:5.24 — preparation feedback_

<<TEXT>>

## 6. Remediation actions captured per record (each gap → action item with owner + due date; feeds the program review)

<<MUST item:A.5.24:ex_remediation>>
_Why: 27002:5.24 — continuous improvement_

<<TEXT>>

## 7. Signoff per record (exercise lead + IR team lead + exec sponsor where high-tier exercise)

<<MUST item:A.5.24:ex_signoff>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External observer noted per record where an independent party (auditor, peer org, regulator) attended (raises defensibility)

<<SHOULD item:A.5.24:ex_external_observer>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Lessons feed per record to A.5.27 lessons register where the exercise surfaced patterns worth retaining beyond this control

<<SHOULD item:A.5.24:ex_lessons_feed>>
_Why: Closing loop with [[A.5.27]]_

<<TEXT>>
