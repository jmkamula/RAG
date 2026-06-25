---
leaf_id: req:A.5.11:per_leaver_return_record
control_ref: A.5.11
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Per-Leaver Asset Return Record

> A.5.11 expects each leaver/role-changer to have a closed-out return event — either confirmed return with verification OR documented non-return with risk-accepted write-off. The per-leaver record evidences the actual closure: leaver id, items returned (with itemised verification), items not returned (with reason + write-off authoriser), access-revocation confirmation, dual signoff, closure date. One record per leaver row, traceable back to the register

<!-- TABLE-COLUMNS leaf:req:A.5.11:per_leaver_return_record -->
<!-- column: item:A.5.11:rec_leaver_ref -->
<!-- column: item:A.5.11:rec_items_returned -->
<!-- column: item:A.5.11:rec_items_unreturned -->
<!-- column: item:A.5.11:rec_writeoff_auth -->
<!-- column: item:A.5.11:rec_access_confirmed -->
<!-- column: item:A.5.11:rec_dual_signoff -->
<!-- column: item:A.5.11:rec_closure_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.11:per_leaver_return_record -->
| Rec Leaver Ref | Rec Items Returned | Rec Items Unreturned | Rec Writeoff Auth | Rec Access Confirmed | Rec Dual Signoff | Rec Closure Date |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.11:per_leaver_return_record -->

## Column guidance — what to fill in

### Rec Leaver Ref

<<MUST item:A.5.11:rec_leaver_ref>>
_Why: 27002:5.11 — traceability_

> _Standard text:_ Leaver identifier per record (links to leaver register)

### Rec Items Returned

<<MUST item:A.5.11:rec_items_returned>>
_Why: 27002:5.11 — return verification_

> _Standard text:_ Itemised list of returned items per record (matched against the leaver's asset list from A.5.9)

### Rec Items Unreturned

<<MUST item:A.5.11:rec_items_unreturned>>
_Why: 27002:5.11 — risk-based handling_

> _Standard text:_ Itemised list of NOT-returned items per record (with reason: lost / damaged / kept-by-agreement / dispute)

### Rec Writeoff Auth

<<MUST item:A.5.11:rec_writeoff_auth>>
_Why: Risk discipline_

> _Standard text:_ Write-off authoriser per record where applicable (proportional to asset value; InfoSec sign-off for data-bearing devices)

### Rec Access Confirmed

<<MUST item:A.5.11:rec_access_confirmed>>
_Why: 27002:5.11 — logical asset handling_

> _Standard text:_ Access-revocation confirmed per record (corp accounts disabled, SSO removed, credentials rotated)

### Rec Dual Signoff

<<MUST item:A.5.11:rec_dual_signoff>>
_Why: 27002:5.11 — verification_

> _Standard text:_ Dual signoff per record (returning party + receiving role) — captured even when in-person handover isn't possible (remote attestation)

### Rec Closure Date

<<MUST item:A.5.11:rec_closure_date>>
_Why: Operational discipline_

> _Standard text:_ Closure date recorded

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rec Data Attestation

<<SHOULD item:A.5.11:rec_data_attestation>>
_Why: BYOD coverage_

> _Standard text:_ Data-deletion attestation per record where leaver-personal-device held org data (BYOD scenarios — selective-MDM removal proof or screenshot evidence)

### Rec Post Close Review

<<SHOULD item:A.5.11:rec_post_close_review>>
_Why: Continual assurance_

> _Standard text:_ Post-closure verification window noted (e.g. 30-day check that no stale access reappears)
