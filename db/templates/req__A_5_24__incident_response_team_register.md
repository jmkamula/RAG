---
leaf_id: req:A.5.24:incident_response_team_register
control_ref: A.5.24
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Incident Response Team Register

> A.5.24 requires the responders to be ready before the incident — half a team during a real incident is the failure mode. The register catalogues every named responder: name (or stable role), tier, on-call status, contact info (multiple channels), training currency, backup. It is the operational record that proves the team is staffed-and-trained, not just nominated on the org chart

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each IR team member captured with a unique identifier (employee or contractor id)

<<MUST item:A.5.24:reg_member_id>>
_Why: 27002:5.24 — preparation_

<<TEXT>>

## 2. Role per row (ir_lead / deputy / comms / legal / forensic_specialist / technical_lead) — explicitly mapped to framework role taxonomy

<<MUST item:A.5.24:reg_role>>
_Why: 27002:5.24a_

<<TEXT>>

## 3. Tier per row (primary / backup / escalation_only) — drives the activation order

<<MUST item:A.5.24:reg_tier>>
_Why: 27002:5.24 — preparation_

<<TEXT>>

## 4. Contact info per row across multiple channels (phone + secondary phone + email + out-of-band channel for if corp comms are compromised)

<<MUST item:A.5.24:reg_contact>>
_Why: 27002:5.24 — communication_

<<TEXT>>

## 5. On-call status per row (when in active rotation; how long; when next handover)

<<MUST item:A.5.24:reg_oncall>>
_Why: 27002:5.24 — readiness_

<<TEXT>>

## 6. Training-currency per row (last training date, training type; flagged when stale)

<<MUST item:A.5.24:reg_training_current>>
_Why: 27002:5.24 — preparation_

<<TEXT>>

## 7. Backup named per row (no single-person roles; rotation continuity guaranteed)

<<MUST item:A.5.24:reg_backup_named>>
_Why: 27002:5.24 — preparation_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External-partner contacts captured alongside internal members (regulator points-of-contact, retained forensic firm contact)

<<SHOULD item:A.5.24:reg_external_partner>>
_Why: Response continuity_

<<TEXT>>

### 2. DPIA / data-protection competence flag per row (drives who handles the GDPR Art.33 path when personal data is in scope)

<<SHOULD item:A.5.24:reg_dpia_competence>>
_Why: GDPR Art.33 readiness_

<<TEXT>>
