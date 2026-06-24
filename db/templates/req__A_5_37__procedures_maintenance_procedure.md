---
leaf_id: req:A.5.37:procedures_maintenance_procedure
control_ref: A.5.37
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Operating Procedures Maintenance Procedure

> A.5.37 expects procedures to be documented AND kept available — both require maintenance. The procedure documents who keeps the register and procedures current, what triggers an update (system change, control change, finding-driven update, exercise outcome), and the lifecycle from draft → review → publish → retire

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Named maintainer of the register (typically operations lead with InfoSec partner) accountable for catalogue currency

<<MUST item:A.5.37:proc_maintainer>>
_Why: Accountability_

<<TEXT>>

## 2. Update triggers enumerated (system change A.8.32 → procedure update, control change, finding from A.5.35/A.5.36 review, exercise outcome from A.5.24/A.5.29, operator-reported error)

<<MUST item:A.5.37:proc_update_triggers>>
_Why: 27002:5.37 — documented + current_

<<TEXT>>

## 3. Review path before publication (peer review by other operators, InfoSec sign-off for procedures touching security controls)

<<MUST item:A.5.37:proc_review_path>>
_Why: Operational sufficiency_

<<TEXT>>

## 4. Retirement path for obsolete procedures (system decommissioned, procedure superseded) — retired procedures are archived, not deleted

<<MUST item:A.5.37:proc_retire_path>>
_Why: Auditability_

<<TEXT>>

## 5. Template definition stated (purpose / scope / prerequisites / steps / verification / rollback / contacts) — drives consistent shape

<<MUST item:A.5.37:proc_template>>
_Why: Reviewability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Runbook-drill cadence — periodic exercise of selected procedures (especially emergency-use ones) so they're verified actionable under pressure

<<SHOULD item:A.5.37:proc_runbook_drill>>
_Why: Effectiveness check_

<<TEXT>>

### 2. Change-log requirement for procedure edits (so the audit trail is preserved across versions)

<<SHOULD item:A.5.37:proc_change_log>>
_Why: Auditability_

<<TEXT>>
