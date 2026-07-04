---
leaf_id: req:A.7.2.4:consent_record_register
control_ref: A.7.2.4
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Per-Subject Consent Record Register

> Per-consent-event row — the auditable evidence that consent was given by a specific subject at a specific time for specific purposes with a specific artifact version. Not per-subject-summary; per-event.

<!-- TABLE-COLUMNS leaf:req:A.7.2.4:consent_record_register -->
<!-- column: item:A.7.2.4:reg_event_id -->
<!-- column: item:A.7.2.4:reg_subject_id -->
<!-- column: item:A.7.2.4:reg_timestamp -->
<!-- column: item:A.7.2.4:reg_purposes_consented -->
<!-- column: item:A.7.2.4:reg_artifact_version -->
<!-- column: item:A.7.2.4:reg_channel -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.4:consent_record_register -->
| Reg Event Id | Reg Subject Id | Reg Timestamp | Reg Purposes Consented | Reg Artifact Version | Reg Channel |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.4:consent_record_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:A.7.2.4:reg_event_id>>
_Why: Audit trail_

> _Standard text:_ Unique consent event id per row

### Reg Subject Id

<<MUST item:A.7.2.4:reg_subject_id>>
_Why: §7.2.4 — identification of subject_

> _Standard text:_ Subject identifier per row

### Reg Timestamp

<<MUST item:A.7.2.4:reg_timestamp>>
_Why: §7.2.4 — time consent provided_

> _Standard text:_ Timestamp of consent per row

### Reg Purposes Consented

<<MUST item:A.7.2.4:reg_purposes_consented>>
_Why: §7.2.4 — specific_

> _Standard text:_ Purposes consented to per row (list of A.7.2.1 purpose ids)

### Reg Artifact Version

<<MUST item:A.7.2.4:reg_artifact_version>>
_Why: §7.2.4 — consent statement_

> _Standard text:_ Artifact version consented to per row (link to A.7.2.3 register)

### Reg Channel

<<MUST item:A.7.2.4:reg_channel>>
_Why: Traceability_

> _Standard text:_ Collection channel per row (web / mobile / paper / verbal)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Withdrawal Link

<<SHOULD item:A.7.2.4:reg_withdrawal_link>>
_Why: §7.3.4 cross-link_

> _Standard text:_ Withdrawal timestamp where withdrawal has occurred
