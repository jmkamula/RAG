---
leaf_id: req:A.5.21:eol_replacement_record
control_ref: A.5.21
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# ICT Component End-of-Life Replacement Records

> A.5.21 requires components to be replaced before they reach end-of-life or end-of-support, or compensated for with stated controls if that is unavoidable. The replacement record evidences the actual execution: replacement selected (with sourcing controls re-applied), the cutover date, and post-replacement verification — or, where replacement was delayed, the compensating controls and risk acceptance

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. EOL trigger per record (vendor announcement / contract end / vulnerability-driven decommission)

<<MUST item:A.5.21:eol_trigger>>
_Why: 27002:5.21i_

<<TEXT>>

## 2. Replacement component selected and sourcing controls re-applied

<<MUST item:A.5.21:eol_replacement>>
_Why: 27002:5.21a,i_

<<TEXT>>

## 3. Cutover date executed (or compensating controls + risk acceptance where replacement was delayed)

<<MUST item:A.5.21:eol_cutover>>
_Why: 27002:5.21i_

<<TEXT>>

## 4. Post-replacement verification (integrity-verification, functional acceptance)

<<MUST item:A.5.21:eol_verification>>
_Why: 27002:5.21g — assurance_

<<TEXT>>

## 5. Authoriser of the replacement (or of the delay + risk acceptance)

<<MUST item:A.5.21:eol_authoriser>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Rolling 12-month EOL forecast linked back to the component register

<<SHOULD item:A.5.21:eol_forecast>>
_Why: Planning_

<<TEXT>>

### 2. Lessons-learned from the replacement feeding back to the procedure (e.g. sourcing-control gaps)

<<SHOULD item:A.5.21:eol_lessons>>
_Why: Continual improvement_

<<TEXT>>
