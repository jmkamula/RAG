---
leaf_id: req:B.8.2.3:program_review
control_ref: B.8.2.3
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Marketing Use Program Review

<<DOC_CONTROL>>

> Annual verification — customer-PII isolation from marketing intact, exceptions defensible + honoured, no conditionality drift (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.2.3:program_review -->
<!-- column: item:B.8.2.3:rev_date -->
<!-- column: item:B.8.2.3:rev_reviewer -->
<!-- column: item:B.8.2.3:rev_isolation_audit -->
<!-- column: item:B.8.2.3:rev_conditionality_check -->
<!-- column: item:B.8.2.3:rev_exception_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document and review how customer personal information is kept separate from marketing activities, ensuring any exceptions are justified and respected. It supports compliance with privacy standards and annual audit needs.

## When to use it

Use this template if your organization handles customer data and needs to verify, about once a year, that marketing programs do not misuse personal information. It applies when your business profile matches certain privacy-related triggers.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend around 50 to 75 minutes completing this template from scratch, as it requires detailed input for five main areas in a tabular format.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.3:program_review -->
| Rev Date | Rev Reviewer | Rev Isolation Audit | Rev Conditionality Check | Rev Exception Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.3:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.2.3:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.2.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Marketing Lead)

<<GUIDANCE>>

### Rev Isolation Audit

<<MUST item:B.8.2.3:rev_isolation_audit>>
_Why: §8.2.3 — shall not use_

> _Standard text:_ Isolation audit — marketing systems verified to use own-controller PII only

<<GUIDANCE>>

### Rev Conditionality Check

<<MUST item:B.8.2.3:rev_conditionality_check>>
_Why: §8.2.3 — shall not make consent a condition_

> _Standard text:_ No-conditionality regression check — signup / renewal / support flows not gated on marketing consent

<<GUIDANCE>>

### Rev Exception Audit

<<MUST item:B.8.2.3:rev_exception_audit>>
_Why: §8.2.3 — prior consent_

> _Standard text:_ Exception audit — any registered exceptions still defensible + consent evidence current

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.2.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
