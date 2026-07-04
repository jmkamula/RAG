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

> The upstream — which requests are 'legitimate' (from a verifiable subject about their own PII) and which are excluded (from third parties without authorisation, unrelated to org's processing, etc.).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Legitimate-request test (verifiable subject + about their own PII + relates to org's processing)

<<MUST item:A.7.3.9:scope_legitimate_test>>
_Why: §7.3.9 — legitimate requests_

<<TEXT>>

## 2. Per-jurisdiction response-time matrix (Art.12.3 30 days default + extensions)

<<MUST item:A.7.3.9:scope_response_time_matrix>>
_Why: GDPR Art.12.3_

<<TEXT>>

## 3. Where fees permitted (excessive/repetitive under GDPR; other jurisdictions vary)

<<MUST item:A.7.3.9:scope_fee_scope>>
_Why: §7.3.9 — some jurisdictions_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new jurisdiction / new SA guidance)

<<SHOULD item:A.7.3.9:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
