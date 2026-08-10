---
leaf_id: req:B.8.2.6:applicable_scope
control_ref: B.8.2.6
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Processor RoPA Coverage Scope

<<DOC_CONTROL>>

> The upstream — every customer engagement in scope of B.8.2.1 must have a corresponding B.8.2.6 RoPA row. Excludes own-controller processing.

## What this template gives you

This template helps you clearly define which customer engagements fall under the Processor RoPA requirements, making it easier to ensure your privacy documentation is complete and aligned with ISO 27701 standards.

## When to use it

Use this document whenever your activities match the criteria for Processor RoPA coverage, especially when new customer engagements begin or your processing profile changes. Update it as needed to keep your records accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, depending on the number of required elements and how many customer engagements you need to document.

## 1. In-scope customer engagements (from B.8.2.1 register)

<<MUST item:B.8.2.6:scope_customer_engagements>>
_Why: §8.2.6 — carried out on behalf of a customer_

<<GUIDANCE>>

<<TEXT>>

## 2. Own-controller processing excluded (goes to a separate own-controller RoPA if the org also acts as controller — Arion does both)

<<MUST item:B.8.2.6:scope_own_controller_exclusion>>
_Why: Classification defensibility_

<<GUIDANCE>>

<<TEXT>>

## 3. Coverage test — processor RoPA rowcount reconciles against B.8.2.1 customer register

<<MUST item:B.8.2.6:scope_coverage_test>>
_Why: Integrity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new customer onboarding / customer churn)

<<SHOULD item:B.8.2.6:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
