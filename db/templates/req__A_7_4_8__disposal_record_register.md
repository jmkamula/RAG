---
leaf_id: req:A.7.4.8:disposal_record_register
control_ref: A.7.4.8
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# PII Disposal Record Register

<<DOC_CONTROL>>

> Per-disposal-action row — with media type + technique + certificate. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.8:disposal_record_register -->
<!-- column: item:A.7.4.8:reg_action_id -->
<!-- column: item:A.7.4.8:reg_media_type -->
<!-- column: item:A.7.4.8:reg_technique -->
<!-- column: item:A.7.4.8:reg_certificate_ref -->
<!-- column: item:A.7.4.8:reg_date -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every time you dispose of personal data, including how and what was destroyed, and proof it was done securely.

## When to use it

Use this register whenever you destroy personal data or media containing personal information, and update it at least once a year to stay current with privacy requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each disposal event; setting up the register from scratch may take around 1-2 hours, depending on the number of disposals you need to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.8:disposal_record_register -->
| Reg Action Id | Reg Media Type | Reg Technique | Reg Certificate Ref | Reg Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.8:disposal_record_register -->

## Column guidance — what to fill in

### Reg Action Id

<<MUST item:A.7.4.8:reg_action_id>>
_Why: Audit trail_

> _Standard text:_ Unique disposal action identifier per row

<<GUIDANCE>>

### Reg Media Type

<<MUST item:A.7.4.8:reg_media_type>>
_Why: Traceability_

> _Standard text:_ Media type per row (SSD / HDD / paper / tape / cloud volume)

<<GUIDANCE>>

### Reg Technique

<<MUST item:A.7.4.8:reg_technique>>
_Why: §7.4.8 — techniques_

> _Standard text:_ Technique per row (cryptographic erase / overwrite / degaussing / shredding / provider attestation)

<<GUIDANCE>>

### Reg Certificate Ref

<<MUST item:A.7.4.8:reg_certificate_ref>>
_Why: Defensibility_

> _Standard text:_ Disposal certificate / attestation reference per row

<<GUIDANCE>>

### Reg Date

<<MUST item:A.7.4.8:reg_date>>
_Why: Currency_

> _Standard text:_ Disposal date per row

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Verifier

<<SHOULD item:A.7.4.8:reg_verifier>>
_Why: Accountability_

> _Standard text:_ Verifier identity per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
