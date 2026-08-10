---
leaf_id: req:A.7.4.7:applicable_scope
control_ref: A.7.4.7
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Retention Contexts Scope

<<DOC_CONTROL>>

> The upstream — which PII categories × activity combinations require dedicated retention schedules vs which follow defaults.

## What this template gives you

This template helps you clearly identify which types of personal information and activities need special retention rules, and which can follow your standard retention policy.

## When to use it

Use this document whenever your data handling activities or personal information types change in a way that could affect retention requirements. Update it as needed to stay current with your practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as each required section takes around 10 to 15 minutes to fill in thoughtfully.

## 1. Regulated PII categories (health / financial / employment / tax / other jurisdiction-specific)

<<MUST item:A.7.4.7:scope_regulated_data>>
_Why: §7.4.7 — legal + regulatory_

<<GUIDANCE>>

<<TEXT>>

## 2. Business PII categories with business retention rationale

<<MUST item:A.7.4.7:scope_business_data>>
_Why: §7.4.7 — business requirements_

<<GUIDANCE>>

<<TEXT>>

## 3. Default retention period for uncategorised PII

<<MUST item:A.7.4.7:scope_default_period>>
_Why: Comprehensiveness_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new regulation / new business requirement)

<<SHOULD item:A.7.4.7:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
