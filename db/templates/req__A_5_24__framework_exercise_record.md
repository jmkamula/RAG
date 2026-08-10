---
leaf_id: req:A.5.24:framework_exercise_record
control_ref: A.5.24
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Per-Exercise Framework Activation Record

<<DOC_CONTROL>>

> A.5.24 expects the framework to be exercised, not just written. The exercise record evidences each tabletop, simulation, live drill, or regulator-led exercise: exercise id, type, scenario, participants (link to IR team register), gaps identified, remediation actions, sign-off. One record per exercise, distinct from A.5.26's incident_closure_record (which tracks REAL incidents). This is per-DRILL evidence — the readiness proof

<!-- TABLE-COLUMNS leaf:req:A.5.24:framework_exercise_record -->
<!-- column: item:A.5.24:ex_exercise_id -->
<!-- column: item:A.5.24:ex_type -->
<!-- column: item:A.5.24:ex_scenario -->
<!-- column: item:A.5.24:ex_participants -->
<!-- column: item:A.5.24:ex_gaps -->
<!-- column: item:A.5.24:ex_remediation -->
<!-- column: item:A.5.24:ex_signoff -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document every time you test your incident response framework, whether through tabletop exercises, simulations, live drills, or regulator-led activities. It provides clear proof of your readiness and compliance with ISO 27001 requirements.

## When to use it

Use this template whenever you conduct a planned exercise of your incident response framework, and update it as needed for each new drill or test. It should be completed for every exercise, not just real incidents.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours filling out this record for each exercise, depending on the number of details and participants involved.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.24:framework_exercise_record -->
| Ex Exercise Id | Ex Type | Ex Scenario | Ex Participants | Ex Gaps | Ex Remediation | Ex Signoff |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.24:framework_exercise_record -->

## Column guidance — what to fill in

### Ex Exercise Id

<<MUST item:A.5.24:ex_exercise_id>>
_Why: 27002:5.24 — traceability_

> _Standard text:_ Exercise identifier per record (unique, sequenced)

<<GUIDANCE>>

### Ex Type

<<MUST item:A.5.24:ex_type>>
_Why: 27002:5.24 — preparation taxonomy_

> _Standard text:_ Exercise type per record (tabletop / live_simulation / red_team_drill / regulator_led / partial_segment)

<<GUIDANCE>>

### Ex Scenario

<<MUST item:A.5.24:ex_scenario>>
_Why: 27002:5.24 — preparation depth_

> _Standard text:_ Scenario per record (what was simulated; severity; in-scope assets; threat-actor archetype)

<<GUIDANCE>>

### Ex Participants

<<MUST item:A.5.24:ex_participants>>
_Why: 27002:5.24 + cross-link to register_

> _Standard text:_ Participant list per record (links to IR team register entries; observers noted separately)

<<GUIDANCE>>

### Ex Gaps

<<MUST item:A.5.24:ex_gaps>>
_Why: 27002:5.24 — preparation feedback_

> _Standard text:_ Gaps identified per record (where the framework or team fell short; severity per gap)

<<GUIDANCE>>

### Ex Remediation

<<MUST item:A.5.24:ex_remediation>>
_Why: 27002:5.24 — continuous improvement_

> _Standard text:_ Remediation actions captured per record (each gap → action item with owner + due date; feeds the program review)

<<GUIDANCE>>

### Ex Signoff

<<MUST item:A.5.24:ex_signoff>>
_Why: Accountability_

> _Standard text:_ Signoff per record (exercise lead + IR team lead + exec sponsor where high-tier exercise)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Ex External Observer

<<SHOULD item:A.5.24:ex_external_observer>>
_Why: Audit defensibility_

> _Standard text:_ External observer noted per record where an independent party (auditor, peer org, regulator) attended (raises defensibility)

<<GUIDANCE>>

### Ex Lessons Feed

<<SHOULD item:A.5.24:ex_lessons_feed>>
_Why: Closing loop with [[A.5.27]]_

> _Standard text:_ Lessons feed per record to A.5.27 lessons register where the exercise surfaced patterns worth retaining beyond this control

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
