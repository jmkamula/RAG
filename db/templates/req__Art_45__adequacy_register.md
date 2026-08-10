---
leaf_id: req:Art.45:adequacy_register
control_ref: Art.45
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Adequacy Reliance Register

<<DOC_CONTROL>>

> Per-transfer record proving adequacy reliance is current and recipient is eligible. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.45:adequacy_register -->
<!-- column: item:Art.45:reg_transfer_id -->
<!-- column: item:Art.45:reg_adequacy_decision -->
<!-- column: item:Art.45:reg_recipient_eligible -->
<!-- column: item:Art.45:reg_last_verified -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record showing that your international data transfers meet GDPR adequacy requirements and that each recipient remains eligible. It's useful for demonstrating compliance during audits or reviews.

## When to use it

Use this register whenever you transfer personal data to countries or organizations relying on adequacy decisions. Update it about once a year, or whenever there are changes to your transfers or recipients.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40-60 minutes to complete the required sections for each transfer recipient, with additional time needed as you add more entries over time.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.45:adequacy_register -->
| Reg Transfer Id | Reg Adequacy Decision | Reg Recipient Eligible | Reg Last Verified |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.45:adequacy_register -->

## Column guidance — what to fill in

### Reg Transfer Id

<<MUST item:Art.45:reg_transfer_id>>
_Why: Cross-leaf_

> _Standard text:_ Per-row transfer id (Art.44 register cross-ref)

<<GUIDANCE>>

### Reg Adequacy Decision

<<MUST item:Art.45:reg_adequacy_decision>>
_Why: Art.45.3_

> _Standard text:_ Per-row adequacy decision cited (Commission decision reference + effective date)

<<GUIDANCE>>

### Reg Recipient Eligible

<<MUST item:Art.45:reg_recipient_eligible>>
_Why: Art.45.3 partial_

> _Standard text:_ Per-row recipient-eligibility status (e.g. US-DPF active certification verified)

<<GUIDANCE>>

### Reg Last Verified

<<MUST item:Art.45:reg_last_verified>>
_Why: Currency_

> _Standard text:_ Per-row last-verified date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Invalidation Watch

<<SHOULD item:Art.45:reg_invalidation_watch>>
_Why: Schrems-style risk_

> _Standard text:_ Per-row invalidation-watch flag (active CJEU challenges / Commission review status)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
