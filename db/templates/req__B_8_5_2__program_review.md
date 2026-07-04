---
leaf_id: req:B.8.5.2:program_review
control_ref: B.8.5.2
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Processor Destinations Program Review

> Annual verification — destinations register + customer disclosures + subprocessor destinations aligned (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.5.2:program_review -->
<!-- column: item:B.8.5.2:rev_date -->
<!-- column: item:B.8.5.2:rev_reviewer -->
<!-- column: item:B.8.5.2:rev_completeness -->
<!-- column: item:B.8.5.2:rev_disclosure_sync -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.2:program_review -->
| Rev Date | Rev Reviewer | Rev Completeness | Rev Disclosure Sync |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.2:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.5.2:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:B.8.5.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Trust + DPO)

### Rev Completeness

<<MUST item:B.8.5.2:rev_completeness>>
_Why: §8.5.2_

> _Standard text:_ Completeness check — actual customer-PII flows reconciled against register

### Rev Disclosure Sync

<<MUST item:B.8.5.2:rev_disclosure_sync>>
_Why: §8.5.2 — available to customers_

> _Standard text:_ Customer-facing disclosure sync (DPA schedule / trust page / on-request material matches register)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.5.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
