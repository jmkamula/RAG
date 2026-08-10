---
leaf_id: req:A.5.18:access_rights_register
control_ref: A.5.18
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
table_shape: true
---

# Access Rights Register

<<DOC_CONTROL>>

> A.5.18 requires a central record of access rights — without a register, 'who has access to what' devolves to system-by-system queries that drift apart. The register is the live source of truth: every subject-to-asset right mapped, every grant authorised + dated + statused. It feeds the periodic review (which surveys it) and the revocation record (which closes rows out)

<!-- TABLE-COLUMNS leaf:req:A.5.18:access_rights_register -->
<!-- column: item:A.5.18:reg_subject_asset -->
<!-- column: item:A.5.18:reg_authoriser -->
<!-- column: item:A.5.18:reg_grant_date -->
<!-- column: item:A.5.18:reg_status -->
<!-- column: item:A.5.18:reg_idmgmt_link -->
<!-- column: item:A.5.18:reg_last_verified -->
<!-- column: item:A.5.18:reg_review_due -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, up-to-date record of who has access to which systems and data in your organization. It makes it easy to see, review, and manage access rights in one place.

## When to use it

Use this register at all times to track access rights across your environment, updating it whenever access is granted, changed, or revoked. Refresh the information as needed to ensure accuracy.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1-2 hours to set up the initial register, depending on the number of access rights you need to record. Ongoing updates will take less time as you add or change entries.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.18:access_rights_register -->
| Reg Subject Asset | Reg Authoriser | Reg Grant Date | Reg Status | Reg Idmgmt Link | Reg Last Verified | Reg Review Due |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.18:access_rights_register -->

## Column guidance — what to fill in

### Reg Subject Asset

<<MUST item:A.5.18:reg_subject_asset>>
_Why: 27002:5.18f_

> _Standard text:_ Subject-to-asset rights mapping (who has access to what — drives review and the orphan-access check)

<<GUIDANCE>>

### Reg Authoriser

<<MUST item:A.5.18:reg_authoriser>>
_Why: 27002:5.18a, k_

> _Standard text:_ Authoriser captured per grant (named individual, not generic role; drives accountability)

<<GUIDANCE>>

### Reg Grant Date

<<MUST item:A.5.18:reg_grant_date>>
_Why: 27002:5.18k_

> _Standard text:_ Grant date captured per row (proves the grant happened in the right order — authorisation → grant, not reverse)

<<GUIDANCE>>

### Reg Status

<<MUST item:A.5.18:reg_status>>
_Why: 27002:5.18d, g_

> _Standard text:_ Status field per row (active / suspended / revoked) — drives the review's orphan check and the revocation_record lifecycle close-out

<<GUIDANCE>>

### Reg Idmgmt Link

<<MUST item:A.5.18:reg_idmgmt_link>>
_Why: A.5.16 coherence — was SHOULD, promoted to MUST_

> _Standard text:_ Linkage to A.5.16 identity-management register per row — every access right attaches to a registered identity (no orphan rights pointing to disabled or deleted identities)

<<GUIDANCE>>

### Reg Last Verified

<<MUST item:A.5.18:reg_last_verified>>
_Why: 27002:5.18h — kept current_

> _Standard text:_ Last-verified date per row (when this access was last confirmed still needed — drives staleness detection between formal reviews)

<<GUIDANCE>>

### Reg Review Due

<<MUST item:A.5.18:reg_review_due>>
_Why: 27002:5.18h — planned intervals_

> _Standard text:_ Next review-due date per row (drives the schedule for the periodic review leaf)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Privileged Flag

<<SHOULD item:A.5.18:reg_privileged_flag>>
_Why: A.8.2 linkage_

> _Standard text:_ Privileged-access rows flagged for A.8.2 oversight (drives separate-tier review and tighter cadence for privileged subset)

<<GUIDANCE>>

### Reg Temporary Flag

<<SHOULD item:A.5.18:reg_temporary_flag>>
_Why: Operational discipline_

> _Standard text:_ Temporary-access rows flagged with expiry date (drives automated cleanup; complements the procedure's temporary_access SHOULD)

<<GUIDANCE>>

### Reg Business Justification

<<SHOULD item:A.5.18:reg_business_justification>>
_Why: Audit defensibility_

> _Standard text:_ Business justification stated per grant (why this access is needed — informs review decisions later)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
