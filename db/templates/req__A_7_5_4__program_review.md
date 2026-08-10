---
leaf_id: req:A.7.5.4:program_review
control_ref: A.7.5.4
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Disclosure Records Program Review

<<DOC_CONTROL>>

> Annual verification — disclosures captured, source-of-authority documented per row, intake-gate functional (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.5.4:program_review -->
<!-- column: item:A.7.5.4:rev_date -->
<!-- column: item:A.7.5.4:rev_reviewer -->
<!-- column: item:A.7.5.4:rev_completeness -->
<!-- column: item:A.7.5.4:rev_authority_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of all your disclosure records, making sure each one has a clear source and that your intake process is working as it should.

## When to use it

Use this template once a year, or whenever your organization meets certain criteria that require a review of disclosure records and processes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes to complete this from scratch, depending on how many disclosures you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5.4:program_review -->
| Rev Date | Rev Reviewer | Rev Completeness | Rev Authority Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5.4:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.5.4:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.5.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal)

<<GUIDANCE>>

### Rev Completeness

<<MUST item:A.7.5.4:rev_completeness>>
_Why: §7.5.4_

> _Standard text:_ Completeness check — investigation + audit disclosures reconciled

<<GUIDANCE>>

### Rev Authority Audit

<<MUST item:A.7.5.4:rev_authority_audit>>
_Why: §7.5.4 — source of authority_

> _Standard text:_ Authority audit — sampled disclosures reviewed for documented authority

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.5.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
