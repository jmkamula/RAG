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

<<DOC_CONTROL>>

> Per-consent-event row — the auditable evidence that consent was given by a specific subject at a specific time for specific purposes with a specific artifact version. Not per-subject-summary; per-event.

<!-- TABLE-COLUMNS leaf:req:A.7.2.4:consent_record_register -->
<!-- column: item:A.7.2.4:reg_event_id -->
<!-- column: item:A.7.2.4:reg_subject_id -->
<!-- column: item:A.7.2.4:reg_timestamp -->
<!-- column: item:A.7.2.4:reg_purposes_consented -->
<!-- column: item:A.7.2.4:reg_artifact_version -->
<!-- column: item:A.7.2.4:reg_channel -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, auditable record of each time an individual gives consent, including who, when, what for, and which version of your consent form was used.

## When to use it

Use this register whenever you collect consent from someone for privacy-related purposes, especially if you need to show compliance with ISO 27701. Plan to review and update it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes setting up the required information for each consent event. The time will increase as you add more consent records over time.

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

<<GUIDANCE>>

### Reg Subject Id

<<MUST item:A.7.2.4:reg_subject_id>>
_Why: §7.2.4 — identification of subject_

> _Standard text:_ Subject identifier per row

<<GUIDANCE>>

### Reg Timestamp

<<MUST item:A.7.2.4:reg_timestamp>>
_Why: §7.2.4 — time consent provided_

> _Standard text:_ Timestamp of consent per row

<<GUIDANCE>>

### Reg Purposes Consented

<<MUST item:A.7.2.4:reg_purposes_consented>>
_Why: §7.2.4 — specific_

> _Standard text:_ Purposes consented to per row (list of A.7.2.1 purpose ids)

<<GUIDANCE>>

### Reg Artifact Version

<<MUST item:A.7.2.4:reg_artifact_version>>
_Why: §7.2.4 — consent statement_

> _Standard text:_ Artifact version consented to per row (link to A.7.2.3 register)

<<GUIDANCE>>

### Reg Channel

<<MUST item:A.7.2.4:reg_channel>>
_Why: Traceability_

> _Standard text:_ Collection channel per row (web / mobile / paper / verbal)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Withdrawal Link

<<SHOULD item:A.7.2.4:reg_withdrawal_link>>
_Why: §7.3.4 cross-link_

> _Standard text:_ Withdrawal timestamp where withdrawal has occurred

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
