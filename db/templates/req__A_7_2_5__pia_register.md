---
leaf_id: req:A.7.2.5:pia_register
control_ref: A.7.2.5
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 7
should_count: 1
table_shape: true
---

# PIA / DPIA Report Register

> Per-PIA row — the register of completed PIAs (report link + date + signoff + residual risk + review-due date). Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.2.5:pia_register -->
<!-- column: item:A.7.2.5:reg_pia_id -->
<!-- column: item:A.7.2.5:reg_processing_activity -->
<!-- column: item:A.7.2.5:reg_completion_date -->
<!-- column: item:A.7.2.5:reg_signoff -->
<!-- column: item:A.7.2.5:reg_residual_risk -->
<!-- column: item:A.7.2.5:reg_sa_consultation -->
<!-- column: item:A.7.2.5:reg_review_due -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.5:pia_register -->
| Reg Pia Id | Reg Processing Activity | Reg Completion Date | Reg Signoff | Reg Residual Risk | Reg Sa Consultation | Reg Review Due |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.5:pia_register -->

## Column guidance — what to fill in

### Reg Pia Id

<<MUST item:A.7.2.5:reg_pia_id>>
_Why: Referenceability_

> _Standard text:_ Unique PIA identifier per row

### Reg Processing Activity

<<MUST item:A.7.2.5:reg_processing_activity>>
_Why: Traceability_

> _Standard text:_ Processing activity assessed per row

### Reg Completion Date

<<MUST item:A.7.2.5:reg_completion_date>>
_Why: Currency_

> _Standard text:_ PIA completion date per row

### Reg Signoff

<<MUST item:A.7.2.5:reg_signoff>>
_Why: §7.2.5 accountability_

> _Standard text:_ Signoff identities per row (DPO + business owner)

### Reg Residual Risk

<<MUST item:A.7.2.5:reg_residual_risk>>
_Why: Art.35.7.d_

> _Standard text:_ Residual-risk rating per row (low/medium/high after mitigations)

### Reg Sa Consultation

<<MUST item:A.7.2.5:reg_sa_consultation>>
_Why: Art.36.1_

> _Standard text:_ SA consultation flag per row (Art.36 invoked yes/no)

### Reg Review Due

<<MUST item:A.7.2.5:reg_review_due>>
_Why: §7.2.5 — changes to existing processing_

> _Standard text:_ Next review due date per row (triggered by change or periodic)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Mitigations

<<SHOULD item:A.7.2.5:reg_mitigations>>
_Why: Transparency_

> _Standard text:_ Mitigations summary per row
