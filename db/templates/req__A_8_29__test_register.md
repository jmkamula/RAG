---
leaf_id: req:A.8.29:test_register
control_ref: A.8.29
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Security Test Register

<<DOC_CONTROL>>

> Per-test record — test id, application, type, gate, outcome, findings count

<!-- TABLE-COLUMNS leaf:req:A.8.29:test_register -->
<!-- column: item:A.8.29:reg_test_id -->
<!-- column: item:A.8.29:reg_app -->
<!-- column: item:A.8.29:reg_type -->
<!-- column: item:A.8.29:reg_gate -->
<!-- column: item:A.8.29:reg_outcome -->
<!-- column: item:A.8.29:reg_artefact_ref -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of each security test you conduct, including key details like test ID, application, type, and findings. It's designed to support ISO 27001 compliance and make tracking easier.

## When to use it

Use this register whenever your organization’s profile matches specific security testing requirements, and update it as needed whenever new tests are performed or existing records change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes entering the initial required details for each test, with additional time needed for each new test you add to the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.29:test_register -->
| Reg Test Id | Reg App | Reg Type | Reg Gate | Reg Outcome | Reg Artefact Ref |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.29:test_register -->

## Column guidance — what to fill in

### Reg Test Id

<<MUST item:A.8.29:reg_test_id>>
_Why: Auditability_

> _Standard text:_ Per-test unique identifier

<<GUIDANCE>>

### Reg App

<<MUST item:A.8.29:reg_app>>
_Why: Cross-control coherence_

> _Standard text:_ Per-test application (cross-link to A.8.26 application register)

<<GUIDANCE>>

### Reg Type

<<MUST item:A.8.29:reg_type>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-test type (matches procedure's test-types list)

<<GUIDANCE>>

### Reg Gate

<<MUST item:A.8.29:reg_gate>>
_Why: 27002:8.29 — development life cycle_

> _Standard text:_ Per-test lifecycle gate (where in lifecycle this test ran)

<<GUIDANCE>>

### Reg Outcome

<<MUST item:A.8.29:reg_outcome>>
_Why: 27002:8.29 — acceptance_

> _Standard text:_ Per-test outcome (pass / fail / waived-with-exception) + findings-count

<<GUIDANCE>>

### Reg Artefact Ref

<<MUST item:A.8.29:reg_artefact_ref>>
_Why: Defensibility_

> _Standard text:_ Per-test artefact reference (report / scan output / pen-test deliverable retained)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg External

<<SHOULD item:A.8.29:reg_external>>
_Why: Assurance visibility_

> _Standard text:_ Per-test external/internal flag (independent vs internal)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
