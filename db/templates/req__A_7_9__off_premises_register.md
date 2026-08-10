---
leaf_id: req:A.7.9:off_premises_register
control_ref: A.7.9
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Off-Premises Asset Register

<<DOC_CONTROL>>

> The catalogue of assets currently off-premises — laptops issued, equipment taken to events, media in transit. Drives 'where is asset X right now' query and loss-detection

<!-- TABLE-COLUMNS leaf:req:A.7.9:off_premises_register -->
<!-- column: item:A.7.9:reg_asset_id -->
<!-- column: item:A.7.9:reg_holder -->
<!-- column: item:A.7.9:reg_off_since -->
<!-- column: item:A.7.9:reg_expected_return -->
<!-- column: item:A.7.9:reg_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of all assets that are currently off your premises, such as laptops, equipment at events, or media in transit. It makes it easy to answer questions about the location of any asset and helps with loss detection.

## When to use it

Use this register whenever you have assets leaving your main location, and update it as needed whenever assets move off-site or return. It should always be maintained to reflect your current environment.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each asset. Setting up the register for the first time may take around an hour, with ongoing updates taking just a few minutes per new entry.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.9:off_premises_register -->
| Reg Asset Id | Reg Holder | Reg Off Since | Reg Expected Return | Reg Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.9:off_premises_register -->

## Column guidance — what to fill in

### Reg Asset Id

<<MUST item:A.7.9:reg_asset_id>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row asset identifier (cross-link to A.5.9 asset register)

<<GUIDANCE>>

### Reg Holder

<<MUST item:A.7.9:reg_holder>>
_Why: Accountability_

> _Standard text:_ Per-row current holder (named individual)

<<GUIDANCE>>

### Reg Off Since

<<MUST item:A.7.9:reg_off_since>>
_Why: Operational discipline_

> _Standard text:_ Per-row off-premises date (drives stale-loaner detection)

<<GUIDANCE>>

### Reg Expected Return

<<MUST item:A.7.9:reg_expected_return>>
_Why: 27002:7.9 — registration_

> _Standard text:_ Per-row expected return date where applicable

<<GUIDANCE>>

### Reg Status

<<MUST item:A.7.9:reg_status>>
_Why: Lifecycle_

> _Standard text:_ Per-row status (active-off-premises / returned / lost / stolen / written-off)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Purpose

<<SHOULD item:A.7.9:reg_purpose>>
_Why: Risk profile_

> _Standard text:_ Per-row purpose (daily-loaner / conference / customer-visit / permanent-issue)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
