---
leaf_id: req:A.8.29:security_testing_procedure
control_ref: A.8.29
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Security Testing in Development and Acceptance Procedure

<<DOC_CONTROL>>

> A.8.29 requires security-testing processes defined + implemented. Procedure documents test types, lifecycle gates, acceptance criteria, defect handling, pen-test cadence. Per-test register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you document your security testing process during software development and acceptance, covering test types, lifecycle checkpoints, acceptance criteria, defect management, and penetration test scheduling.

## When to use it

Use this template when your organization needs to define or update its security testing procedures, especially if your activities match certain risk or compliance triggers. Review and refresh the document whenever your processes change or as needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this template from scratch, depending on the complexity of your testing processes and the amount of detail required for each section.

## 1. Test types (SAST / DAST / IAST / SCA / fuzzing / manual review / penetration testing) with applicability rules

<<MUST item:A.8.29:test_types>>
_Why: 27002:8.29 — security testing processes_

<<GUIDANCE>>

<<TEXT>>

## 2. Test gates in lifecycle (per-commit / pre-merge / pre-release / post-deployment)

<<MUST item:A.8.29:lifecycle_gates>>
_Why: 27002:8.29 — development life cycle_

<<GUIDANCE>>

<<TEXT>>

## 3. Acceptance criteria (severity thresholds that block release; documented exception authority)

<<MUST item:A.8.29:acceptance>>
_Why: 27002:8.29 — acceptance_

<<GUIDANCE>>

<<TEXT>>

## 4. Defect handling (creation / triage / fix / retest cycle with closure criteria)

<<MUST item:A.8.29:defect_handling>>
_Why: 27002:8.29 — implemented_

<<GUIDANCE>>

<<TEXT>>

## 5. Retesting requirement after remediation (no fix-without-retest)

<<MUST item:A.8.29:retesting>>
_Why: 27002:8.29 — implemented_

<<GUIDANCE>>

<<TEXT>>

## 6. Third-party penetration-testing cadence (annual + on significant change for customer-facing PII-touching apps; modern baseline)

<<MUST item:A.8.29:pen_test_cadence>>
_Why: Independent assurance (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Bug-bounty / responsible-disclosure programme

<<SHOULD item:A.8.29:bug_bounty>>
_Why: Continuous external testing_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
