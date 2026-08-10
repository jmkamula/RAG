---
leaf_id: req:A.7.2.4:applicable_scope
control_ref: A.7.2.4
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Consent Records Scope

<<DOC_CONTROL>>

> The upstream — which activities produce recordable consent events. Excludes non-consent bases (contract/legal obligation processing doesn't produce consent records).

## What this template gives you

This template helps you clearly define which activities in your organization generate consent records, making it easier to demonstrate compliance with privacy standards like ISO 27701.

## When to use it

Use this document whenever your data processing activities may involve collecting or recording consent, especially when your operations or new projects match specific privacy triggers. Update it as your processes change or new activities arise.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required elements and consider one recommended detail.

## 1. In-scope activities enumerated (map to A.7.2.3 consent-required list)

<<MUST item:A.7.2.4:scope_consent_activities>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Consent record retention (until withdrawn + statutory retention period for demonstration)

<<MUST item:A.7.2.4:scope_retention>>
_Why: §7.2.4 — provide on request_

<<GUIDANCE>>

<<TEXT>>

## 3. Non-consent activities excluded with rationale (contract necessity / legal obligation basis)

<<MUST item:A.7.2.4:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new consent-basis activity launched)

<<SHOULD item:A.7.2.4:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
