---
leaf_id: req:A.7.3.7:program_review
control_ref: A.7.3.7
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Third-Party Notification Program Review

<<DOC_CONTROL>>

> Annual verification — recipient inventory current, notifications issued reliably, acknowledgements tracked, impossibility invocations defensible (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.7:program_review -->
<!-- column: item:A.7.3.7:rev_date -->
<!-- column: item:A.7.3.7:rev_reviewer -->
<!-- column: item:A.7.3.7:rev_recipient_currency -->
<!-- column: item:A.7.3.7:rev_dispatch_audit -->
<!-- column: item:A.7.3.7:rev_impossibility_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of which third parties need to be notified about privacy matters, making sure your records are up to date and all notifications and responses are properly documented.

## When to use it

Use this template if your organization is required to review and confirm its third-party notification process, especially when your activities match certain privacy-related triggers. Plan to update it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on the number of third parties you need to document and the availability of your records.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.7:program_review -->
| Rev Date | Rev Reviewer | Rev Recipient Currency | Rev Dispatch Audit | Rev Impossibility Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.7:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.7:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.3.7:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Vendor Management)

<<GUIDANCE>>

### Rev Recipient Currency

<<MUST item:A.7.3.7:rev_recipient_currency>>
_Why: §7.3.7 — determine and maintain_

> _Standard text:_ Recipient inventory currency — reconciled against A.7.5.4 disclosure register

<<GUIDANCE>>

### Rev Dispatch Audit

<<MUST item:A.7.3.7:rev_dispatch_audit>>
_Why: Coverage_

> _Standard text:_ Dispatch audit — sampled subject events verified to have generated corresponding third-party notifications

<<GUIDANCE>>

### Rev Impossibility Audit

<<MUST item:A.7.3.7:rev_impossibility_audit>>
_Why: Art.19_

> _Standard text:_ Impossibility-invocation audit — sampled invocations reviewed for defensibility

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.7:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
