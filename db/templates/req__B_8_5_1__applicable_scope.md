---
leaf_id: req:B.8.5.1:applicable_scope
control_ref: B.8.5.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processor Transfer Scope

> The upstream — every cross-jurisdiction customer PII flow (direct + via subprocessors + via support access from other regions).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Direct customer-PII transfers (multi-region cloud / backup + DR)

<<MUST item:B.8.5.1:scope_direct_transfers>>
_Why: Coverage_

<<TEXT>>

## 2. Subprocessor-driven transfers (data flowing to subprocessor regions)

<<MUST item:B.8.5.1:scope_subprocessor_transfers>>
_Why: §8.5.1 — suppliers_

<<TEXT>>

## 3. Support-access transfers (support engineers in different regions accessing customer PII)

<<MUST item:B.8.5.1:scope_support_access>>
_Why: Coverage_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new region / new subprocessor)

<<SHOULD item:B.8.5.1:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
