---
leaf_id: req:A.8.16:monitoring_program_review
control_ref: A.8.16
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 1
table_shape: true
---

# Periodic Monitoring Program Review

<<DOC_CONTROL>>

> Periodic verification — detection coverage gaps, true-positive rate trending, missed-detection postmortems, threat-intel feeding (freshness=180; threat landscape volatile)

<!-- TABLE-COLUMNS leaf:req:A.8.16:monitoring_program_review -->
<!-- column: item:A.8.16:rev_date -->
<!-- column: item:A.8.16:rev_reviewer -->
<!-- column: item:A.8.16:rev_coverage -->
<!-- column: item:A.8.16:rev_tp_trending -->
<!-- column: item:A.8.16:rev_missed_postmortems -->
<!-- column: item:A.8.16:rev_threat_intel_feed -->
<!-- column: item:A.8.16:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you regularly review and document the effectiveness of your monitoring program, including detection coverage, accuracy trends, and how well threat intelligence is integrated. It's useful for identifying gaps and improving your security posture.

## When to use it

Use this template whenever you need to review your monitoring program, which should happen about every six months. It's designed for ongoing environments where regular checks are important.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 70 to 105 minutes completing this from scratch, depending on the amount of detail and the number of items you need to review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.16:monitoring_program_review -->
| Rev Date | Rev Reviewer | Rev Coverage | Rev Tp Trending | Rev Missed Postmortems | Rev Threat Intel Feed | Rev Register Update |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.16:monitoring_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.16:rev_date>>
_Why: 27002:8.16 — periodic_

> _Standard text:_ Review date within the planned interval (≤180 days)

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.16:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Security Operations lead + InfoSec lead)

<<GUIDANCE>>

### Rev Coverage

<<MUST item:A.8.16:rev_coverage>>
_Why: 27002:8.16 — coverage_

> _Standard text:_ Coverage check against threat-mapping (any uncovered MITRE technique surfaced)

<<GUIDANCE>>

### Rev Tp Trending

<<MUST item:A.8.16:rev_tp_trending>>
_Why: Detection effectiveness_

> _Standard text:_ True-positive rate trending review per detection

<<GUIDANCE>>

### Rev Missed Postmortems

<<MUST item:A.8.16:rev_missed_postmortems>>
_Why: Detection improvement_

> _Standard text:_ Missed-detection postmortems reviewed (incidents that bypassed monitoring)

<<GUIDANCE>>

### Rev Threat Intel Feed

<<MUST item:A.8.16:rev_threat_intel_feed>>
_Why: Currency_

> _Standard text:_ Threat-intel feeding effectiveness (cross-link to A.5.7 — new tactics translated to detections)

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.8.16:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to register / procedure / scope

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.16:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
