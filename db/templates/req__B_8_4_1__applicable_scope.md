---
leaf_id: req:B.8.4.1:applicable_scope
control_ref: B.8.4.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processor Temp-File Scope

> The upstream — infrastructure serving customer processing (application tier + database + cache + queue).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Customer-serving infrastructure enumerated

<<MUST item:B.8.4.1:scope_infrastructure>>
_Why: Coverage_

<<TEXT>>

## 2. Shared paths where cross-tenant temp file leakage is possible (with mitigation)

<<MUST item:B.8.4.1:scope_shared_paths>>
_Why: Multi-tenant discipline_

<<TEXT>>

## 3. Undeletable-file circumstances with rationale + compensating controls

<<MUST item:B.8.4.1:scope_undeletable>>
_Why: §8.4.1 — circumstances in which cannot be deleted_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new infrastructure)

<<SHOULD item:B.8.4.1:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
