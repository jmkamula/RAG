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

<<DOC_CONTROL>>

> A.5.21 requires components to be replaced before they reach end-of-life or end-of-support, or compensated for with stated controls if that is unavoidable. The replacement record evidences the actual execution: replacement selected (with sourcing controls re-applied), the cutover date, and post-replacement verification — or, where replacement was delayed, the compensating controls and risk acceptance

<!-- TABLE-COLUMNS leaf:req:A.5.21:eol_replacement_record -->
<!-- column: item:A.5.21:eol_trigger -->
<!-- column: item:A.5.21:eol_replacement -->
<!-- column: item:A.5.21:eol_cutover -->
<!-- column: item:A.5.21:eol_verification -->
<!-- column: item:A.5.21:eol_authoriser -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document the replacement of IT components that are reaching the end of their supported life, ensuring you have a clear record of what was replaced, when, and how it was verified.

## When to use it

Use this whenever you replace or delay replacing IT components that are no longer supported, and update it as needed whenever such events occur in your environment.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing the required sections for each component, with additional time needed as you add more entries to the register.

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

<<GUIDANCE>>

### Eol Replacement

<<MUST item:A.5.21:eol_replacement>>
_Why: 27002:5.21a,i_

> _Standard text:_ Replacement component selected and sourcing controls re-applied

<<GUIDANCE>>

### Eol Cutover

<<MUST item:A.5.21:eol_cutover>>
_Why: 27002:5.21i_

> _Standard text:_ Cutover date executed (or compensating controls + risk acceptance where replacement was delayed)

<<GUIDANCE>>

### Eol Verification

<<MUST item:A.5.21:eol_verification>>
_Why: 27002:5.21g — assurance_

> _Standard text:_ Post-replacement verification (integrity-verification, functional acceptance)

<<GUIDANCE>>

### Eol Authoriser

<<MUST item:A.5.21:eol_authoriser>>
_Why: Accountability_

> _Standard text:_ Authoriser of the replacement (or of the delay + risk acceptance)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Eol Forecast

<<SHOULD item:A.5.21:eol_forecast>>
_Why: Planning_

> _Standard text:_ Rolling 12-month EOL forecast linked back to the component register

<<GUIDANCE>>

### Eol Lessons

<<SHOULD item:A.5.21:eol_lessons>>
_Why: Continual improvement_

> _Standard text:_ Lessons-learned from the replacement feeding back to the procedure (e.g. sourcing-control gaps)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
