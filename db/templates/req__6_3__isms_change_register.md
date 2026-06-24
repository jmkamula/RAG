---
leaf_id: req:6.3:isms_change_register
control_ref: 6.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# ISMS Change Register

> Per-change record capturing every ISMS-level change — the integration point between 4.3 scope changes, 4.4 manual changes, 5.3 roles changes (whose own change records flow up here). Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique change identifier per row

<<MUST item:6.3:reg_change_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-row change type (scope / policy / manual / roles / risk-criteria / structural)

<<MUST item:6.3:reg_change_type>>
_Why: Clause 6.3 — determines the need_

<<TEXT>>

## 3. Per-row trigger stated (audit finding, regulator change, org restructure, etc.)

<<MUST item:6.3:reg_trigger>>
_Why: Defensibility_

<<TEXT>>

## 4. Per-row approval signature + date

<<MUST item:6.3:reg_approval>>
_Why: Clause 6.3 — planned_

<<TEXT>>

## 5. Per-row impact summary recorded

<<MUST item:6.3:reg_impact_summary>>
_Why: Clause 6.3 — consequences_

<<TEXT>>

## 6. Per-row status (proposed / approved / implemented / withdrawn)

<<MUST item:6.3:reg_status>>
_Why: Tracking_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row cross-reference to the source change record (4.3 / 4.4 / 5.3 etc.) where applicable

<<SHOULD item:6.3:reg_source_xref>>
_Why: Cross-leaf coherence_

<<TEXT>>
