---
leaf_id: req:A.7.3.9:applicable_scope
control_ref: A.7.3.9
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Request Scope

<<DOC_CONTROL>>

> The upstream — which requests are 'legitimate' (from a verifiable subject about their own PII) and which are excluded (from third parties without authorisation, unrelated to org's processing, etc.).

## What this template gives you

This template helps you clearly define which data requests your organization will accept and which ones you will exclude, making it easier to handle privacy requests in line with privacy standards.

## When to use it

Use this document whenever your organization needs to clarify which types of personal data requests are valid, especially when your activities match certain privacy triggers. Update it as needed when your processes or regulations change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you’ll need to address three required elements and possibly one recommended element.

## 1. Legitimate-request test (verifiable subject + about their own PII + relates to org's processing)

<<MUST item:A.7.3.9:scope_legitimate_test>>
_Why: §7.3.9 — legitimate requests_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-jurisdiction response-time matrix (Art.12.3 30 days default + extensions)

<<MUST item:A.7.3.9:scope_response_time_matrix>>
_Why: GDPR Art.12.3_

<<GUIDANCE>>

<<TEXT>>

## 3. Where fees permitted (excessive/repetitive under GDPR; other jurisdictions vary)

<<MUST item:A.7.3.9:scope_fee_scope>>
_Why: §7.3.9 — some jurisdictions_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new jurisdiction / new SA guidance)

<<SHOULD item:A.7.3.9:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
