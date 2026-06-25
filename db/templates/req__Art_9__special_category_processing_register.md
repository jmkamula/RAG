---
leaf_id: req:Art.9:special_category_processing_register
control_ref: Art.9
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Special Category Processing Register

> Per-activity register for every special-category processing operation — which Art.9.1 category, which Art.9.2 condition, what safeguards, what RoPA reference. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.9:special_category_processing_register -->
<!-- column: item:Art.9:reg_activity_id -->
<!-- column: item:Art.9:reg_category -->
<!-- column: item:Art.9:reg_condition -->
<!-- column: item:Art.9:reg_safeguards -->
<!-- column: item:Art.9:reg_approval -->
<!-- column: item:Art.9:reg_ropa_xref -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.9:special_category_processing_register -->
| Reg Activity Id | Reg Category | Reg Condition | Reg Safeguards | Reg Approval | Reg Ropa Xref |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.9:special_category_processing_register -->

## Column guidance — what to fill in

### Reg Activity Id

<<MUST item:Art.9:reg_activity_id>>
_Why: Audit defensibility_

> _Standard text:_ Activity identifier per row (links to Art.30 RoPA)

### Reg Category

<<MUST item:Art.9:reg_category>>
_Why: Art.9.1_

> _Standard text:_ Art.9.1 category per row (which special category)

### Reg Condition

<<MUST item:Art.9:reg_condition>>
_Why: Art.9.2_

> _Standard text:_ Art.9.2 condition per row (a-j) with citation

### Reg Safeguards

<<MUST item:Art.9:reg_safeguards>>
_Why: Art.9.3_

> _Standard text:_ Safeguards in place per row (Art.9.3 secrecy where applicable; technical + organisational measures)

### Reg Approval

<<MUST item:Art.9:reg_approval>>
_Why: Accountability_

> _Standard text:_ Per-row approval signature + date

### Reg Ropa Xref

<<MUST item:Art.9:reg_ropa_xref>>
_Why: Cross-article coherence_

> _Standard text:_ Per-row cross-reference to Art.30 RoPA entry

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Member State

<<SHOULD item:Art.9:reg_member_state>>
_Why: Art.9.4_

> _Standard text:_ Per-row Member State law overlay where Art.9.4 derogations apply
