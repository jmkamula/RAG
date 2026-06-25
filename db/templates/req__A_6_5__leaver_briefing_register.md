---
leaf_id: req:A.6.5:leaver_briefing_register
control_ref: A.6.5
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Leaver Briefing Register

> The operational catalogue of exit briefings and role-change briefings. Each event: leaver identifier, trigger (termination / contract end / role change), briefing date, briefer, signed acknowledgment of surviving obligations. Drives 'show me every leaver acknowledged their post-employment obligations' audit

<!-- TABLE-COLUMNS leaf:req:A.6.5:leaver_briefing_register -->
<!-- column: item:A.6.5:reg_leaver_id -->
<!-- column: item:A.6.5:reg_trigger -->
<!-- column: item:A.6.5:reg_briefing_date -->
<!-- column: item:A.6.5:reg_briefer -->
<!-- column: item:A.6.5:reg_acknowledgment -->
<!-- column: item:A.6.5:reg_obligations_covered -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.5:leaver_briefing_register -->
| Reg Leaver Id | Reg Trigger | Reg Briefing Date | Reg Briefer | Reg Acknowledgment | Reg Obligations Covered |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.5:leaver_briefing_register -->

## Column guidance — what to fill in

### Reg Leaver Id

<<MUST item:A.6.5:reg_leaver_id>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row leaver identifier (links to identity register A.5.16; cross-link to A.5.11 return-of-assets record + A.5.16 identity revocation)

### Reg Trigger

<<MUST item:A.6.5:reg_trigger>>
_Why: 27002:6.5 — termination or change_

> _Standard text:_ Per-row trigger (termination / contract end / role change within org / retirement)

### Reg Briefing Date

<<MUST item:A.6.5:reg_briefing_date>>
_Why: 27002:6.5 — communicated_

> _Standard text:_ Per-row briefing date (typically last working day or shortly after; for role change, at point of role transition)

### Reg Briefer

<<MUST item:A.6.5:reg_briefer>>
_Why: Accountability_

> _Standard text:_ Per-row briefer identity (HR partner; line manager joins for role-change cases)

### Reg Acknowledgment

<<MUST item:A.6.5:reg_acknowledgment>>
_Why: 27002:6.5 — communicated_

> _Standard text:_ Per-row signed acknowledgment evidence (digital signature / signed PDF / recorded receipt of intranet artefact)

### Reg Obligations Covered

<<MUST item:A.6.5:reg_obligations_covered>>
_Why: 27002:6.5 — duties that remain_

> _Standard text:_ Per-row covered obligations list (confidentiality + IP + non-poach + non-compete where applicable per jurisdiction)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Post Briefing Check

<<SHOULD item:A.6.5:reg_post_briefing_check>>
_Why: Continual assurance_

> _Standard text:_ Per-row post-briefing check (30/90/180-day check that no breach has occurred — proportional to role seniority)

### Reg A5 11 Link

<<SHOULD item:A.6.5:reg_a5_11_link>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row cross-link to A.5.11 return-of-assets register (same leaver event)
