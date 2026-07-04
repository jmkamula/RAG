---
leaf_id: req:A.7.2.6:program_review
control_ref: A.7.2.6
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Processor Contract Program Review

> Annual verification — every engaged processor has a current contract, Art.28.3 terms complete, subprocessor authorisations current (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.2.6:program_review -->
<!-- column: item:A.7.2.6:rev_date -->
<!-- column: item:A.7.2.6:rev_reviewer -->
<!-- column: item:A.7.2.6:rev_coverage_check -->
<!-- column: item:A.7.2.6:rev_expiry_sweep -->
<!-- column: item:A.7.2.6:rev_subprocessor_audit -->
<!-- column: item:A.7.2.6:rev_missing_terms_audit -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.6:program_review -->
| Rev Date | Rev Reviewer | Rev Coverage Check | Rev Expiry Sweep | Rev Subprocessor Audit | Rev Missing Terms Audit |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.6:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.2.6:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.2.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Procurement + Legal)

### Rev Coverage Check

<<MUST item:A.7.2.6:rev_coverage_check>>
_Why: §7.2.6 — written contract with any PII processor_

> _Standard text:_ Coverage check — every engaged processor has a signed contract on file

### Rev Expiry Sweep

<<MUST item:A.7.2.6:rev_expiry_sweep>>
_Why: Currency_

> _Standard text:_ Expiry sweep — contracts approaching renewal flagged

### Rev Subprocessor Audit

<<MUST item:A.7.2.6:rev_subprocessor_audit>>
_Why: Art.28.2_

> _Standard text:_ Subprocessor audit — sampled contracts checked for current subprocessor authorisation

### Rev Missing Terms Audit

<<MUST item:A.7.2.6:rev_missing_terms_audit>>
_Why: Art.28.3_

> _Standard text:_ Missing-terms audit — sampled contracts checked against Art.28.3 mandatory list

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.2.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
