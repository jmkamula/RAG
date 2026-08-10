---
leaf_id: req:Art.17:program_review
control_ref: Art.17
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.17 Erasure Program Review

<<DOC_CONTROL>>

> Annual verification — SLAs met, backup erasure handled, Art.17.3 exception claims defensible, Art.17.2 public-disclosure actions taken where applicable (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.17:program_review -->
<!-- column: item:Art.17:rev_date -->
<!-- column: item:Art.17:rev_reviewer -->
<!-- column: item:Art.17:rev_sla_compliance -->
<!-- column: item:Art.17:rev_backup_handling -->
<!-- column: item:Art.17:rev_exception_defensibility -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of how your organization handles data erasure requests under GDPR, including backup deletion, exception claims, and any required public disclosures.

## When to use it

Use this template once a year to confirm your data erasure processes meet GDPR requirements, especially if you regularly receive or process erasure requests in your environment.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on how many erasure cases or exceptions you need to document in the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.17:program_review -->
| Rev Date | Rev Reviewer | Rev Sla Compliance | Rev Backup Handling | Rev Exception Defensibility |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.17:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.17:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.17:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + ops lead)

<<GUIDANCE>>

### Rev Sla Compliance

<<MUST item:Art.17:rev_sla_compliance>>
_Why: Art.12.3_

> _Standard text:_ SLA compliance (Art.12.3 one-month)

<<GUIDANCE>>

### Rev Backup Handling

<<MUST item:Art.17:rev_backup_handling>>
_Why: Art.17.1_

> _Standard text:_ Backup-handling sample — backups actually purged on cycle, immutable records correctly flagged-not-erased

<<GUIDANCE>>

### Rev Exception Defensibility

<<MUST item:Art.17:rev_exception_defensibility>>
_Why: Art.17.3_

> _Standard text:_ Art.17.3 exception sample — refused requests have defensible exception grounds

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.17:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
