---
leaf_id: req:A.7.3.9:program_review
control_ref: A.7.3.9
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Request Handling Program Review

<<DOC_CONTROL>>

> Annual verification — intake channels functional, SLAs met, delay notifications issued, complaint routes surfaced, fees defensible where charged (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.9:program_review -->
<!-- column: item:A.7.3.9:rev_date -->
<!-- column: item:A.7.3.9:rev_reviewer -->
<!-- column: item:A.7.3.9:rev_sla_audit -->
<!-- column: item:A.7.3.9:rev_channel_test -->
<!-- column: item:A.7.3.9:rev_complaint_route_test -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document and review how your organization handles incoming requests, ensuring your intake channels work, service levels are met, and complaint processes are clear and defensible.

## When to use it

Use this template if your organization needs to regularly check that request handling processes meet privacy standards, especially when your activities match certain criteria. Plan to complete this review about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes filling out this register from scratch, depending on the number of request types and the detail you provide for each required element.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.9:program_review -->
| Rev Date | Rev Reviewer | Rev Sla Audit | Rev Channel Test | Rev Complaint Route Test |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.9:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.9:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.3.9:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Privacy Ops lead)

<<GUIDANCE>>

### Rev Sla Audit

<<MUST item:A.7.3.9:rev_sla_audit>>
_Why: §7.3.9 — response times_

> _Standard text:_ SLA audit — aggregate + sampled requests measured against response-time matrix

<<GUIDANCE>>

### Rev Channel Test

<<MUST item:A.7.3.9:rev_channel_test>>
_Why: §7.3.9 — handling_

> _Standard text:_ Channel test — sampled inbound requests through each intake channel

<<GUIDANCE>>

### Rev Complaint Route Test

<<MUST item:A.7.3.9:rev_complaint_route_test>>
_Why: Art.13.2.d + Art.14.2.e_

> _Standard text:_ Complaint-route visibility test — subject notice surfaces the SA-complaint right

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.9:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
