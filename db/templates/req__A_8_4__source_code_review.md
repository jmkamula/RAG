---
leaf_id: req:A.8.4:source_code_review
control_ref: A.8.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 180
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Source Code Access Review

> Periodic verification that repository access is current, dependency allowlist is current, and the monitoring log shows expected hygiene (freshness=180; dev landscape changes fast)

<!-- TABLE-COLUMNS leaf:req:A.8.4:source_code_review -->
<!-- column: item:A.8.4:rev_date -->
<!-- column: item:A.8.4:rev_reviewer -->
<!-- column: item:A.8.4:rev_access_sample -->
<!-- column: item:A.8.4:rev_dep_currency -->
<!-- column: item:A.8.4:rev_findings_closed -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.4:source_code_review -->
| Rev Date | Rev Reviewer | Rev Access Sample | Rev Dep Currency | Rev Findings Closed |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.4:source_code_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.4:rev_date>>
_Why: 27002:8.4 — periodic_

> _Standard text:_ Review date within the planned interval (≤180 days)

### Rev Reviewer

<<MUST item:A.8.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Engineering + InfoSec)

### Rev Access Sample

<<MUST item:A.8.4:rev_access_sample>>
_Why: Drift prevention_

> _Standard text:_ Sample-based repo access verification (per-repo admin and write list re-confirmed)

### Rev Dep Currency

<<MUST item:A.8.4:rev_dep_currency>>
_Why: Supply chain hygiene_

> _Standard text:_ Dependency-allowlist currency check (no abandoned libraries; vulnerable versions retired)

### Rev Findings Closed

<<MUST item:A.8.4:rev_findings_closed>>
_Why: Closes the loop_

> _Standard text:_ Outstanding scanner findings reviewed (closed / accepted / extended)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
