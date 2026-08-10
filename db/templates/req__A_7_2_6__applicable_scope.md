---
leaf_id: req:A.7.2.6:applicable_scope
control_ref: A.7.2.6
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processor Engagements Scope

<<DOC_CONTROL>>

> The upstream — which supplier relationships qualify as 'PII processor' (as opposed to independent controller / vendor / integration). Correct classification determines whether A.7.2.6 or A.7.2.7 applies.

## What this template gives you

This template helps you clearly identify which of your suppliers are acting as personal data processors, making it easier to apply the correct privacy controls and meet ISO 27701 requirements.

## When to use it

Use this document whenever you need to determine if a supplier relationship involves processing personal data on your behalf, especially when your business profile or supplier list changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to provide details for three required elements.

## 1. Processor test — supplier processes PII on org's behalf under org's instructions (not for its own purposes)

<<MUST item:A.7.2.6:scope_processor_test>>
_Why: GDPR Art.4.8_

<<GUIDANCE>>

<<TEXT>>

## 2. In-scope processors enumerated with classification rationale

<<MUST item:A.7.2.6:scope_processor_list>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded relationships (independent controllers / joint controllers → A.7.2.7 / non-PII vendors)

<<MUST item:A.7.2.6:scope_exclusions>>
_Why: Classification defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new supplier onboarding / supplier role change)

<<SHOULD item:A.7.2.6:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
