---
leaf_id: req:Art.85:national_law_derogation_register
control_ref: Art.85
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Per-Jurisdiction Art.85 National Law Derogation Register

> Per-jurisdiction record of the national-law provisions invoked for Art.85 derogations. One row per (Member State × derogated GDPR provision × activity scope) tuple. Refreshed at the national-law currency cadence — annual review minimum (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.85:national_law_derogation_register -->
<!-- column: item:Art.85:reg_owner -->
<!-- column: item:Art.85:reg_member_state -->
<!-- column: item:Art.85:reg_national_provision -->
<!-- column: item:Art.85:reg_derogated_articles -->
<!-- column: item:Art.85:reg_activity_scope -->
<!-- column: item:Art.85:reg_currency_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.85:national_law_derogation_register -->
| Reg Owner | Reg Member State | Reg National Provision | Reg Derogated Articles | Reg Activity Scope | Reg Currency Date |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.85:national_law_derogation_register -->

## Column guidance — what to fill in

### Reg Owner

<<MUST item:Art.85:reg_owner>>
_Why: Accountability_

> _Standard text:_ Named owner of the register

### Reg Member State

<<MUST item:Art.85:reg_member_state>>
_Why: Art.85.2 — Member State law_

> _Standard text:_ Per-row Member State whose national law is being invoked

### Reg National Provision

<<MUST item:Art.85:reg_national_provision>>
_Why: Demonstrability_

> _Standard text:_ Per-row specific national-law citation (statute + section + as-of date)

### Reg Derogated Articles

<<MUST item:Art.85:reg_derogated_articles>>
_Why: Art.85.2 — scope of permissible derogations_

> _Standard text:_ Per-row enumeration of GDPR articles being derogated (must be from Chapter II/III/IV/V/VI/VII/IX)

### Reg Activity Scope

<<MUST item:Art.85:reg_activity_scope>>
_Why: Art.85.1_

> _Standard text:_ Per-row activity scope (which processing this derogation covers — journalism / academic / artistic / literary)

### Reg Currency Date

<<MUST item:Art.85:reg_currency_date>>
_Why: Art.85.2 — current state of law_

> _Standard text:_ Per-row as-of-date of the national-law citation (proves the law cited is still in force)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Commission Notification

<<SHOULD item:Art.85:reg_commission_notification>>
_Why: Art.85.3 — Commission notification_

> _Standard text:_ Reference to Member State notification to Commission per Art.85.3 (where available)

### Reg Review Date

<<SHOULD item:Art.85:reg_review_date>>
_Why: Currency_

> _Standard text:_ Per-row next planned review date
