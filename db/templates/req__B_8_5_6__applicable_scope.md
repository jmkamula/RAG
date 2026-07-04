---
leaf_id: req:B.8.5.6:applicable_scope
control_ref: B.8.5.6
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Subcontractor Scope

> Every subcontractor that processes customer PII on the processor's behalf. Excludes suppliers who do not touch customer PII.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. PII-processing test per supplier (does the supplier touch customer PII?)

<<MUST item:B.8.5.6:scope_pii_processing_test>>
_Why: §8.5.6 — process PII_

<<TEXT>>

## 2. In-scope subcontractors enumerated

<<MUST item:B.8.5.6:scope_subcontractor_list>>
_Why: Coverage_

<<TEXT>>

## 3. Excluded suppliers (no PII contact) with rationale

<<MUST item:B.8.5.6:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new supplier onboarding / supplier scope change)

<<SHOULD item:B.8.5.6:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
