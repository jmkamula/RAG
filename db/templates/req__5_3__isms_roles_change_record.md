---
leaf_id: req:5.3:isms_roles_change_record
control_ref: 5.3
standard_id: ISO27001:2022
evidence_type: change_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# ISMS Roles Change Record

> Per-change record capturing each amendment to the roles matrix — role added, role retired, role-holder changed. Lifecycle-end artefact proving role drift is being managed, not silent

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Change trigger stated (org restructure, new control area, person change, new framework)

<<MUST item:5.3:chg_trigger>>
_Why: Defensible amendment_

<<TEXT>>

## 2. Change summary — what was added, removed, or reassigned

<<MUST item:5.3:chg_summary>>
_Why: Audit clarity_

<<TEXT>>

## 3. Communication of the change (link to 7.4) — affected role-holders informed

<<MUST item:5.3:chg_comms>>
_Why: Clause 5.3 — communicated_

<<TEXT>>

## 4. Approval signature with date (top management or delegated authority)

<<MUST item:5.3:chg_approval>>
_Why: Clause 5.3 — assigned_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. A.5.2 operational-roles cross-check captured (where 5.3 and A.5.2 touch)

<<SHOULD item:5.3:chg_a52_check>>
_Why: Cross-control coherence_

<<TEXT>>
