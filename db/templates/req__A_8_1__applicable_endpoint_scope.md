---
leaf_id: req:A.8.1:applicable_endpoint_scope
control_ref: A.8.1
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Endpoint Scope

> Upstream that drives the policy and register. Documents which endpoint classes apply, exclusions (kiosks → A.8.18; servers → A.8.9), and the BYOD authorisation model

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Endpoint classes enumerated (laptop / desktop / mobile / tablet / contractor-owned)

<<MUST item:A.8.1:scope_classes>>
_Why: 27002:8.1 — applicable_

<<TEXT>>

## 2. Exclusions stated explicitly (kiosks via A.8.18, servers via A.8.9, lab/test rigs via A.8.31)

<<MUST item:A.8.1:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

## 3. BYOD authorisation model (allowed / not-allowed / conditional with container)

<<MUST item:A.8.1:scope_byod_model>>
_Why: Common ambiguity point_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new device class, new vendor, regulatory inspection rights)

<<SHOULD item:A.8.1:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
