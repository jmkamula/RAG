---
leaf_id: req:A.8.30:outsourced_program_review
control_ref: A.8.30
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Outsourced Development Program Review

> Annual verification — engagement-register currency, delivered-code-test coverage, vendor incident patterns (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.30:outsourced_program_review -->
<!-- column: item:A.8.30:rev_date -->
<!-- column: item:A.8.30:rev_reviewer -->
<!-- column: item:A.8.30:rev_register_currency -->
<!-- column: item:A.8.30:rev_test_coverage -->
<!-- column: item:A.8.30:rev_vendor_incidents -->
<!-- column: item:A.8.30:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.30:outsourced_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Test Coverage | Rev Vendor Incidents | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.30:outsourced_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.30:rev_date>>
_Why: 27002:8.30 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.8.30:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Engineering + Supplier Management + InfoSec)

### Rev Register Currency

<<MUST item:A.8.30:rev_register_currency>>
_Why: Drift prevention_

> _Standard text:_ Engagement-register currency check

### Rev Test Coverage

<<MUST item:A.8.30:rev_test_coverage>>
_Why: 27002:8.30 — review_

> _Standard text:_ Delivered-code-test coverage per engagement (was every release tested before merge to production)

### Rev Vendor Incidents

<<MUST item:A.8.30:rev_vendor_incidents>>
_Why: Cross-control coherence_

> _Standard text:_ Vendor incident-pattern review (cross-link to A.5.22 supplier review)

### Rev Findings Update

<<MUST item:A.8.30:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / contract terms

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.30:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
