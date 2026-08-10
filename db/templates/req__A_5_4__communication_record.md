---
leaf_id: req:A.5.4:communication_record
control_ref: A.5.4
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
table_shape: true
---

# Management Directive Communication Record

<<DOC_CONTROL>>

> A directive that personnel haven't seen is not an applied directive. Evidence must show active distribution to all personnel and, critically, that new personnel are reached at onboarding — not just availability of the directive on an intranet

<!-- TABLE-COLUMNS leaf:req:A.5.4:communication_record -->
<!-- column: item:A.5.4:comm_date -->
<!-- column: item:A.5.4:comm_audience -->
<!-- column: item:A.5.4:comm_channel -->
<!-- column: item:A.5.4:comm_onboarding -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of how and when important management directives are shared with your team, including proof that new hires receive this information during onboarding.

## When to use it

Use this record whenever you distribute a management directive to your staff, and update it as needed—especially when new personnel join or when directives are updated.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes to complete the required sections for the first time, plus a few minutes for each new entry as you add more personnel.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.4:communication_record -->
| Comm Date | Comm Audience | Comm Channel | Comm Onboarding |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.4:communication_record -->

## Column guidance — what to fill in

### Comm Date

<<MUST item:A.5.4:comm_date>>
_Why: Operational sufficiency_

> _Standard text:_ Date of publication/communication

<<GUIDANCE>>

### Comm Audience

<<MUST item:A.5.4:comm_audience>>
_Why: 27002:5.4 — all personnel_

> _Standard text:_ Audience reached (all personnel, including contractors and third parties in scope)

<<GUIDANCE>>

### Comm Channel

<<MUST item:A.5.4:comm_channel>>
_Why: Operational sufficiency_

> _Standard text:_ Channel used (all-hands briefing, intranet publication, manager cascade, training module)

<<GUIDANCE>>

### Comm Onboarding

<<MUST item:A.5.4:comm_onboarding>>
_Why: 27002:5.4 — new-joiner coverage_

> _Standard text:_ Distribution at onboarding for new personnel evidenced (induction pack, mandatory module)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Comm Acknowledgement

<<SHOULD item:A.5.4:comm_acknowledgement>>
_Why: Reinforces personal accountability_

> _Standard text:_ Personnel acknowledgement captured (signature, e-attestation, training completion)

<<GUIDANCE>>

### Comm Refresh

<<SHOULD item:A.5.4:comm_refresh>>
_Why: Ongoing reinforcement_

> _Standard text:_ Periodic re-acknowledgement referenced (annual at minimum)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
