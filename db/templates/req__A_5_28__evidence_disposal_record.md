---
leaf_id: req:A.5.28:evidence_disposal_record
control_ref: A.5.28
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Per-Package Evidence Disposal / Handover Record

> A.5.28 requires that the chain of custody be demonstrable end-to-end — including the *end* of the chain. The disposal record evidences the legitimate closure of each evidence package: either external handover (to law enforcement, regulator, opposing counsel) with receipt OR retention-driven destruction with witness + method + final hash. One record per closed package, traceable back to the custody register and through to the source incident

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Package identifier per record (links to custody register)

<<MUST item:A.5.28:disp_package_ref>>
_Why: 27002:5.28 — traceability_

<<TEXT>>

## 2. Closure type per record (external_handover / retention_destruction / case_closed_internal)

<<MUST item:A.5.28:disp_closure_type>>
_Why: 27002:5.28 — preservation lifecycle_

<<TEXT>>

## 3. Authoriser per record (proportional to closure type — counsel sign-off required for external handover)

<<MUST item:A.5.28:disp_authoriser>>
_Why: Accountability_

<<TEXT>>

## 4. Closure method per record (sealed-handover with receipt OR secure-destruction method with witness)

<<MUST item:A.5.28:disp_method>>
_Why: 27002:5.28 — secure handling_

<<TEXT>>

## 5. Final hash per record (handover destination hash matches register hash OR pre-destruction hash logged)

<<MUST item:A.5.28:disp_final_hash>>
_Why: 27002:5.28 — integrity at end_

<<TEXT>>

## 6. Closure date recorded

<<MUST item:A.5.28:disp_closure_date>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External handover receipt scanned/attached per record (where closure_type = external_handover)

<<SHOULD item:A.5.28:disp_receipt>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Witness identity per destruction record (independent of authoriser where possible)

<<SHOULD item:A.5.28:disp_witness>>
_Why: Operational discipline_

<<TEXT>>
