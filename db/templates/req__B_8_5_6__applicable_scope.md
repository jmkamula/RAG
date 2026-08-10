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

<<DOC_CONTROL>>

> Every subcontractor that processes customer PII on the processor's behalf. Excludes suppliers who do not touch customer PII.

## What this template gives you

This template helps you clearly define which subcontractors handle customer personal data on your behalf, making it easier to demonstrate compliance with privacy requirements.

## When to use it

Use this document whenever you engage a subcontractor who processes customer PII for you, and update it whenever your list of such subcontractors changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, depending on how many subcontractors you need to include.

## 1. PII-processing test per supplier (does the supplier touch customer PII?)

<<MUST item:B.8.5.6:scope_pii_processing_test>>
_Why: §8.5.6 — process PII_

<<GUIDANCE>>

<<TEXT>>

## 2. In-scope subcontractors enumerated

<<MUST item:B.8.5.6:scope_subcontractor_list>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded suppliers (no PII contact) with rationale

<<MUST item:B.8.5.6:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new supplier onboarding / supplier scope change)

<<SHOULD item:B.8.5.6:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
