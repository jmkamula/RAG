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

> A.8.29 requires security-testing processes defined + implemented. Procedure documents test types, lifecycle gates, acceptance criteria, defect handling, pen-test cadence. Per-test register, applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Test types (SAST / DAST / IAST / SCA / fuzzing / manual review / penetration testing) with applicability rules

<<MUST item:A.8.29:test_types>>
_Why: 27002:8.29 — security testing processes_

<<TEXT>>

## 2. Test gates in lifecycle (per-commit / pre-merge / pre-release / post-deployment)

<<MUST item:A.8.29:lifecycle_gates>>
_Why: 27002:8.29 — development life cycle_

<<TEXT>>

## 3. Acceptance criteria (severity thresholds that block release; documented exception authority)

<<MUST item:A.8.29:acceptance>>
_Why: 27002:8.29 — acceptance_

<<TEXT>>

## 4. Defect handling (creation / triage / fix / retest cycle with closure criteria)

<<MUST item:A.8.29:defect_handling>>
_Why: 27002:8.29 — implemented_

<<TEXT>>

## 5. Retesting requirement after remediation (no fix-without-retest)

<<MUST item:A.8.29:retesting>>
_Why: 27002:8.29 — implemented_

<<TEXT>>

## 6. Third-party penetration-testing cadence (annual + on significant change for customer-facing PII-touching apps; modern baseline)

<<MUST item:A.8.29:pen_test_cadence>>
_Why: Independent assurance (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Bug-bounty / responsible-disclosure programme

<<SHOULD item:A.8.29:bug_bounty>>
_Why: Continuous external testing_

<<TEXT>>
