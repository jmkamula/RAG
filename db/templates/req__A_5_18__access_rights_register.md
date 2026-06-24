---
leaf_id: req:A.5.18:access_rights_register
control_ref: A.5.18
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Access Rights Register

> A.5.18 requires a central record of access rights — without a register, 'who has access to what' devolves to system-by-system queries that drift apart. The register is the live source of truth: every subject-to-asset right mapped, every grant authorised + dated + statused. It feeds the periodic review (which surveys it) and the revocation record (which closes rows out)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Subject-to-asset rights mapping (who has access to what — drives review and the orphan-access check)

<<MUST item:A.5.18:reg_subject_asset>>
_Why: 27002:5.18f_

<<TEXT>>

## 2. Authoriser captured per grant (named individual, not generic role; drives accountability)

<<MUST item:A.5.18:reg_authoriser>>
_Why: 27002:5.18a, k_

<<TEXT>>

## 3. Grant date captured per row (proves the grant happened in the right order — authorisation → grant, not reverse)

<<MUST item:A.5.18:reg_grant_date>>
_Why: 27002:5.18k_

<<TEXT>>

## 4. Status field per row (active / suspended / revoked) — drives the review's orphan check and the revocation_record lifecycle close-out

<<MUST item:A.5.18:reg_status>>
_Why: 27002:5.18d, g_

<<TEXT>>

## 5. Linkage to A.5.16 identity-management register per row — every access right attaches to a registered identity (no orphan rights pointing to disabled or deleted identities)

<<MUST item:A.5.18:reg_idmgmt_link>>
_Why: A.5.16 coherence — was SHOULD, promoted to MUST_

<<TEXT>>

## 6. Last-verified date per row (when this access was last confirmed still needed — drives staleness detection between formal reviews)

<<MUST item:A.5.18:reg_last_verified>>
_Why: 27002:5.18h — kept current_

<<TEXT>>

## 7. Next review-due date per row (drives the schedule for the periodic review leaf)

<<MUST item:A.5.18:reg_review_due>>
_Why: 27002:5.18h — planned intervals_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Privileged-access rows flagged for A.8.2 oversight (drives separate-tier review and tighter cadence for privileged subset)

<<SHOULD item:A.5.18:reg_privileged_flag>>
_Why: A.8.2 linkage_

<<TEXT>>

### 2. Temporary-access rows flagged with expiry date (drives automated cleanup; complements the procedure's temporary_access SHOULD)

<<SHOULD item:A.5.18:reg_temporary_flag>>
_Why: Operational discipline_

<<TEXT>>

### 3. Business justification stated per grant (why this access is needed — informs review decisions later)

<<SHOULD item:A.5.18:reg_business_justification>>
_Why: Audit defensibility_

<<TEXT>>
