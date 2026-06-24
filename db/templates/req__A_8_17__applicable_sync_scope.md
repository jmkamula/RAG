---
leaf_id: req:A.8.17:applicable_sync_scope
control_ref: A.8.17
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 2
should_count: 1
---

# Applicable Sync Scope

> Upstream — which system classes need sync, what drift tolerance per class (sub-second for forensics-critical; seconds acceptable elsewhere)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. System classes enumerated with drift tolerance per class

<<MUST item:A.8.17:scope_classes>>
_Why: 27002:8.17 — appropriate_

<<TEXT>>

## 2. Exclusion rationale (network-isolated systems with documented offline-clock procedure)

<<MUST item:A.8.17:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system class, new regulator drift requirement)

<<SHOULD item:A.8.17:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
