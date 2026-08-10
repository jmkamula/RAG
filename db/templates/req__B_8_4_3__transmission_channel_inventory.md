---
leaf_id: req:B.8.4.3:transmission_channel_inventory
control_ref: B.8.4.3
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Processor Transmission Channel Inventory

<<DOC_CONTROL>>

> Per-channel row — the transmission channels used for customer PII. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.4.3:transmission_channel_inventory -->
<!-- column: item:B.8.4.3:reg_channel_id -->
<!-- column: item:B.8.4.3:reg_customer -->
<!-- column: item:B.8.4.3:reg_endpoint -->
<!-- column: item:B.8.4.3:reg_encryption -->
<!-- column: item:B.8.4.3:reg_contract_alignment -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of all the channels your organization uses to transmit customer personal data, making it easier to track and manage privacy risks.

## When to use it

Use this document whenever your organization handles customer personal data and needs to keep an up-to-date list of all transmission channels. Plan to review and update it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per channel row, with a total time depending on how many channels you need to document. For five channels, set aside roughly 1 to 1.5 hours.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.4.3:transmission_channel_inventory -->
| Reg Channel Id | Reg Customer | Reg Endpoint | Reg Encryption | Reg Contract Alignment |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.4.3:transmission_channel_inventory -->

## Column guidance — what to fill in

### Reg Channel Id

<<MUST item:B.8.4.3:reg_channel_id>>
_Why: Referenceability_

> _Standard text:_ Unique channel identifier per row

<<GUIDANCE>>

### Reg Customer

<<MUST item:B.8.4.3:reg_customer>>
_Why: Traceability_

> _Standard text:_ Customer per row (if channel is customer-specific)

<<GUIDANCE>>

### Reg Endpoint

<<MUST item:B.8.4.3:reg_endpoint>>
_Why: Traceability_

> _Standard text:_ Source + destination endpoints per row

<<GUIDANCE>>

### Reg Encryption

<<MUST item:B.8.4.3:reg_encryption>>
_Why: GDPR Art.32.1.a_

> _Standard text:_ Encryption standard per row

<<GUIDANCE>>

### Reg Contract Alignment

<<MUST item:B.8.4.3:reg_contract_alignment>>
_Why: §8.4.3 — contract requirements_

> _Standard text:_ Contract-alignment status per row (in / not-in customer B.8.2.1 agreement)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Verified

<<SHOULD item:B.8.4.3:reg_last_verified>>
_Why: Currency_

> _Standard text:_ Last verification date per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
