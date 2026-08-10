---
leaf_id: req:A.8.15:logging_program_review
control_ref: A.8.15
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Logging Program Review

<<DOC_CONTROL>>

> Periodic verification — source-register currency, silent-source detection, retention compliance, integrity-verification spot-checks (freshness=180; threat landscape volatile)

<!-- TABLE-COLUMNS leaf:req:A.8.15:logging_program_review -->
<!-- column: item:A.8.15:rev_date -->
<!-- column: item:A.8.15:rev_reviewer -->
<!-- column: item:A.8.15:rev_silent_sources -->
<!-- column: item:A.8.15:rev_retention_compliance -->
<!-- column: item:A.8.15:rev_integrity_check -->
<!-- column: item:A.8.15:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you regularly review your logging program, making sure your log sources are up to date, compliant with retention rules, and checked for integrity and silent failures.

## When to use it

Use this review record about every six months, or twice a year, to keep your logging practices aligned with ISO 27001 requirements and to address changes in your environment or threat landscape.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the number of log sources and the detail required for each element.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.15:logging_program_review -->
| Rev Date | Rev Reviewer | Rev Silent Sources | Rev Retention Compliance | Rev Integrity Check | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.15:logging_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.15:rev_date>>
_Why: 27002:8.15 — periodic_

> _Standard text:_ Review date within the planned interval (≤180 days)

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.15:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Security Operations + Infrastructure)

<<GUIDANCE>>

### Rev Silent Sources

<<MUST item:A.8.15:rev_silent_sources>>
_Why: Detection gap closure_

> _Standard text:_ Silent-source detection — sources missing recent events triaged

<<GUIDANCE>>

### Rev Retention Compliance

<<MUST item:A.8.15:rev_retention_compliance>>
_Why: 27002:8.15 — stored_

> _Standard text:_ Retention compliance check (no premature deletion; no over-retention of personal data)

<<GUIDANCE>>

### Rev Integrity Check

<<MUST item:A.8.15:rev_integrity_check>>
_Why: Forensic defensibility_

> _Standard text:_ Integrity-verification spot-check (hash chain or signature validates against retained logs)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.15:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / source register / scope

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.15:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
