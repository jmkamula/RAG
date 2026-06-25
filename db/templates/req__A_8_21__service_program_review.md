---
leaf_id: req:A.8.21:service_program_review
control_ref: A.8.21
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Network Services Program Review

> Periodic verification — SLA attainment trending, security-mechanism currency, provider obligations re-confirmed (freshness=180; service delivery dynamic + supplier landscape evolves)

<!-- TABLE-COLUMNS leaf:req:A.8.21:service_program_review -->
<!-- column: item:A.8.21:rev_date -->
<!-- column: item:A.8.21:rev_reviewer -->
<!-- column: item:A.8.21:rev_sla_attainment -->
<!-- column: item:A.8.21:rev_mechanisms_currency -->
<!-- column: item:A.8.21:rev_a522_link -->
<!-- column: item:A.8.21:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.21:service_program_review -->
| Rev Date | Rev Reviewer | Rev Sla Attainment | Rev Mechanisms Currency | Rev A522 Link | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.21:service_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.21:rev_date>>
_Why: 27002:8.21 — periodic_

> _Standard text:_ Review date within the planned interval (≤180 days)

### Rev Reviewer

<<MUST item:A.8.21:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Network Engineering + Supplier Management)

### Rev Sla Attainment

<<MUST item:A.8.21:rev_sla_attainment>>
_Why: 27002:8.21 — monitored_

> _Standard text:_ SLA-attainment trending per service

### Rev Mechanisms Currency

<<MUST item:A.8.21:rev_mechanisms_currency>>
_Why: 27002:8.21 — security mechanisms_

> _Standard text:_ Security-mechanism currency check (TLS versions / crypto algorithms / authentication strength still acceptable)

### Rev A522 Link

<<MUST item:A.8.21:rev_a522_link>>
_Why: Cross-control coherence_

> _Standard text:_ Cross-link to A.5.22 supplier review outcomes for in-scope vendor services

### Rev Findings Update

<<MUST item:A.8.21:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / register / scope

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.21:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
