---
leaf_id: req:10.1:improvement_action_register
control_ref: 10.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 1
---

# Improvement Action Register

> Per-improvement record — every improvement action with trigger, owner, target date, effectiveness assessment on closure. Distinct from 10.2 NC register (which is reactive — fixing NCs) and 6.1.1 action register (which is forward-planning): this is targeted improvement of ISMS suitability/adequacy/effectiveness. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique action identifier per row

<<MUST item:10.1:reg_action_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-row trigger type (audit finding / measurement gap / opportunity / party feedback / mgmt review output)

<<MUST item:10.1:reg_trigger_type>>
_Why: Clause 10.1 — triggers_

<<TEXT>>

## 3. Per-row improvement dimension (suitability / adequacy / effectiveness)

<<MUST item:10.1:reg_dimension>>
_Why: Clause 10.1 — three dimensions_

<<TEXT>>

## 4. Per-row owner

<<MUST item:10.1:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 5. Per-row target completion date

<<MUST item:10.1:reg_target_date>>
_Why: Tracking_

<<TEXT>>

## 6. Per-row status (proposed / approved / in-progress / closed / superseded)

<<MUST item:10.1:reg_status>>
_Why: Tracking_

<<TEXT>>

## 7. Per-row effectiveness assessment captured on closure (did the improvement work?)

<<MUST item:10.1:reg_effectiveness>>
_Why: Clause 10.1 — effectiveness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row cross-reference to the trigger source (9.2 audit finding id, 9.1 measurement breach, 9.3 review decision)

<<SHOULD item:10.1:reg_source_xref>>
_Why: Traceability_

<<TEXT>>
