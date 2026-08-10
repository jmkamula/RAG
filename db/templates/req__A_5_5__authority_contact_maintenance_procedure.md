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

<<DOC_CONTROL>>

> A.5.5 requires authority contact to be maintained, not just established once. The procedure documents who keeps the register current, what triggers an update, how new authorities enter the register when scope changes, and the activation path when an incident requires engagement

## What this template gives you

This template helps you clearly document how your organization keeps its list of authority contacts up to date, including who is responsible, when updates are needed, and how to respond during incidents.

## When to use it

Use this procedure whenever your environment requires ongoing maintenance of authority contact information, especially when there are changes in scope or after any incident that involves engaging with authorities. Review and update the document as needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on how many authority contacts you need to register and how much detail you provide for each required section.

## 1. Named maintainer of the register (compliance lead, security manager, or designate)

<<MUST item:A.5.5:proc_maintainer>>
_Why: Accountability — 27002:5.5_

<<GUIDANCE>>

<<TEXT>>

## 2. Update triggers enumerated (new jurisdiction, new service line, regulator reorganisation, contact-change alert)

<<MUST item:A.5.5:proc_update_triggers>>
_Why: 27002:5.5 — maintained_

<<GUIDANCE>>

<<TEXT>>

## 3. Intake path for adding a new authority (driven from the applicable-authorities scope leaf)

<<MUST item:A.5.5:proc_intake_path>>
_Why: Operational sufficiency_

<<GUIDANCE>>

<<TEXT>>

## 4. Activation path — who contacts whom on which trigger (incident category, regulatory deadline)

<<MUST item:A.5.5:proc_activation_path>>
_Why: 27002:5.5b — when to contact_

<<GUIDANCE>>

<<TEXT>>

## 5. Re-verification cadence for contact details (annual at minimum)

<<MUST item:A.5.5:proc_verification_cadence>>
_Why: 27002:5.5 — maintained_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic tabletop or drill of the activation path (proves the contact path works under pressure)

<<SHOULD item:A.5.5:proc_drill>>
_Why: Effectiveness check_

<<GUIDANCE>>

<<TEXT>>

### 2. Links to notification templates kept beside the procedure

<<SHOULD item:A.5.5:proc_template_link>>
_Why: Speed at time of incident_

<<GUIDANCE>>

<<TEXT>>

### 3. Change-log requirement for any register edit so the audit trail is preserved

<<SHOULD item:A.5.5:proc_change_log>>
_Why: Auditability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
