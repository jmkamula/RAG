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
---

# Periodic Threat Intelligence Program Review

> The threat intelligence program creates value only if it closes the loop into defensive action — feeds get retired when stale, consumer feedback drives product changes, and analysis effort tracks the threats relevant to the org. The review captures the planned-interval check: feed-value analysis, products delivered, consumer feedback, missed-event analysis, and resulting program adjustments. Cadence tightened to 180 days — detection landscape volatility outpaces annual cycles

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned 180-day interval

<<MUST item:A.5.7:rev_date>>
_Why: 27002:5.7 — periodic_

<<TEXT>>

## 2. Reviewer identity (program owner + InfoSec lead jointly)

<<MUST item:A.5.7:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Feed-value analysis per source (which feeds delivered actionable IOCs / advisories; which were dropped)

<<MUST item:A.5.7:rev_feed_value>>
_Why: 27002:5.7 — sources curation_

<<TEXT>>

## 4. Products delivered count and distribution evidenced (proves the program ran, not just the procedure existed)

<<MUST item:A.5.7:rev_products_delivered>>
_Why: 27002:5.7 — produce threat intelligence_

<<TEXT>>

## 5. Consumer feedback collected from named consumers (sec ops, A.5.21 supplier risk, A.5.25 detection, exec briefing)

<<MUST item:A.5.7:rev_consumer_feedback>>
_Why: 27002:5.7 — communication effectiveness_

<<TEXT>>

## 6. Missed-event analysis (events surfaced by A.5.25 triage or A.5.27 lessons that intel didn't flag in advance)

<<MUST item:A.5.7:rev_missed>>
_Why: Closing the loop with [[A.5.25]] / [[A.5.27]]_

<<TEXT>>

## 7. Action items captured for the program (e.g. add new feed, retire stale source, tune analysis cadence)

<<MUST item:A.5.7:rev_actions>>
_Why: 27002:5.7 — program adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External threat-landscape snapshot considered (industry reports, vendor briefings)

<<SHOULD item:A.5.7:rev_landscape>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated (within 180d of this review)

<<SHOULD item:A.5.7:rev_next_date>>
_Why: Planning_

<<TEXT>>
