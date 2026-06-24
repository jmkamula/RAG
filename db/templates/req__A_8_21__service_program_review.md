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
---

# Periodic Network Services Program Review

> Periodic verification — SLA attainment trending, security-mechanism currency, provider obligations re-confirmed (freshness=180; service delivery dynamic + supplier landscape evolves)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (≤180 days)

<<MUST item:A.8.21:rev_date>>
_Why: 27002:8.21 — periodic_

<<TEXT>>

## 2. Reviewer identity (Network Engineering + Supplier Management)

<<MUST item:A.8.21:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. SLA-attainment trending per service

<<MUST item:A.8.21:rev_sla_attainment>>
_Why: 27002:8.21 — monitored_

<<TEXT>>

## 4. Security-mechanism currency check (TLS versions / crypto algorithms / authentication strength still acceptable)

<<MUST item:A.8.21:rev_mechanisms_currency>>
_Why: 27002:8.21 — security mechanisms_

<<TEXT>>

## 5. Cross-link to A.5.22 supplier review outcomes for in-scope vendor services

<<MUST item:A.8.21:rev_a522_link>>
_Why: Cross-control coherence_

<<TEXT>>

## 6. Findings propagated to procedure / register / scope

<<MUST item:A.8.21:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.21:rev_next_date>>
_Why: Planning_

<<TEXT>>
