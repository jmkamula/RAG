---
leaf_id: req:6.2:objectives_program_review
control_ref: 6.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Objectives Program Review

> Annual verification that objectives reflect current policy + risk reality, owners are tracking, KPIs are reporting (freshness=365)

<!-- TABLE-COLUMNS leaf:req:6.2:objectives_program_review -->
<!-- column: item:6.2:rev_date -->
<!-- column: item:6.2:rev_reviewer -->
<!-- column: item:6.2:rev_currency -->
<!-- column: item:6.2:rev_alignment -->
<!-- column: item:6.2:rev_kpi_health -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:6.2:objectives_program_review -->
| Rev Date | Rev Reviewer | Rev Currency | Rev Alignment | Rev Kpi Health |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:6.2:objectives_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:6.2:rev_date>>
_Why: Clause 6.2 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:6.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + function heads)

### Rev Currency

<<MUST item:6.2:rev_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — every objective reviewed (refreshed / closed / re-targeted)

### Rev Alignment

<<MUST item:6.2:rev_alignment>>
_Why: Clause 6.2 a) + c)_

> _Standard text:_ Alignment check — objectives still consistent with current 5.2 policy + 6.1.2 risk results

### Rev Kpi Health

<<MUST item:6.2:rev_kpi_health>>
_Why: Clause 6.2 b)_

> _Standard text:_ KPI health check — measurements actually flowing for measurable objectives

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:6.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
