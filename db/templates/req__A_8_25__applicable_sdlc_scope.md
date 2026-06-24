---
leaf_id: req:A.8.25:applicable_sdlc_scope
control_ref: A.8.25
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable SDLC Scope

> Upstream — what counts as in-scope development. In-house product development yes. Major internal tooling typically yes. Quick scripts / one-off automation typically not. Outsourced via A.8.30

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Development classes in scope (in-house product / major internal tooling / API-as-product / customer-facing add-ons)

<<MUST item:A.8.25:scope_classes>>
_Why: 27002:8.25 — appropriate_

<<TEXT>>

## 2. Exclusion rationale (quick scripts / throwaway automation / outsourced governed via A.8.30)

<<MUST item:A.8.25:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

## 3. Proportionality rules per project class (lightweight gates for low-risk; full SDLC for customer-facing PII-touching)

<<MUST item:A.8.25:scope_proportionality>>
_Why: 27002:8.25 — proportionate_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new product line, new development paradigm — e.g. AI/ML)

<<SHOULD item:A.8.25:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
