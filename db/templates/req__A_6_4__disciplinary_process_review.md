---
leaf_id: req:A.6.4:disciplinary_process_review
control_ref: A.6.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Periodic Disciplinary Process Review

> Periodic verification that the process still aligns with current employment law per jurisdiction, that case outcomes show consistent application (not discriminatory), and that lessons from cases feed back to relevant controls. Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.6.4:disciplinary_process_review -->
<!-- column: item:A.6.4:rev_date -->
<!-- column: item:A.6.4:rev_reviewer -->
<!-- column: item:A.6.4:rev_consistency -->
<!-- column: item:A.6.4:rev_legal_drift -->
<!-- column: item:A.6.4:rev_lessons_propagated -->
<!-- column: item:A.6.4:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.4:disciplinary_process_review -->
| Rev Date | Rev Reviewer | Rev Consistency | Rev Legal Drift | Rev Lessons Propagated | Rev Register Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.4:disciplinary_process_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.6.4:rev_date>>
_Why: 27002:6.4 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.6.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (HR lead + InfoSec lead + Legal counsel)

### Rev Consistency

<<MUST item:A.6.4:rev_consistency>>
_Why: Procedural fairness_

> _Standard text:_ Consistency analysis — case outcomes reviewed for consistent application across cases / demographics (avoids discriminatory enforcement patterns)

### Rev Legal Drift

<<MUST item:A.6.4:rev_legal_drift>>
_Why: 27002:6.4 — applicable laws_

> _Standard text:_ Employment-law drift check per jurisdiction (legal counsel input)

### Rev Lessons Propagated

<<MUST item:A.6.4:rev_lessons_propagated>>
_Why: Continual improvement_

> _Standard text:_ Lessons-propagation check — did case-driven lessons feed back to awareness curriculum (A.6.3), control updates, or policy amendments?

### Rev Register Update

<<MUST item:A.6.4:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the procedure with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.6.4:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers (employment tribunal ruling affecting the process, regulator enforcement action, major incident with personnel involvement)

### Rev Next Date

<<SHOULD item:A.6.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
