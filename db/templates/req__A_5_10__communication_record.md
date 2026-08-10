---
leaf_id: req:A.5.10:communication_record
control_ref: A.5.10
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Acceptable Use Policy Communication Record

<<DOC_CONTROL>>

> AUP enforcement requires the user to have been informed of the rules — courts and tribunals routinely hinge on this. Evidence must show active distribution and, ideally, individual acknowledgement (signature, click-through, training completion) — not just availability on an intranet

<!-- TABLE-COLUMNS leaf:req:A.5.10:communication_record -->
<!-- column: item:A.5.10:comm_date -->
<!-- column: item:A.5.10:comm_audience -->
<!-- column: item:A.5.10:comm_channel -->
<!-- column: item:A.5.10:comm_acknowledgement -->
<!-- column: item:A.5.10:comm_onboarding -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of how and when your Acceptable Use Policy was shared with users, including proof that each person received and acknowledged it.

## When to use it

Use this record whenever you distribute or update your Acceptable Use Policy, and update it as needed to reflect new communications or acknowledgements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes entering the required details for the first set of users, with additional time needed as you add more entries over time.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.10:communication_record -->
| Comm Date | Comm Audience | Comm Channel | Comm Acknowledgement | Comm Onboarding |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.10:communication_record -->

## Column guidance — what to fill in

### Comm Date

<<MUST item:A.5.10:comm_date>>
_Why: Operational sufficiency_

> _Standard text:_ Date of publication/communication

<<GUIDANCE>>

### Comm Audience

<<MUST item:A.5.10:comm_audience>>
_Why: 27002:5.10 — all relevant personnel_

> _Standard text:_ Audience reached (all in-scope users, including new joiners and contractors)

<<GUIDANCE>>

### Comm Channel

<<MUST item:A.5.10:comm_channel>>
_Why: Operational sufficiency_

> _Standard text:_ Channel used (mandatory training module, intranet publication with notification, signature campaign)

<<GUIDANCE>>

### Comm Acknowledgement

<<MUST item:A.5.10:comm_acknowledgement>>
_Why: Enforceability — burden of proof_

> _Standard text:_ User-level acknowledgement captured (e-signature, training completion record, click-through)

<<GUIDANCE>>

### Comm Onboarding

<<MUST item:A.5.10:comm_onboarding>>
_Why: 27002:5.10 — new joiners_

> _Standard text:_ Distribution at onboarding for new personnel evidenced (induction pack, mandatory module)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Comm Refresh

<<SHOULD item:A.5.10:comm_refresh>>
_Why: Sustained communication_

> _Standard text:_ Periodic re-acknowledgement (annual at minimum) referenced

<<GUIDANCE>>

### Comm Translations

<<SHOULD item:A.5.10:comm_translations>>
_Why: Accessibility_

> _Standard text:_ Translations or language considerations where the workforce is multilingual

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
