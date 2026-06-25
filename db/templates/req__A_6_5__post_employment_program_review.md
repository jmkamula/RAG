---
leaf_id: req:A.6.5:post_employment_program_review
control_ref: A.6.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Periodic Post-Employment Program Review

> Periodic verification that every leaver in the period was briefed, that the obligation scope still matches current law, and that any breach incidents have been handled per the enforcement approach. Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.6.5:post_employment_program_review -->
<!-- column: item:A.6.5:rev_date -->
<!-- column: item:A.6.5:rev_reviewer -->
<!-- column: item:A.6.5:rev_briefing_coverage -->
<!-- column: item:A.6.5:rev_legal_drift -->
<!-- column: item:A.6.5:rev_breach_history -->
<!-- column: item:A.6.5:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.5:post_employment_program_review -->
| Rev Date | Rev Reviewer | Rev Briefing Coverage | Rev Legal Drift | Rev Breach History | Rev Register Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.5:post_employment_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.6.5:rev_date>>
_Why: 27002:6.5 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.6.5:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (HR lead + InfoSec lead + Legal counsel)

### Rev Briefing Coverage

<<MUST item:A.6.5:rev_briefing_coverage>>
_Why: 27002:6.5 — completeness_

> _Standard text:_ Briefing coverage check — every leaver in the period received and acknowledged a briefing (the register's completeness gate)

### Rev Legal Drift

<<MUST item:A.6.5:rev_legal_drift>>
_Why: 27002:6.5 — applicable laws_

> _Standard text:_ Employment-law drift check per jurisdiction (legal counsel input on enforceability changes)

### Rev Breach History

<<MUST item:A.6.5:rev_breach_history>>
_Why: 27002:6.5 — enforced_

> _Standard text:_ Breach history review — any post-employment breaches occurred? handled per enforcement approach? lessons captured?

### Rev Register Update

<<MUST item:A.6.5:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the procedure / scope with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.6.5:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers (high-profile leaver, regulator action affecting post-employment terms, employment-tribunal ruling)

### Rev Next Date

<<SHOULD item:A.6.5:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
