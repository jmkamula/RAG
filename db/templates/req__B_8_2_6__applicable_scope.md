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

> The upstream — every customer engagement in scope of B.8.2.1 must have a corresponding B.8.2.6 RoPA row. Excludes own-controller processing.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. In-scope customer engagements (from B.8.2.1 register)

<<MUST item:B.8.2.6:scope_customer_engagements>>
_Why: §8.2.6 — carried out on behalf of a customer_

<<TEXT>>

## 2. Own-controller processing excluded (goes to a separate own-controller RoPA if the org also acts as controller — Arion does both)

<<MUST item:B.8.2.6:scope_own_controller_exclusion>>
_Why: Classification defensibility_

<<TEXT>>

## 3. Coverage test — processor RoPA rowcount reconciles against B.8.2.1 customer register

<<MUST item:B.8.2.6:scope_coverage_test>>
_Why: Integrity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new customer onboarding / customer churn)

<<SHOULD item:B.8.2.6:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
