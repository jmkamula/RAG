---
leaf_id: req:Art.8:child_consent_register
control_ref: Art.8
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Child Consent Register

<<DOC_CONTROL>>

> Per-minor consent record proving the parental-authority path was followed. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.8:child_consent_register -->
<!-- column: item:Art.8:reg_subject_id -->
<!-- column: item:Art.8:reg_claimed_age -->
<!-- column: item:Art.8:reg_route -->
<!-- column: item:Art.8:reg_parental_evidence -->
<!-- column: item:Art.8:reg_timestamp -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record that parental consent was properly obtained for each child user, supporting your compliance with GDPR requirements for minors.

## When to use it

Use this register whenever you collect personal data from children and need to show that you followed the correct steps to get parental consent. Update it about once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each child, so the total time will depend on how many minors you need to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.8:child_consent_register -->
| Reg Subject Id | Reg Claimed Age | Reg Route | Reg Parental Evidence | Reg Timestamp |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.8:child_consent_register -->

## Column guidance — what to fill in

### Reg Subject Id

<<MUST item:Art.8:reg_subject_id>>
_Why: Demonstrability_

> _Standard text:_ Minor's pseudonymous identifier per row

<<GUIDANCE>>

### Reg Claimed Age

<<MUST item:Art.8:reg_claimed_age>>
_Why: Decision trail_

> _Standard text:_ Per-row claimed age at registration

<<GUIDANCE>>

### Reg Route

<<MUST item:Art.8:reg_route>>
_Why: Art.8.1_

> _Standard text:_ Per-row consent route (child if age threshold met / parental if below threshold)

<<GUIDANCE>>

### Reg Parental Evidence

<<MUST item:Art.8:reg_parental_evidence>>
_Why: Art.8.2 — verify_

> _Standard text:_ Per-row parental-authority evidence (where parental route used)

<<GUIDANCE>>

### Reg Timestamp

<<MUST item:Art.8:reg_timestamp>>
_Why: Currency_

> _Standard text:_ Per-row capture timestamp

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Re Verification

<<SHOULD item:Art.8:reg_re_verification>>
_Why: Lifecycle_

> _Standard text:_ Re-verification trigger when minor crosses the age threshold (consent transitions from parental to direct)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
