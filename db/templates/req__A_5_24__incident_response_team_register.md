---
leaf_id: req:A.5.24:incident_response_team_register
control_ref: A.5.24
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Incident Response Team Register

<<DOC_CONTROL>>

> A.5.24 requires the responders to be ready before the incident — half a team during a real incident is the failure mode. The register catalogues every named responder: name (or stable role), tier, on-call status, contact info (multiple channels), training currency, backup. It is the operational record that proves the team is staffed-and-trained, not just nominated on the org chart

<!-- TABLE-COLUMNS leaf:req:A.5.24:incident_response_team_register -->
<!-- column: item:A.5.24:reg_member_id -->
<!-- column: item:A.5.24:reg_role -->
<!-- column: item:A.5.24:reg_tier -->
<!-- column: item:A.5.24:reg_contact -->
<!-- column: item:A.5.24:reg_oncall -->
<!-- column: item:A.5.24:reg_training_current -->
<!-- column: item:A.5.24:reg_backup_named -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an up-to-date list of your incident response team members, showing who is available, trained, and ready to respond if something goes wrong. It demonstrates that your team is fully staffed and prepared, not just listed on paper.

## When to use it

Use this register at all times to maintain a clear record of your incident response team. Update it whenever team members change, contact details are updated, or training status shifts.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each team member. For a typical team of five, initial setup may take 1–2 hours, with occasional updates as needed.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.24:incident_response_team_register -->
| Reg Member Id | Reg Role | Reg Tier | Reg Contact | Reg Oncall | Reg Training Current | Reg Backup Named |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.24:incident_response_team_register -->

## Column guidance — what to fill in

### Reg Member Id

<<MUST item:A.5.24:reg_member_id>>
_Why: 27002:5.24 — preparation_

> _Standard text:_ Each IR team member captured with a unique identifier (employee or contractor id)

<<GUIDANCE>>

### Reg Role

<<MUST item:A.5.24:reg_role>>
_Why: 27002:5.24a_

> _Standard text:_ Role per row (ir_lead / deputy / comms / legal / forensic_specialist / technical_lead) — explicitly mapped to framework role taxonomy

<<GUIDANCE>>

### Reg Tier

<<MUST item:A.5.24:reg_tier>>
_Why: 27002:5.24 — preparation_

> _Standard text:_ Tier per row (primary / backup / escalation_only) — drives the activation order

<<GUIDANCE>>

### Reg Contact

<<MUST item:A.5.24:reg_contact>>
_Why: 27002:5.24 — communication_

> _Standard text:_ Contact info per row across multiple channels (phone + secondary phone + email + out-of-band channel for if corp comms are compromised)

<<GUIDANCE>>

### Reg Oncall

<<MUST item:A.5.24:reg_oncall>>
_Why: 27002:5.24 — readiness_

> _Standard text:_ On-call status per row (when in active rotation; how long; when next handover)

<<GUIDANCE>>

### Reg Training Current

<<MUST item:A.5.24:reg_training_current>>
_Why: 27002:5.24 — preparation_

> _Standard text:_ Training-currency per row (last training date, training type; flagged when stale)

<<GUIDANCE>>

### Reg Backup Named

<<MUST item:A.5.24:reg_backup_named>>
_Why: 27002:5.24 — preparation_

> _Standard text:_ Backup named per row (no single-person roles; rotation continuity guaranteed)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg External Partner

<<SHOULD item:A.5.24:reg_external_partner>>
_Why: Response continuity_

> _Standard text:_ External-partner contacts captured alongside internal members (regulator points-of-contact, retained forensic firm contact)

<<GUIDANCE>>

### Reg Dpia Competence

<<SHOULD item:A.5.24:reg_dpia_competence>>
_Why: GDPR Art.33 readiness_

> _Standard text:_ DPIA / data-protection competence flag per row (drives who handles the GDPR Art.33 path when personal data is in scope)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
