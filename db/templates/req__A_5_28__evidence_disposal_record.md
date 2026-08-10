---
leaf_id: req:A.5.28:evidence_disposal_record
control_ref: A.5.28
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Per-Package Evidence Disposal / Handover Record

<<DOC_CONTROL>>

> A.5.28 requires that the chain of custody be demonstrable end-to-end — including the *end* of the chain. The disposal record evidences the legitimate closure of each evidence package: either external handover (to law enforcement, regulator, opposing counsel) with receipt OR retention-driven destruction with witness + method + final hash. One record per closed package, traceable back to the custody register and through to the source incident

<!-- TABLE-COLUMNS leaf:req:A.5.28:evidence_disposal_record -->
<!-- column: item:A.5.28:disp_package_ref -->
<!-- column: item:A.5.28:disp_closure_type -->
<!-- column: item:A.5.28:disp_authoriser -->
<!-- column: item:A.5.28:disp_method -->
<!-- column: item:A.5.28:disp_final_hash -->
<!-- column: item:A.5.28:disp_closure_date -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document the final handover or destruction of evidence packages, ensuring you can prove exactly how and when each package leaves your control or is securely destroyed.

## When to use it

Use this record whenever an evidence package is either handed over to an external party or destroyed, and update it as needed for each package closure event.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing a new record for each evidence package, depending on the details required for each element.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.28:evidence_disposal_record -->
| Disp Package Ref | Disp Closure Type | Disp Authoriser | Disp Method | Disp Final Hash | Disp Closure Date |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.28:evidence_disposal_record -->

## Column guidance — what to fill in

### Disp Package Ref

<<MUST item:A.5.28:disp_package_ref>>
_Why: 27002:5.28 — traceability_

> _Standard text:_ Package identifier per record (links to custody register)

<<GUIDANCE>>

### Disp Closure Type

<<MUST item:A.5.28:disp_closure_type>>
_Why: 27002:5.28 — preservation lifecycle_

> _Standard text:_ Closure type per record (external_handover / retention_destruction / case_closed_internal)

<<GUIDANCE>>

### Disp Authoriser

<<MUST item:A.5.28:disp_authoriser>>
_Why: Accountability_

> _Standard text:_ Authoriser per record (proportional to closure type — counsel sign-off required for external handover)

<<GUIDANCE>>

### Disp Method

<<MUST item:A.5.28:disp_method>>
_Why: 27002:5.28 — secure handling_

> _Standard text:_ Closure method per record (sealed-handover with receipt OR secure-destruction method with witness)

<<GUIDANCE>>

### Disp Final Hash

<<MUST item:A.5.28:disp_final_hash>>
_Why: 27002:5.28 — integrity at end_

> _Standard text:_ Final hash per record (handover destination hash matches register hash OR pre-destruction hash logged)

<<GUIDANCE>>

### Disp Closure Date

<<MUST item:A.5.28:disp_closure_date>>
_Why: Operational discipline_

> _Standard text:_ Closure date recorded

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Disp Receipt

<<SHOULD item:A.5.28:disp_receipt>>
_Why: Audit defensibility_

> _Standard text:_ External handover receipt scanned/attached per record (where closure_type = external_handover)

<<GUIDANCE>>

### Disp Witness

<<SHOULD item:A.5.28:disp_witness>>
_Why: Operational discipline_

> _Standard text:_ Witness identity per destruction record (independent of authoriser where possible)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
