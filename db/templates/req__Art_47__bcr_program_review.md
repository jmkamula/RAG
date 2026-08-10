---
leaf_id: req:Art.47:bcr_program_review
control_ref: Art.47
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# BCR Program Review

<<DOC_CONTROL>>

> Annual verification — every bound entity still in compliance, complaints handled per Art.47.2.i, training delivered, lead SA notified of material changes (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.47:bcr_program_review -->
<!-- column: item:Art.47:rev_date -->
<!-- column: item:Art.47:rev_reviewer -->
<!-- column: item:Art.47:rev_compliance_audit -->
<!-- column: item:Art.47:rev_complaints_handled -->
<!-- column: item:Art.47:rev_change_notification -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record that your Binding Corporate Rules (BCR) program is up to date, including compliance checks, complaint handling, staff training, and notifications of important changes.

## When to use it

Use this template if your organization is subject to GDPR and needs to review its BCR program, especially when your compliance profile changes or at least once every year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as each required section takes around 10–15 minutes to fill in.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.47:bcr_program_review -->
| Rev Date | Rev Reviewer | Rev Compliance Audit | Rev Complaints Handled | Rev Change Notification |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.47:bcr_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.47:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.47:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + group privacy lead)

<<GUIDANCE>>

### Rev Compliance Audit

<<MUST item:Art.47:rev_compliance_audit>>
_Why: Art.47.2.j_

> _Standard text:_ Compliance audit — bound entities adhering to BCR provisions (sampled audit results)

<<GUIDANCE>>

### Rev Complaints Handled

<<MUST item:Art.47:rev_complaints_handled>>
_Why: Art.47.2.i_

> _Standard text:_ Complaints-handling audit — Art.47.2.i path functioning + SAs receiving cooperation

<<GUIDANCE>>

### Rev Change Notification

<<MUST item:Art.47:rev_change_notification>>
_Why: Art.47.2.k_

> _Standard text:_ Material-change notification — significant changes notified to lead SA per Art.63 consistency

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.47:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
