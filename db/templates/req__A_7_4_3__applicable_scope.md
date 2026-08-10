---
leaf_id: req:A.7.4.3:applicable_scope
control_ref: A.7.4.3
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Accuracy Contexts Scope

<<DOC_CONTROL>>

> The upstream — which PII categories need active accuracy management (contact details + address + payment info + employment status) vs which are relatively static.

## What this template gives you

This template helps you clearly define which types of personal information in your systems need regular accuracy checks, such as contact details, addresses, payment information, and employment status, versus those that rarely change.

## When to use it

Use this document whenever your organization’s profile matches certain privacy triggers that require you to manage the accuracy of personal data, and update it whenever there are changes to your data handling practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you’ll need to address three required points and consider one recommended detail.

## 1. High-churn field categories (contact details / address / employment / preferences)

<<MUST item:A.7.4.3:scope_high_churn_fields>>
_Why: Prioritisation_

<<GUIDANCE>>

<<TEXT>>

## 2. Low-churn field categories (date of birth / national ID / immutable identifiers)

<<MUST item:A.7.4.3:scope_low_churn_fields>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. Verification source map (postal address vs national registry vs subject self-serve)

<<MUST item:A.7.4.3:scope_verification_sources>>
_Why: Practicability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new PII category / new verification source)

<<SHOULD item:A.7.4.3:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
