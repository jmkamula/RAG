---
leaf_id: req:Art.38:position_evidence_register
control_ref: Art.38
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# DPO Position Evidence Register

> Per-period record of position-guarantee evidence (board attendance, budget approval, independence demonstrations). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.38:position_evidence_register -->
<!-- column: item:Art.38:reg_period -->
<!-- column: item:Art.38:reg_board_attendance -->
<!-- column: item:Art.38:reg_budget_approval -->
<!-- column: item:Art.38:reg_independence_signal -->
<!-- column: item:Art.38:reg_coi_attestation -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.38:position_evidence_register -->
| Reg Period | Reg Board Attendance | Reg Budget Approval | Reg Independence Signal | Reg Coi Attestation |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.38:position_evidence_register -->

## Column guidance — what to fill in

### Reg Period

<<MUST item:Art.38:reg_period>>
_Why: Cadence_

> _Standard text:_ Per-row reporting period (typically quarterly)

### Reg Board Attendance

<<MUST item:Art.38:reg_board_attendance>>
_Why: Art.38.3 — reporting line_

> _Standard text:_ Per-row board / management forum attendance evidence

### Reg Budget Approval

<<MUST item:Art.38:reg_budget_approval>>
_Why: Art.38.2_

> _Standard text:_ Per-row budget approval / spend evidence (Art.38.2 resources)

### Reg Independence Signal

<<MUST item:Art.38:reg_independence_signal>>
_Why: Art.38.3_

> _Standard text:_ Per-row independence signals (no overruled DPO opinion; if overruled, formal record + escalation)

### Reg Coi Attestation

<<MUST item:Art.38:reg_coi_attestation>>
_Why: Art.38.6_

> _Standard text:_ Per-row conflict-of-interest re-attestation (Art.38.6)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Training

<<SHOULD item:Art.38:reg_training>>
_Why: Cross-article_

> _Standard text:_ Per-row training / development hours (sustains expertise per Art.37.5)
