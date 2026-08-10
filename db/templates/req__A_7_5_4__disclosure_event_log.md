---
leaf_id: req:A.7.5.4:disclosure_event_log
control_ref: A.7.5.4
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# PII Disclosure Event Log

<<DOC_CONTROL>>

> Per-disclosure-event row — every disclosure with recipient, PII scope, timing, source of authority. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.5.4:disclosure_event_log -->
<!-- column: item:A.7.5.4:reg_disclosure_id -->
<!-- column: item:A.7.5.4:reg_recipient -->
<!-- column: item:A.7.5.4:reg_pii_scope -->
<!-- column: item:A.7.5.4:reg_timestamp -->
<!-- column: item:A.7.5.4:reg_source_of_authority -->
<!-- column: item:A.7.5.4:reg_source_of_disclosure -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of every time personal information is shared, including who received it, what was shared, when, and why. It's designed to support privacy compliance and transparency.

## When to use it

Use this register whenever you disclose personal information to someone outside your organization, and update it at least once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes setting up the initial register, plus 10 to 15 minutes for each new disclosure event you need to log.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5.4:disclosure_event_log -->
| Reg Disclosure Id | Reg Recipient | Reg Pii Scope | Reg Timestamp | Reg Source Of Authority | Reg Source Of Disclosure |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5.4:disclosure_event_log -->

## Column guidance — what to fill in

### Reg Disclosure Id

<<MUST item:A.7.5.4:reg_disclosure_id>>
_Why: Audit trail_

> _Standard text:_ Unique disclosure identifier per row

<<GUIDANCE>>

### Reg Recipient

<<MUST item:A.7.5.4:reg_recipient>>
_Why: §7.5.4 — to whom_

> _Standard text:_ Recipient identity per row

<<GUIDANCE>>

### Reg Pii Scope

<<MUST item:A.7.5.4:reg_pii_scope>>
_Why: §7.5.4 — what PII_

> _Standard text:_ PII scope per row (what was disclosed)

<<GUIDANCE>>

### Reg Timestamp

<<MUST item:A.7.5.4:reg_timestamp>>
_Why: §7.5.4 — at what time_

> _Standard text:_ Timestamp per row

<<GUIDANCE>>

### Reg Source Of Authority

<<MUST item:A.7.5.4:reg_source_of_authority>>
_Why: §7.5.4 — source of authority_

> _Standard text:_ Source of authority per row (statute / contract / court order / customer instruction)

<<GUIDANCE>>

### Reg Source Of Disclosure

<<MUST item:A.7.5.4:reg_source_of_disclosure>>
_Why: §7.5.4 — source of the disclosure_

> _Standard text:_ Internal source of disclosure per row (which team / system released the data)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Customer Notification

<<SHOULD item:A.7.5.4:reg_customer_notification>>
_Why: Integration_

> _Standard text:_ Customer notification flag per row if the disclosure involved customer PII (link to B.8.5.4)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
