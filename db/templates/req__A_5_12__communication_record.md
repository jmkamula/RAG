---
leaf_id: req:A.5.12:communication_record
control_ref: A.5.12
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Classification Scheme Communication Record

> Every information creator (i.e. every employee) needs to know which level applies and how to classify their output — an unknown scheme produces unclassified information by default, which collapses A.5.13 and A.5.10 downstream. Evidence must show active distribution and ideally individual training completion

<!-- TABLE-COLUMNS leaf:req:A.5.12:communication_record -->
<!-- column: item:A.5.12:comm_date -->
<!-- column: item:A.5.12:comm_audience -->
<!-- column: item:A.5.12:comm_channel -->
<!-- column: item:A.5.12:comm_training -->
<!-- column: item:A.5.12:comm_onboarding -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.12:communication_record -->
| Comm Date | Comm Audience | Comm Channel | Comm Training | Comm Onboarding |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.12:communication_record -->

## Column guidance — what to fill in

### Comm Date

<<MUST item:A.5.12:comm_date>>
_Why: Operational sufficiency_

> _Standard text:_ Date of publication/communication

### Comm Audience

<<MUST item:A.5.12:comm_audience>>
_Why: 27002:5.12 — all relevant personnel_

> _Standard text:_ Audience reached (all information creators, owners, custodians — broader than just data owners)

### Comm Channel

<<MUST item:A.5.12:comm_channel>>
_Why: Operational sufficiency_

> _Standard text:_ Channel used (mandatory training module, classification guide, role-specific workshops)

### Comm Training

<<MUST item:A.5.12:comm_training>>
_Why: Operational fitness_

> _Standard text:_ Classification training completion captured at user level (proves users can apply the scheme)

### Comm Onboarding

<<MUST item:A.5.12:comm_onboarding>>
_Why: 27002:5.12 — new joiners_

> _Standard text:_ Distribution at onboarding for new personnel evidenced (induction pack, mandatory module)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Comm Refresh

<<SHOULD item:A.5.12:comm_refresh>>
_Why: Sustained communication_

> _Standard text:_ Periodic refresher referenced (annual at minimum, especially after scheme amendments)

### Comm Practical Aids

<<SHOULD item:A.5.12:comm_practical_aids>>
_Why: Adoption_

> _Standard text:_ Practical aids referenced (decision tree, sensitivity-label automation, examples library)
