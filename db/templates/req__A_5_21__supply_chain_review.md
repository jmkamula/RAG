---
leaf_id: req:A.5.21:supply_chain_review
control_ref: A.5.21
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 5
should_count: 2
---

# Periodic ICT Supply Chain Review

> ICT supply chains are volatile — vendor M&A, EOL pipelines, new vulnerability disclosures and sub-supplier shifts can move risk significantly inside a year. The review record captures the planned-interval review of the component register, the vendor-maturity assessment, the EOL pipeline and the resulting action items

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.21:rev_date>>
_Why: 27002:5.21 — periodic_

<<TEXT>>

## 2. Reviewer identity (typically architecture lead + InfoSec lead)

<<MUST item:A.5.21:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. EOL pipeline review (which components reach EOL in the next planning horizon, replacement status)

<<MUST item:A.5.21:rev_eol_pipeline>>
_Why: 27002:5.21i_

<<TEXT>>

## 4. Vendor maturity review (recent attestations, incidents, sub-supplier disclosures)

<<MUST item:A.5.21:rev_maturity>>
_Why: 27002:5.21d_

<<TEXT>>

## 5. Action items captured per critical component (e.g. tighten monitoring, push for upgrade, replan replacement)

<<MUST item:A.5.21:rev_actions>>
_Why: 27002:5.21d,i_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External threat intelligence input considered (link to A.5.7)

<<SHOULD item:A.5.21:rev_threat_intel>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.21:rev_next_date>>
_Why: Planning_

<<TEXT>>
