---
leaf_id: req:A.8.26:appsec_program_review
control_ref: A.8.26
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Application Security Requirements Review

> Annual verification — requirements catalogue currency vs threat landscape, traceability sample, exception inventory (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.26:appsec_program_review -->
<!-- column: item:A.8.26:rev_date -->
<!-- column: item:A.8.26:rev_reviewer -->
<!-- column: item:A.8.26:rev_catalogue_currency -->
<!-- column: item:A.8.26:rev_traceability_sample -->
<!-- column: item:A.8.26:rev_exception_inventory -->
<!-- column: item:A.8.26:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.26:appsec_program_review -->
| Rev Date | Rev Reviewer | Rev Catalogue Currency | Rev Traceability Sample | Rev Exception Inventory | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.26:appsec_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.26:rev_date>>
_Why: 27002:8.26 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.8.26:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Engineering + InfoSec + Product)

### Rev Catalogue Currency

<<MUST item:A.8.26:rev_catalogue_currency>>
_Why: 27002:8.26 — information security requirements_

> _Standard text:_ Requirements-catalogue currency check (new threat patterns → requirement-category updates)

### Rev Traceability Sample

<<MUST item:A.8.26:rev_traceability_sample>>
_Why: 27002:8.26 — specified_

> _Standard text:_ Sample-based traceability verification (requirements → test cases mapping intact)

### Rev Exception Inventory

<<MUST item:A.8.26:rev_exception_inventory>>
_Why: Drift prevention_

> _Standard text:_ Exception inventory re-confirmed / retired

### Rev Findings Update

<<MUST item:A.8.26:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / scope

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.26:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
