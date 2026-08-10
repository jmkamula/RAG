---
leaf_id: req:B.8.5.3:disclosure_event_log
control_ref: B.8.5.3
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Processor Disclosure Event Log

<<DOC_CONTROL>>

> Per-disclosure row — processor-side. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.5.3:disclosure_event_log -->
<!-- column: item:B.8.5.3:reg_disclosure_id -->
<!-- column: item:B.8.5.3:reg_customer -->
<!-- column: item:B.8.5.3:reg_recipient -->
<!-- column: item:B.8.5.3:reg_timestamp -->
<!-- column: item:B.8.5.3:reg_source_of_authority -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of each time you disclose data to a processor, making it easier to track and demonstrate compliance with privacy standards.

## When to use it

Use this register whenever you disclose personal data to a processor and need to document the event. Update it at least once a year, or whenever a new disclosure occurs.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10 to 15 minutes per required detail for each disclosure event, so the total time will depend on how many disclosures you need to log.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.3:disclosure_event_log -->
| Reg Disclosure Id | Reg Customer | Reg Recipient | Reg Timestamp | Reg Source Of Authority |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.3:disclosure_event_log -->

## Column guidance — what to fill in

### Reg Disclosure Id

<<MUST item:B.8.5.3:reg_disclosure_id>>
_Why: Audit trail_

> _Standard text:_ Unique disclosure identifier per row

<<GUIDANCE>>

### Reg Customer

<<MUST item:B.8.5.3:reg_customer>>
_Why: Traceability_

> _Standard text:_ Customer whose PII was disclosed per row

<<GUIDANCE>>

### Reg Recipient

<<MUST item:B.8.5.3:reg_recipient>>
_Why: §8.5.3 — to whom_

> _Standard text:_ Recipient per row

<<GUIDANCE>>

### Reg Timestamp

<<MUST item:B.8.5.3:reg_timestamp>>
_Why: §8.5.3 — when_

> _Standard text:_ Timestamp per row

<<GUIDANCE>>

### Reg Source Of Authority

<<MUST item:B.8.5.3:reg_source_of_authority>>
_Why: §8.5.3 — source of authority_

> _Standard text:_ Source of authority per row

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Customer Notified

<<SHOULD item:B.8.5.3:reg_customer_notified>>
_Why: Integration_

> _Standard text:_ Customer notification flag per row (link to B.8.5.4 if legally-binding request)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
