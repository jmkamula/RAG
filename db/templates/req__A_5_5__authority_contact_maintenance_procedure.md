---
leaf_id: req:A.5.5:authority_contact_maintenance_procedure
control_ref: A.5.5
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 3
---

# Authority Contact Maintenance Procedure

> A.5.5 requires authority contact to be maintained, not just established once. The procedure documents who keeps the register current, what triggers an update, how new authorities enter the register when scope changes, and the activation path when an incident requires engagement

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Named maintainer of the register (compliance lead, security manager, or designate)

<<MUST item:A.5.5:proc_maintainer>>
_Why: Accountability — 27002:5.5_

<<TEXT>>

## 2. Update triggers enumerated (new jurisdiction, new service line, regulator reorganisation, contact-change alert)

<<MUST item:A.5.5:proc_update_triggers>>
_Why: 27002:5.5 — maintained_

<<TEXT>>

## 3. Intake path for adding a new authority (driven from the applicable-authorities scope leaf)

<<MUST item:A.5.5:proc_intake_path>>
_Why: Operational sufficiency_

<<TEXT>>

## 4. Activation path — who contacts whom on which trigger (incident category, regulatory deadline)

<<MUST item:A.5.5:proc_activation_path>>
_Why: 27002:5.5b — when to contact_

<<TEXT>>

## 5. Re-verification cadence for contact details (annual at minimum)

<<MUST item:A.5.5:proc_verification_cadence>>
_Why: 27002:5.5 — maintained_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic tabletop or drill of the activation path (proves the contact path works under pressure)

<<SHOULD item:A.5.5:proc_drill>>
_Why: Effectiveness check_

<<TEXT>>

### 2. Links to notification templates kept beside the procedure

<<SHOULD item:A.5.5:proc_template_link>>
_Why: Speed at time of incident_

<<TEXT>>

### 3. Change-log requirement for any register edit so the audit trail is preserved

<<SHOULD item:A.5.5:proc_change_log>>
_Why: Auditability_

<<TEXT>>
