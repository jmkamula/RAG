---
leaf_id: req:A.8.32:applicable_change_scope
control_ref: A.8.32
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Change Scope

> Upstream — what counts as a change requiring CM, what gets exempt (read-only operations / break-glass usage already covered elsewhere)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Change classes enumerated with CM path per class (standard / normal / emergency / pre-approved)

<<MUST item:A.8.32:scope_change_classes>>
_Why: 27002:8.32 — appropriate_

<<TEXT>>

## 2. Exemption rationale (read-only operations; A.8.2 break-glass usage governed there; A.8.19 software-install governed there)

<<MUST item:A.8.32:scope_exemptions>>
_Why: Boundary clarity_

<<TEXT>>

## 3. In-scope systems (cross-link to A.5.9 asset register)

<<MUST item:A.8.32:scope_systems>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system class, new automation pattern)

<<SHOULD item:A.8.32:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
