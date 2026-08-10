---
leaf_id: req:B.8.2.3:applicable_scope
control_ref: B.8.2.3
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Marketing Activities Scope

<<DOC_CONTROL>>

> The upstream — which processor activities could touch customer PII for marketing/advertising purposes. For most processors, this scope is empty (customer PII strictly siloed from marketing).

## What this template gives you

This template helps you clearly define which of your marketing or advertising activities, if any, could involve customer personal data. It’s useful for showing how you keep marketing separate from customer information.

## When to use it

Use this document if your organization’s activities might involve customer data for marketing or advertising, or when your privacy profile changes. Update it whenever your processes or data flows change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes to complete this from scratch, as you’ll need to describe three required elements about your marketing data practices.

## 1. Marketing channels enumerated (email marketing / retargeting / in-product prompts / third-party ad platforms)

<<MUST item:B.8.2.3:scope_marketing_channels>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Customer-PII isolation posture (marketing systems use own-controller data only)

<<MUST item:B.8.2.3:scope_pii_isolation>>
_Why: §8.2.3 — default prohibition_

<<GUIDANCE>>

<<TEXT>>

## 3. Documented exceptions (empty for most processors) with rationale

<<MUST item:B.8.2.3:scope_exceptions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new marketing programme launched / new customer permit request)

<<SHOULD item:B.8.2.3:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
