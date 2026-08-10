---
leaf_id: req:B.8.5.1:transfer_basis_register
control_ref: B.8.5.1
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Processor Transfer Basis Register

<<DOC_CONTROL>>

> Per-transfer-relationship row — every cross-jurisdiction transfer (including via subprocessors) with basis + customer-disclosure status. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.5.1:transfer_basis_register -->
<!-- column: item:B.8.5.1:reg_relationship_id -->
<!-- column: item:B.8.5.1:reg_jurisdiction_pair -->
<!-- column: item:B.8.5.1:reg_basis -->
<!-- column: item:B.8.5.1:reg_customer_notification_date -->
<!-- column: item:B.8.5.1:reg_change_history -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of each time personal data is transferred across borders, including through subprocessors, and shows the legal basis and whether your customers have been informed.

## When to use it

Use this register whenever your organization transfers personal data to another country, especially if you work with subprocessors. Update it about once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each transfer relationship. If you have several transfers, filling out the register from scratch could take a few hours.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.1:transfer_basis_register -->
| Reg Relationship Id | Reg Jurisdiction Pair | Reg Basis | Reg Customer Notification Date | Reg Change History |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.1:transfer_basis_register -->

## Column guidance — what to fill in

### Reg Relationship Id

<<MUST item:B.8.5.1:reg_relationship_id>>
_Why: Referenceability_

> _Standard text:_ Unique transfer relationship identifier per row

<<GUIDANCE>>

### Reg Jurisdiction Pair

<<MUST item:B.8.5.1:reg_jurisdiction_pair>>
_Why: Traceability_

> _Standard text:_ Origin + destination jurisdiction per row

<<GUIDANCE>>

### Reg Basis

<<MUST item:B.8.5.1:reg_basis>>
_Why: §8.5.1_

> _Standard text:_ Basis cited per row (Art.45/46/47/49 or equivalent)

<<GUIDANCE>>

### Reg Customer Notification Date

<<MUST item:B.8.5.1:reg_customer_notification_date>>
_Why: §8.5.1 — inform customer_

> _Standard text:_ Customer notification date per row

<<GUIDANCE>>

### Reg Change History

<<MUST item:B.8.5.1:reg_change_history>>
_Why: §8.5.1 — inform in advance_

> _Standard text:_ Change history per row (all previous bases + notification dates)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Customer Ack

<<SHOULD item:B.8.5.1:reg_customer_ack>>
_Why: Confirmation_

> _Standard text:_ Customer acknowledgement per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
