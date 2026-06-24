---
leaf_id: req:A.8.34:applicable_audit_testing_scope
control_ref: A.8.34
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Audit Testing Scope

> Upstream — what counts as audit testing on operational systems. Internal audit yes. External pen-test yes. Regulator inspection yes. Routine application testing under A.8.29

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Engagement types in scope (internal audit / third-party pen-test / regulator inspection / customer security assessment)

<<MUST item:A.8.34:scope_engagement_types>>
_Why: 27002:8.34 — appropriate_

<<TEXT>>

## 2. Operational systems in scope (drawn from A.5.9 asset register)

<<MUST item:A.8.34:scope_systems>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Exclusion rationale (routine application testing via A.8.29; non-operational test-bed work)

<<MUST item:A.8.34:scope_exclusions>>
_Why: Cross-control boundary_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new engagement type, new regulator audit power)

<<SHOULD item:A.8.34:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
