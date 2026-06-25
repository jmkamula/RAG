---
leaf_id: req:A.5.15:communication_record
control_ref: A.5.15
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Access Control Policy Communication Record

> Access-granting decision-makers (managers, system owners, IT admins) and access-holders both need to know the rules. The policy's most common failure mode is mid-level managers granting access by default without checking the principles — communication must reach them specifically

<!-- TABLE-COLUMNS leaf:req:A.5.15:communication_record -->
<!-- column: item:A.5.15:comm_date -->
<!-- column: item:A.5.15:comm_audience -->
<!-- column: item:A.5.15:comm_channel -->
<!-- column: item:A.5.15:comm_decision_makers -->
<!-- column: item:A.5.15:comm_onboarding -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.15:communication_record -->
| Comm Date | Comm Audience | Comm Channel | Comm Decision Makers | Comm Onboarding |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.15:communication_record -->

## Column guidance — what to fill in

### Comm Date

<<MUST item:A.5.15:comm_date>>
_Why: Operational sufficiency_

> _Standard text:_ Date of publication/communication

### Comm Audience

<<MUST item:A.5.15:comm_audience>>
_Why: 27002:5.15 — relevant parties_

> _Standard text:_ Audience reached (decision-makers — managers, system owners, IT admins — plus all access-holders)

### Comm Channel

<<MUST item:A.5.15:comm_channel>>
_Why: Operational sufficiency_

> _Standard text:_ Channel used (manager briefing, IT admin training, intranet publication)

### Comm Decision Makers

<<MUST item:A.5.15:comm_decision_makers>>
_Why: Targeted communication_

> _Standard text:_ Decision-maker awareness specifically captured (manager training, system-owner briefing)

### Comm Onboarding

<<MUST item:A.5.15:comm_onboarding>>
_Why: 27002:5.15 — sustained_

> _Standard text:_ Onboarding coverage — new managers and admins receive the policy as part of role induction

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Comm Refresh

<<SHOULD item:A.5.15:comm_refresh>>
_Why: Sustained communication_

> _Standard text:_ Periodic refresher referenced (annual at minimum)

### Comm A518 Link

<<SHOULD item:A.5.15:comm_a518_link>>
_Why: Coherent rollout_

> _Standard text:_ Tie-in with A.5.18 provisioning training — decision-makers know both the rules and the workflow
