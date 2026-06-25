---
leaf_id: req:Art.40:adherence_register
control_ref: Art.40
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Code Adherence Register

> Per-code register listing adhered codes + status. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.40:adherence_register -->
<!-- column: item:Art.40:reg_code_id -->
<!-- column: item:Art.40:reg_adherence_date -->
<!-- column: item:Art.40:reg_scope -->
<!-- column: item:Art.40:reg_monitoring_body -->
<!-- column: item:Art.40:reg_status -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.40:adherence_register -->
| Reg Code Id | Reg Adherence Date | Reg Scope | Reg Monitoring Body | Reg Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.40:adherence_register -->

## Column guidance — what to fill in

### Reg Code Id

<<MUST item:Art.40:reg_code_id>>
_Why: Audit_

> _Standard text:_ Per-row code identifier (name + association + approval reference)

### Reg Adherence Date

<<MUST item:Art.40:reg_adherence_date>>
_Why: Currency_

> _Standard text:_ Per-row adherence date

### Reg Scope

<<MUST item:Art.40:reg_scope>>
_Why: Defensibility_

> _Standard text:_ Per-row scope of adherence (which processing activities)

### Reg Monitoring Body

<<MUST item:Art.40:reg_monitoring_body>>
_Why: Art.41_

> _Standard text:_ Per-row monitoring body engaged (Art.41)

### Reg Status

<<MUST item:Art.40:reg_status>>
_Why: Lifecycle_

> _Standard text:_ Per-row status (active / suspended / withdrawn-on-date)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Assessment

<<SHOULD item:Art.40:reg_last_assessment>>
_Why: Currency_

> _Standard text:_ Per-row last monitoring assessment date
