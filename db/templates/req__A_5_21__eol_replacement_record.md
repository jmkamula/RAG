---
leaf_id: req:A.5.21:eol_replacement_record
control_ref: A.5.21
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# ICT Component End-of-Life Replacement Records

> A.5.21 requires components to be replaced before they reach end-of-life or end-of-support, or compensated for with stated controls if that is unavoidable. The replacement record evidences the actual execution: replacement selected (with sourcing controls re-applied), the cutover date, and post-replacement verification — or, where replacement was delayed, the compensating controls and risk acceptance

<!-- TABLE-COLUMNS leaf:req:A.5.21:eol_replacement_record -->
<!-- column: item:A.5.21:eol_trigger -->
<!-- column: item:A.5.21:eol_replacement -->
<!-- column: item:A.5.21:eol_cutover -->
<!-- column: item:A.5.21:eol_verification -->
<!-- column: item:A.5.21:eol_authoriser -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.21:eol_replacement_record -->
| Eol Trigger | Eol Replacement | Eol Cutover | Eol Verification | Eol Authoriser |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.21:eol_replacement_record -->

## Column guidance — what to fill in

### Eol Trigger

<<MUST item:A.5.21:eol_trigger>>
_Why: 27002:5.21i_

> _Standard text:_ EOL trigger per record (vendor announcement / contract end / vulnerability-driven decommission)

### Eol Replacement

<<MUST item:A.5.21:eol_replacement>>
_Why: 27002:5.21a,i_

> _Standard text:_ Replacement component selected and sourcing controls re-applied

### Eol Cutover

<<MUST item:A.5.21:eol_cutover>>
_Why: 27002:5.21i_

> _Standard text:_ Cutover date executed (or compensating controls + risk acceptance where replacement was delayed)

### Eol Verification

<<MUST item:A.5.21:eol_verification>>
_Why: 27002:5.21g — assurance_

> _Standard text:_ Post-replacement verification (integrity-verification, functional acceptance)

### Eol Authoriser

<<MUST item:A.5.21:eol_authoriser>>
_Why: Accountability_

> _Standard text:_ Authoriser of the replacement (or of the delay + risk acceptance)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Eol Forecast

<<SHOULD item:A.5.21:eol_forecast>>
_Why: Planning_

> _Standard text:_ Rolling 12-month EOL forecast linked back to the component register

### Eol Lessons

<<SHOULD item:A.5.21:eol_lessons>>
_Why: Continual improvement_

> _Standard text:_ Lessons-learned from the replacement feeding back to the procedure (e.g. sourcing-control gaps)
