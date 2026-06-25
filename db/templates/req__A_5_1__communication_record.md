---
leaf_id: req:A.5.1:communication_record
control_ref: A.5.1
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 3
should_count: 2
table_shape: true
---

# Information Security Policy Communication Record

> A.5.1 requires the policy to be published and communicated to relevant personnel. Evidence must show active distribution (date, audience, channel), not mere availability on an intranet

<!-- TABLE-COLUMNS leaf:req:A.5.1:communication_record -->
<!-- column: item:A.5.1:comm_date -->
<!-- column: item:A.5.1:comm_audience -->
<!-- column: item:A.5.1:comm_channel -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.1:communication_record -->
| Comm Date | Comm Audience | Comm Channel |
|---|---|---|
|          |          |          |
|          |          |          |
|          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.1:communication_record -->

## Column guidance — what to fill in

### Comm Date

<<MUST item:A.5.1:comm_date>>
_Why: 27002:5.1 — communicated_

> _Standard text:_ Date of publication/communication

### Comm Audience

<<MUST item:A.5.1:comm_audience>>
_Why: 27002:5.1 — communicated to relevant personnel_

> _Standard text:_ Audience reached (all staff, scoped subset, or named groups)

### Comm Channel

<<MUST item:A.5.1:comm_channel>>
_Why: 27002:5.1 — communicated_

> _Standard text:_ Channel used (intranet publication, email, training session, town hall)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Comm Acknowledgment

<<SHOULD item:A.5.1:comm_acknowledgment>>
_Why: 27002:5.1 — acknowledged_

> _Standard text:_ Acknowledgment of receipt and understanding by personnel (e.g. signed register, e-learning completion)

### Comm Interested

<<SHOULD item:A.5.1:comm_interested>>
_Why: 27002:5.1 — interested parties_

> _Standard text:_ Communication to relevant interested parties (contractors, suppliers) where appropriate
