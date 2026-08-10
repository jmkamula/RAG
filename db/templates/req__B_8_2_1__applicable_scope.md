---
leaf_id: req:B.8.2.1:applicable_scope
control_ref: B.8.2.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Customer Engagements Scope

<<DOC_CONTROL>>

> The upstream — which customer engagements involve PII processing on the customer's behalf. Excludes non-PII services + own-controller services.

## What this template gives you

This template helps you clearly define which customer engagements involve processing personal data on behalf of your clients, making it easier to demonstrate compliance with privacy standards like ISO 27701.

## When to use it

Use this document whenever your services or projects involve handling personal information for customers, especially when your business profile or offerings change. Update it as needed to keep your scope accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required elements about your customer engagements.

## 1. PII-processor test per engagement — processing PII on customer's behalf under customer's instructions

<<MUST item:B.8.2.1:scope_pii_processor_test>>
_Why: GDPR Art.4.8_

<<GUIDANCE>>

<<TEXT>>

## 2. In-scope customer engagements enumerated

<<MUST item:B.8.2.1:scope_customer_list>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded engagements (own-controller services / non-PII services) with rationale

<<MUST item:B.8.2.1:scope_exclusions>>
_Why: Classification defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product line / new customer segment)

<<SHOULD item:B.8.2.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
