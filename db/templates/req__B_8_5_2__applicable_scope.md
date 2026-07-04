---
leaf_id: req:B.8.5.2:applicable_scope
control_ref: B.8.5.2
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processor Destinations Scope

> Every jurisdiction where customer PII is processed (direct / subprocessor / support). Excludes law-enforcement-request destinations (handled via §8.5.4 + §8.5.5).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Normal-operations destinations enumerated

<<MUST item:B.8.5.2:scope_normal>>
_Why: Coverage_

<<TEXT>>

## 2. Law-enforcement exception handling documented

<<MUST item:B.8.5.2:scope_law_enforcement>>
_Why: §8.5.2 — cannot be specified in advance_

<<TEXT>>

## 3. Support-access destinations (where support engineers in other regions can access customer PII)

<<MUST item:B.8.5.2:scope_support>>
_Why: Comprehensiveness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new region / new subprocessor)

<<SHOULD item:B.8.5.2:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
