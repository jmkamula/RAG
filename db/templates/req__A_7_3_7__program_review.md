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

> Annual verification — recipient inventory current, notifications issued reliably, acknowledgements tracked, impossibility invocations defensible (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.7:program_review -->
<!-- column: item:A.7.3.7:rev_date -->
<!-- column: item:A.7.3.7:rev_reviewer -->
<!-- column: item:A.7.3.7:rev_recipient_currency -->
<!-- column: item:A.7.3.7:rev_dispatch_audit -->
<!-- column: item:A.7.3.7:rev_impossibility_audit -->
<!-- /TABLE-COLUMNS -->

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

### Rev Reviewer

<<MUST item:A.7.3.7:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Vendor Management)

### Rev Recipient Currency

<<MUST item:A.7.3.7:rev_recipient_currency>>
_Why: §7.3.7 — determine and maintain_

> _Standard text:_ Recipient inventory currency — reconciled against A.7.5.4 disclosure register

### Rev Dispatch Audit

<<MUST item:A.7.3.7:rev_dispatch_audit>>
_Why: Coverage_

> _Standard text:_ Dispatch audit — sampled subject events verified to have generated corresponding third-party notifications

### Rev Impossibility Audit

<<MUST item:A.7.3.7:rev_impossibility_audit>>
_Why: Art.19_

> _Standard text:_ Impossibility-invocation audit — sampled invocations reviewed for defensibility

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.7:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
