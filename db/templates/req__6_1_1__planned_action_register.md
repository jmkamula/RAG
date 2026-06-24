---
leaf_id: req:6.1.1:planned_action_register
control_ref: 6.1.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# ISMS Planned Action Register

> The live output of the planning procedure — every action targeting a risk or opportunity with owner, due date, integration target. Distinct from the risk register (6.1.2) and the SoA (6.1.3): this tracks ISMS-level planning actions, not control implementations

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique action identifier per row

<<MUST item:6.1.1:reg_action_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-row driver (4.1 issue id, 4.2 party requirement id, risk id, opportunity id)

<<MUST item:6.1.1:reg_driver>>
_Why: Cross-clause traceability_

<<TEXT>>

## 3. Per-row type (risk-addressing / opportunity-enhancing)

<<MUST item:6.1.1:reg_type>>
_Why: Clause 6.1.1 — risks AND opportunities_

<<TEXT>>

## 4. Owner per row

<<MUST item:6.1.1:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 5. Integration target per row (which ISMS process consumes this action)

<<MUST item:6.1.1:reg_integration_target>>
_Why: Clause 6.1.1 — integrated into ISMS processes_

<<TEXT>>

## 6. Status per row (planned / in-progress / complete / deferred)

<<MUST item:6.1.1:reg_status>>
_Why: Tracking_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row effectiveness evaluation captured on completion

<<SHOULD item:6.1.1:reg_effectiveness>>
_Why: Clause 6.1.1 — evaluate effectiveness_

<<TEXT>>
