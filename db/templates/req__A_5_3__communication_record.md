---
leaf_id: req:A.5.3:communication_record
control_ref: A.5.3
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 3
should_count: 2
table_shape: true
---

# Segregation Matrix Communication Record

<<DOC_CONTROL>>

> Affected role-holders must know their conflicts and the separation mechanisms that apply to them — an approved-but-unknown matrix doesn't prevent anything. Evidence must show active distribution (date, audience, channel), not just availability of the matrix on an intranet

<!-- TABLE-COLUMNS leaf:req:A.5.3:communication_record -->
<!-- column: item:A.5.3:comm_date -->
<!-- column: item:A.5.3:comm_audience -->
<!-- column: item:A.5.3:comm_channel -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of who has received information about segregation of duties, including when, how, and to whom the details were communicated. It ensures everyone affected is properly informed about their specific responsibilities and any conflicts.

## When to use it

Use this template whenever you need to document the distribution of your segregation matrix to relevant staff. Update it whenever there are changes or new communications to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30–45 minutes to fill out the required details for a small team, with additional time needed as you add more recipients or communication events.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.3:communication_record -->
| Comm Date | Comm Audience | Comm Channel |
|---|---|---|
|          |          |          |
|          |          |          |
|          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.3:communication_record -->

## Column guidance — what to fill in

### Comm Date

<<MUST item:A.5.3:comm_date>>
_Why: Operational sufficiency_

> _Standard text:_ Date of publication/communication

<<GUIDANCE>>

### Comm Audience

<<MUST item:A.5.3:comm_audience>>
_Why: 27002:5.3 — implemented_

> _Standard text:_ Audience reached (affected role-holders or all relevant function leads)

<<GUIDANCE>>

### Comm Channel

<<MUST item:A.5.3:comm_channel>>
_Why: Operational sufficiency_

> _Standard text:_ Channel used (intranet publication, role-holder briefing, manager cascade)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Comm A64 Link

<<SHOULD item:A.5.3:comm_a64_link>>
_Why: Enforcement_

> _Standard text:_ Linkage into A.6.4 disciplinary process — non-compliance with separation has stated consequence

<<GUIDANCE>>

### Comm Onboarding

<<SHOULD item:A.5.3:comm_onboarding>>
_Why: Sustained communication_

> _Standard text:_ Communication built into onboarding for new role-holders in affected positions

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
