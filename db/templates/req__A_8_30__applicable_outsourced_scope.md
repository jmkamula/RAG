---
leaf_id: req:A.8.30:applicable_outsourced_scope
control_ref: A.8.30
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Outsourced Development Scope

> Upstream — what counts as 'outsourced development'. Custom-development contractor yes. Staff augmentation typically governed under A.6.5 + A.5.20. Pre-existing COTS via A.5.19/A.5.20

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Engagement types in scope (turn-key contract / dedicated team / co-development / pen-test-as-development)

<<MUST item:A.8.30:scope_engagement_types>>
_Why: 27002:8.30 — outsourced_

<<TEXT>>

## 2. Boundary with A.6.5 (staff augmentation governed there) + A.5.20 (general supplier security contract terms)

<<MUST item:A.8.30:scope_boundary_a65>>
_Why: Cross-control boundary_

<<TEXT>>

## 3. Exclusion rationale (e.g. open-source contributions accepted via A.8.4 repo governance)

<<MUST item:A.8.30:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new engagement type, new vendor model)

<<SHOULD item:A.8.30:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
