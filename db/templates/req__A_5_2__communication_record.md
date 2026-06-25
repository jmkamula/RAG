---
leaf_id: req:A.5.2:communication_record
control_ref: A.5.2
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 3
should_count: 2
table_shape: true
---

# Roles and Responsibilities Communication Record

> Clause 5.3 requires roles, responsibilities and authorities to be communicated within the organization. Evidence must show active distribution (date, audience, channel), not mere availability of the matrix on an intranet — affected role-holders need to actually know what they own

<!-- TABLE-COLUMNS leaf:req:A.5.2:communication_record -->
<!-- column: item:A.5.2:comm_date -->
<!-- column: item:A.5.2:comm_audience -->
<!-- column: item:A.5.2:comm_channel -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.2:communication_record -->
| Comm Date | Comm Audience | Comm Channel |
|---|---|---|
|          |          |          |
|          |          |          |
|          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.2:communication_record -->

## Column guidance — what to fill in

### Comm Date

<<MUST item:A.5.2:comm_date>>
_Why: Clause 5.3_

> _Standard text:_ Date of publication/communication

### Comm Audience

<<MUST item:A.5.2:comm_audience>>
_Why: Clause 5.3 — communicated within the organization_

> _Standard text:_ Audience reached (all staff or named role-holders)

### Comm Channel

<<MUST item:A.5.2:comm_channel>>
_Why: Clause 5.3_

> _Standard text:_ Channel used (intranet publication, email, training session, onboarding pack)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Comm Role Briefing

<<SHOULD item:A.5.2:comm_role_briefing>>
_Why: Effectiveness_

> _Standard text:_ Role-specific briefing or acknowledgement from named role-holders (CISO, asset owners, etc.)

### Comm Onboarding

<<SHOULD item:A.5.2:comm_onboarding>>
_Why: Sustained communication_

> _Standard text:_ Communication built into joiner onboarding so new role-holders are briefed on appointment
