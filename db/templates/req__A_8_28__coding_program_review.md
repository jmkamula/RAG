---
leaf_id: req:A.8.28:coding_program_review
control_ref: A.8.28
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Secure Coding Program Review

<<DOC_CONTROL>>

> Annual verification — finding-pattern trending, tooling currency, language-standard updates (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.28:coding_program_review -->
<!-- column: item:A.8.28:rev_date -->
<!-- column: item:A.8.28:rev_reviewer -->
<!-- column: item:A.8.28:rev_finding_patterns -->
<!-- column: item:A.8.28:rev_tooling_currency -->
<!-- column: item:A.8.28:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your secure coding practices, including trends in code issues, updates to tools, and changes in programming language standards. It’s designed to support annual reviews for compliance and improvement.

## When to use it

Use this template once a year, or whenever your organization’s profile matches specific compliance triggers, to review and document your secure coding program’s effectiveness and currency.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this review from scratch, depending on the amount of information you need to gather for each required section.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.28:coding_program_review -->
| Rev Date | Rev Reviewer | Rev Finding Patterns | Rev Tooling Currency | Rev Findings Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.28:coding_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.28:rev_date>>
_Why: 27002:8.28 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.28:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Engineering leads + Security Champions)

<<GUIDANCE>>

### Rev Finding Patterns

<<MUST item:A.8.28:rev_finding_patterns>>
_Why: Continuous improvement_

> _Standard text:_ Finding-pattern trending (recurring patterns → training / tooling action)

<<GUIDANCE>>

### Rev Tooling Currency

<<MUST item:A.8.28:rev_tooling_currency>>
_Why: 27002:8.28 — applied_

> _Standard text:_ Tooling-stack currency (SAST / SCA rules current; new tooling adopted)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.28:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to language standards / training

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.28:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
