---
leaf_id: req:A.8.17:sync_program_review
control_ref: A.8.17
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Clock Sync Program Review

<<DOC_CONTROL>>

> Annual verification — drift compliance per class, source-availability, scope completeness (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.17:sync_program_review -->
<!-- column: item:A.8.17:rev_date -->
<!-- column: item:A.8.17:rev_reviewer -->
<!-- column: item:A.8.17:rev_drift_compliance -->
<!-- column: item:A.8.17:rev_scope_completeness -->
<!-- column: item:A.8.17:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of clock synchronization across your systems, ensuring you meet ISO 27001 requirements for time accuracy and source availability.

## When to use it

Use this template whenever you need to verify and record your environment’s clock sync compliance, which should be done about once every year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend roughly 1 to 1.5 hours completing this from scratch, depending on the number of systems you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.17:sync_program_review -->
| Rev Date | Rev Reviewer | Rev Drift Compliance | Rev Scope Completeness | Rev Findings Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.17:sync_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.17:rev_date>>
_Why: 27002:8.17 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.17:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Infrastructure lead + Security Operations)

<<GUIDANCE>>

### Rev Drift Compliance

<<MUST item:A.8.17:rev_drift_compliance>>
_Why: 27002:8.17 — synchronized_

> _Standard text:_ Drift compliance per class (samples within tolerance)

<<GUIDANCE>>

### Rev Scope Completeness

<<MUST item:A.8.17:rev_scope_completeness>>
_Why: Drift prevention_

> _Standard text:_ Scope-completeness check (new system class covered)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.17:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / scope

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.17:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
