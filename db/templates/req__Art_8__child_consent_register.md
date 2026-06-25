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

> Per-minor consent record proving the parental-authority path was followed. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.8:child_consent_register -->
<!-- column: item:Art.8:reg_subject_id -->
<!-- column: item:Art.8:reg_claimed_age -->
<!-- column: item:Art.8:reg_route -->
<!-- column: item:Art.8:reg_parental_evidence -->
<!-- column: item:Art.8:reg_timestamp -->
<!-- /TABLE-COLUMNS -->

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

### Reg Claimed Age

<<MUST item:Art.8:reg_claimed_age>>
_Why: Decision trail_

> _Standard text:_ Per-row claimed age at registration

### Reg Route

<<MUST item:Art.8:reg_route>>
_Why: Art.8.1_

> _Standard text:_ Per-row consent route (child if age threshold met / parental if below threshold)

### Reg Parental Evidence

<<MUST item:Art.8:reg_parental_evidence>>
_Why: Art.8.2 — verify_

> _Standard text:_ Per-row parental-authority evidence (where parental route used)

### Reg Timestamp

<<MUST item:Art.8:reg_timestamp>>
_Why: Currency_

> _Standard text:_ Per-row capture timestamp

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Re Verification

<<SHOULD item:Art.8:reg_re_verification>>
_Why: Lifecycle_

> _Standard text:_ Re-verification trigger when minor crosses the age threshold (consent transitions from parental to direct)
