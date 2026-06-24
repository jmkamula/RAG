---
leaf_id: req:A.5.11:per_leaver_return_record
control_ref: A.5.11
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Per-Leaver Asset Return Record

> A.5.11 expects each leaver/role-changer to have a closed-out return event — either confirmed return with verification OR documented non-return with risk-accepted write-off. The per-leaver record evidences the actual closure: leaver id, items returned (with itemised verification), items not returned (with reason + write-off authoriser), access-revocation confirmation, dual signoff, closure date. One record per leaver row, traceable back to the register

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Leaver identifier per record (links to leaver register)

<<MUST item:A.5.11:rec_leaver_ref>>
_Why: 27002:5.11 — traceability_

<<TEXT>>

## 2. Itemised list of returned items per record (matched against the leaver's asset list from A.5.9)

<<MUST item:A.5.11:rec_items_returned>>
_Why: 27002:5.11 — return verification_

<<TEXT>>

## 3. Itemised list of NOT-returned items per record (with reason: lost / damaged / kept-by-agreement / dispute)

<<MUST item:A.5.11:rec_items_unreturned>>
_Why: 27002:5.11 — risk-based handling_

<<TEXT>>

## 4. Write-off authoriser per record where applicable (proportional to asset value; InfoSec sign-off for data-bearing devices)

<<MUST item:A.5.11:rec_writeoff_auth>>
_Why: Risk discipline_

<<TEXT>>

## 5. Access-revocation confirmed per record (corp accounts disabled, SSO removed, credentials rotated)

<<MUST item:A.5.11:rec_access_confirmed>>
_Why: 27002:5.11 — logical asset handling_

<<TEXT>>

## 6. Dual signoff per record (returning party + receiving role) — captured even when in-person handover isn't possible (remote attestation)

<<MUST item:A.5.11:rec_dual_signoff>>
_Why: 27002:5.11 — verification_

<<TEXT>>

## 7. Closure date recorded

<<MUST item:A.5.11:rec_closure_date>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Data-deletion attestation per record where leaver-personal-device held org data (BYOD scenarios — selective-MDM removal proof or screenshot evidence)

<<SHOULD item:A.5.11:rec_data_attestation>>
_Why: BYOD coverage_

<<TEXT>>

### 2. Post-closure verification window noted (e.g. 30-day check that no stale access reappears)

<<SHOULD item:A.5.11:rec_post_close_review>>
_Why: Continual assurance_

<<TEXT>>
