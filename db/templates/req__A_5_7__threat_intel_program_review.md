---
leaf_id: req:A.5.7:threat_intel_program_review
control_ref: A.5.7
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic Threat Intelligence Program Review

> The threat intelligence program creates value only if it closes the loop into defensive action — feeds get retired when stale, consumer feedback drives product changes, and analysis effort tracks the threats relevant to the org. The review captures the planned-interval check: feed-value analysis, products delivered, consumer feedback, missed-event analysis, and resulting program adjustments. Cadence tightened to 180 days — detection landscape volatility outpaces annual cycles

<!-- TABLE-COLUMNS leaf:req:A.5.7:threat_intel_program_review -->
<!-- column: item:A.5.7:rev_date -->
<!-- column: item:A.5.7:rev_reviewer -->
<!-- column: item:A.5.7:rev_feed_value -->
<!-- column: item:A.5.7:rev_products_delivered -->
<!-- column: item:A.5.7:rev_consumer_feedback -->
<!-- column: item:A.5.7:rev_missed -->
<!-- column: item:A.5.7:rev_actions -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.7:threat_intel_program_review -->
| Rev Date | Rev Reviewer | Rev Feed Value | Rev Products Delivered | Rev Consumer Feedback | Rev Missed | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.7:threat_intel_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.7:rev_date>>
_Why: 27002:5.7 — periodic_

> _Standard text:_ Review date within the planned 180-day interval

### Rev Reviewer

<<MUST item:A.5.7:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (program owner + InfoSec lead jointly)

### Rev Feed Value

<<MUST item:A.5.7:rev_feed_value>>
_Why: 27002:5.7 — sources curation_

> _Standard text:_ Feed-value analysis per source (which feeds delivered actionable IOCs / advisories; which were dropped)

### Rev Products Delivered

<<MUST item:A.5.7:rev_products_delivered>>
_Why: 27002:5.7 — produce threat intelligence_

> _Standard text:_ Products delivered count and distribution evidenced (proves the program ran, not just the procedure existed)

### Rev Consumer Feedback

<<MUST item:A.5.7:rev_consumer_feedback>>
_Why: 27002:5.7 — communication effectiveness_

> _Standard text:_ Consumer feedback collected from named consumers (sec ops, A.5.21 supplier risk, A.5.25 detection, exec briefing)

### Rev Missed

<<MUST item:A.5.7:rev_missed>>
_Why: Closing the loop with [[A.5.25]] / [[A.5.27]]_

> _Standard text:_ Missed-event analysis (events surfaced by A.5.25 triage or A.5.27 lessons that intel didn't flag in advance)

### Rev Actions

<<MUST item:A.5.7:rev_actions>>
_Why: 27002:5.7 — program adjustments_

> _Standard text:_ Action items captured for the program (e.g. add new feed, retire stale source, tune analysis cadence)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Landscape

<<SHOULD item:A.5.7:rev_landscape>>
_Why: Audit defensibility_

> _Standard text:_ External threat-landscape snapshot considered (industry reports, vendor briefings)

### Rev Next Date

<<SHOULD item:A.5.7:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated (within 180d of this review)
