---
leaf_id: req:A.7.2.1:applicable_scope
control_ref: A.7.2.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processing Activities Scope

> The upstream — which business activities involve PII processing (and therefore need documented purposes). Excludes non-PII activities. Sets the denominator for the purpose register.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. In-scope processing activities enumerated

<<MUST item:A.7.2.1:scope_activities>>
_Why: Coverage_

<<TEXT>>

## 2. Operational test for 'involves PII processing' (identifiability + processing operation)

<<MUST item:A.7.2.1:scope_pii_test>>
_Why: §7.2.1 — PII scope_

<<TEXT>>

## 3. Out-of-scope activities (anonymous analytics, aggregate reporting) with rationale

<<MUST item:A.7.2.1:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product line, new geo entry, new data source)

<<SHOULD item:A.7.2.1:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
