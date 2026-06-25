---
leaf_id: req:Art.35:dpia_register
control_ref: Art.35
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# DPIA Register

> Per-DPIA record — every conducted DPIA with outcome (proceed / mitigate / Art.36 consult / abandon). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.35:dpia_register -->
<!-- column: item:Art.35:reg_dpia_id -->
<!-- column: item:Art.35:reg_processing_activity -->
<!-- column: item:Art.35:reg_trigger -->
<!-- column: item:Art.35:reg_dpo_advice_date -->
<!-- column: item:Art.35:reg_outcome -->
<!-- column: item:Art.35:reg_residual_risk -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.35:dpia_register -->
| Reg Dpia Id | Reg Processing Activity | Reg Trigger | Reg Dpo Advice Date | Reg Outcome | Reg Residual Risk |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.35:dpia_register -->

## Column guidance — what to fill in

### Reg Dpia Id

<<MUST item:Art.35:reg_dpia_id>>
_Why: Audit_

> _Standard text:_ Per-row DPIA identifier

### Reg Processing Activity

<<MUST item:Art.35:reg_processing_activity>>
_Why: Cross-article_

> _Standard text:_ Per-row processing activity (Art.30 RoPA cross-reference)

### Reg Trigger

<<MUST item:Art.35:reg_trigger>>
_Why: Art.35.1+3-4_

> _Standard text:_ Per-row trigger (Art.35.3.a-c / SA list / sectoral / risk-based)

### Reg Dpo Advice Date

<<MUST item:Art.35:reg_dpo_advice_date>>
_Why: Art.35.2_

> _Standard text:_ Per-row DPO advice date + summary

### Reg Outcome

<<MUST item:Art.35:reg_outcome>>
_Why: Audit clarity_

> _Standard text:_ Per-row outcome (proceed / mitigate-then-proceed / Art.36 consult / abandon)

### Reg Residual Risk

<<MUST item:Art.35:reg_residual_risk>>
_Why: Art.36 trigger_

> _Standard text:_ Per-row residual-risk level after mitigations

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Review Date

<<SHOULD item:Art.35:reg_review_date>>
_Why: Art.35.11_

> _Standard text:_ Per-row next review date
