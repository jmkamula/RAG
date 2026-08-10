---
leaf_id: req:Art.24:accountability_program_review
control_ref: Art.24
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Accountability Program Review

<<DOC_CONTROL>>

> Annual verification of the accountability frame — charter current, compliance register reflects all in-scope articles, role decisions still hold, ISO 27001 derivations still aligned (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.24:accountability_program_review -->
<!-- column: item:Art.24:rev_date -->
<!-- column: item:Art.24:rev_reviewer -->
<!-- column: item:Art.24:rev_charter_currency -->
<!-- column: item:Art.24:rev_register_completeness -->
<!-- column: item:Art.24:rev_role_currency -->
<!-- column: item:Art.24:rev_iso_alignment -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your accountability program is up-to-date, ensuring your charter, compliance register, and role assignments are still accurate and aligned with GDPR requirements.

## When to use it

Use this review record once a year to check that your accountability framework remains current and compliant, as it always applies to your environment and should be refreshed annually.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, as each required section takes roughly 10-15 minutes to fill in.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.24:accountability_program_review -->
| Rev Date | Rev Reviewer | Rev Charter Currency | Rev Register Completeness | Rev Role Currency | Rev Iso Alignment |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.24:accountability_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.24:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.24:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + executive sponsor)

<<GUIDANCE>>

### Rev Charter Currency

<<MUST item:Art.24:rev_charter_currency>>
_Why: Art.24.1 — reviewed_

> _Standard text:_ Charter currency check — scope + governance still reflect organisational reality

<<GUIDANCE>>

### Rev Register Completeness

<<MUST item:Art.24:rev_register_completeness>>
_Why: Demonstrability_

> _Standard text:_ Compliance register completeness — every applicable GDPR article has a row with current status

<<GUIDANCE>>

### Rev Role Currency

<<MUST item:Art.24:rev_role_currency>>
_Why: Art.4(7-8) drift_

> _Standard text:_ Role decisions current — no counterparty service-shape change unreflected in role decisions

<<GUIDANCE>>

### Rev Iso Alignment

<<MUST item:Art.24:rev_iso_alignment>>
_Why: Cross-standard_

> _Standard text:_ ISO 27001 alignment — derived dependencies (5.1/5.3/9.3/A.5.1/A.5.34/A.5.36) still in compliant state

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.24:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
