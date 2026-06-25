---
leaf_id: req:A.8.19:installation_program_review
control_ref: A.8.19
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Installation Program Review

> Annual verification — approved-list currency, allowlist enforcement effectiveness, unauthorised-install detection trending (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.19:installation_program_review -->
<!-- column: item:A.8.19:rev_date -->
<!-- column: item:A.8.19:rev_reviewer -->
<!-- column: item:A.8.19:rev_approved_list_currency -->
<!-- column: item:A.8.19:rev_allowlist_effectiveness -->
<!-- column: item:A.8.19:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.19:installation_program_review -->
| Rev Date | Rev Reviewer | Rev Approved List Currency | Rev Allowlist Effectiveness | Rev Findings Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.19:installation_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.19:rev_date>>
_Why: 27002:8.19 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.8.19:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Infrastructure + InfoSec)

### Rev Approved List Currency

<<MUST item:A.8.19:rev_approved_list_currency>>
_Why: 27002:8.19 — securely manage_

> _Standard text:_ Approved-list currency check (no abandoned tools; vulnerable versions retired)

### Rev Allowlist Effectiveness

<<MUST item:A.8.19:rev_allowlist_effectiveness>>
_Why: Detection effectiveness_

> _Standard text:_ Allowlist-enforcement effectiveness review (unauthorised-install attempt rate)

### Rev Findings Update

<<MUST item:A.8.19:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / approved list

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.19:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
