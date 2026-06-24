---
leaf_id: req:A.7.2:applicable_areas_scope
control_ref: A.7.2
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Secure Areas Scope

> The upstream that drives the procedure. Documents which areas require physical entry controls and what classification tier each falls under

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Secure areas enumerated per site (drawn from A.7.1 register)

<<MUST item:A.7.2:scope_areas>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-tier entry controls mapping (which areas need badge-only vs MFA vs escort)

<<MUST item:A.7.2:scope_tier_controls>>
_Why: 27002:7.2 — proportional_

<<TEXT>>

## 3. Visitor-accessible areas defined (vs strictly-staff areas)

<<MUST item:A.7.2:scope_visitor_areas>>
_Why: 27002:7.2 — controls_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new secure area, area classification change, sub-letting)

<<SHOULD item:A.7.2:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
