---
leaf_id: req:A.8.33:applicable_test_data_scope
control_ref: A.8.33
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Test Information Scope

> Upstream — what counts as test information in this org. Includes synthetic / sampled / production-derived. Excludes pure-config (no data values); test fixtures committed to repos go under A.8.4

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Test-information classes in scope (synthetic-generated / production-derived / vendor-provided / user-contributed)

<<MUST item:A.8.33:scope_classes>>
_Why: 27002:8.33 — appropriate_

<<TEXT>>

## 2. Cross-link to A.8.11 masking — A.8.33 governs WHAT is selected, A.8.11 governs HOW it's transformed

<<MUST item:A.8.33:scope_a811_link>>
_Why: Cross-control boundary_

<<TEXT>>

## 3. Exclusion rationale (test fixtures in code governed via A.8.4; one-off load-test data with no real source)

<<MUST item:A.8.33:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new data class, new test pattern — e.g. AI-training data)

<<SHOULD item:A.8.33:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
