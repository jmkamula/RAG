---
leaf_id: req:7.5:document_control_program_review
control_ref: 7.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Document Control Program Review

<<DOC_CONTROL>>

> Annual verification that the policy is being applied, the register is current, stale documents are surfaced and refreshed (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.5:document_control_program_review -->
<!-- column: item:7.5:rev_date -->
<!-- column: item:7.5:rev_reviewer -->
<!-- column: item:7.5:rev_currency -->
<!-- column: item:7.5:rev_stale_sweep -->
<!-- column: item:7.5:rev_coverage -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep your document control program up to date by reviewing policies, surfacing outdated documents, and ensuring your register is current. It's designed for organizations following ISO 27001 requirements.

## When to use it

Use this template once a year to review your document control program and confirm that all documents are current and policies are being followed. It applies to all environments, regardless of changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this review from scratch, depending on the number of documents in your register and the detail required for each element.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.5:document_control_program_review -->
| Rev Date | Rev Reviewer | Rev Currency | Rev Stale Sweep | Rev Coverage |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.5:document_control_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:7.5:rev_date>>
_Why: Clause 7.5 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:7.5:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + document-control lead)

<<GUIDANCE>>

### Rev Currency

<<MUST item:7.5:rev_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — every row reviewed; next-review dates met or rescheduled

<<GUIDANCE>>

### Rev Stale Sweep

<<MUST item:7.5:rev_stale_sweep>>
_Why: Drift detection_

> _Standard text:_ Stale-document sweep — overdue review dates surfaced; refresh or retire decisions made

<<GUIDANCE>>

### Rev Coverage

<<MUST item:7.5:rev_coverage>>
_Why: Cross-leaf coherence_

> _Standard text:_ Coverage check — every in-scope document class has at least one register entry

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:7.5:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
