---
leaf_id: req:A.5.14:communication_record
control_ref: A.5.14
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Information Transfer Policy Communication Record

> Transfer-policy enforcement requires every personnel who could initiate a transfer (which is essentially everyone) to have been informed of the rules — channel choices, encryption requirements, classification gates and external-party disclosure obligations only work if people know about them. Evidence must show active distribution and ideally individual acknowledgement (signature, click-through, training completion), not mere intranet availability

<!-- TABLE-COLUMNS leaf:req:A.5.14:communication_record -->
<!-- column: item:A.5.14:comm_date -->
<!-- column: item:A.5.14:comm_audience -->
<!-- column: item:A.5.14:comm_channel -->
<!-- column: item:A.5.14:comm_acknowledgement -->
<!-- column: item:A.5.14:comm_onboarding -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.14:communication_record -->
| Comm Date | Comm Audience | Comm Channel | Comm Acknowledgement | Comm Onboarding |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.14:communication_record -->

## Column guidance — what to fill in

### Comm Date

<<MUST item:A.5.14:comm_date>>
_Why: Operational sufficiency_

> _Standard text:_ Date of publication/communication

### Comm Audience

<<MUST item:A.5.14:comm_audience>>
_Why: 27002:5.14 — relevant personnel_

> _Standard text:_ Audience reached (all in-scope users, including new joiners; targeted refresh for users who handle sensitive transfers frequently)

### Comm Channel

<<MUST item:A.5.14:comm_channel>>
_Why: Operational sufficiency_

> _Standard text:_ Channel used (mandatory training module, intranet publication with notification, signature campaign)

### Comm Acknowledgement

<<MUST item:A.5.14:comm_acknowledgement>>
_Why: Enforceability — burden of proof_

> _Standard text:_ User-level acknowledgement captured (e-signature, training completion record, click-through)

### Comm Onboarding

<<MUST item:A.5.14:comm_onboarding>>
_Why: 27002:5.14 — sustained communication_

> _Standard text:_ Distribution at onboarding for new personnel evidenced (induction pack, mandatory module covering transfer rules + approved channels)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Comm Refresh

<<SHOULD item:A.5.14:comm_refresh>>
_Why: Sustained communication_

> _Standard text:_ Periodic re-acknowledgement (annual at minimum) referenced

### Comm Scenario Examples

<<SHOULD item:A.5.14:comm_scenario_examples>>
_Why: Practical effectiveness_

> _Standard text:_ Scenario-based examples included in training (e.g. external auditor data request, supplier integration handover, regulator response)
