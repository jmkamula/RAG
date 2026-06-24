---
leaf_id: req:A.8.29:test_register
control_ref: A.8.29
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Security Test Register

> Per-test record — test id, application, type, gate, outcome, findings count

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-test unique identifier

<<MUST item:A.8.29:reg_test_id>>
_Why: Auditability_

<<TEXT>>

## 2. Per-test application (cross-link to A.8.26 application register)

<<MUST item:A.8.29:reg_app>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-test type (matches procedure's test-types list)

<<MUST item:A.8.29:reg_type>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Per-test lifecycle gate (where in lifecycle this test ran)

<<MUST item:A.8.29:reg_gate>>
_Why: 27002:8.29 — development life cycle_

<<TEXT>>

## 5. Per-test outcome (pass / fail / waived-with-exception) + findings-count

<<MUST item:A.8.29:reg_outcome>>
_Why: 27002:8.29 — acceptance_

<<TEXT>>

## 6. Per-test artefact reference (report / scan output / pen-test deliverable retained)

<<MUST item:A.8.29:reg_artefact_ref>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-test external/internal flag (independent vs internal)

<<SHOULD item:A.8.29:reg_external>>
_Why: Assurance visibility_

<<TEXT>>
