---
leaf_id: req:Art.28:applicable_processors_scope
control_ref: Art.28
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processors Scope

> The upstream — what counts as a 'processor' (vs joint controller per Art.26, vs intra-group transfer). Operational definition + the controller-vs-processor decision tree

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Processor types in scope (cloud / SaaS providers, payroll, marketing platforms, analytics, support ticketing, etc.)

<<MUST item:Art.28:scope_processor_types>>
_Why: Coverage_

<<TEXT>>

## 2. Controller-vs-processor decision criteria (means & purpose test per EDPB guidelines)

<<MUST item:Art.28:scope_controller_vs_processor>>
_Why: Art.4(7-8) boundary_

<<TEXT>>

## 3. Out-of-scope vendors (those processing only their own data, intra-group with no GDPR transfer)

<<MUST item:Art.28:scope_exclusions>>
_Why: Defensible bounding_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new vendor onboarded, vendor service-shape change)

<<SHOULD item:Art.28:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
