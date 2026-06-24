---
leaf_id: req:A.5.19:portfolio_review
control_ref: A.5.19
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 2
---

# Periodic Supplier Portfolio Review

> A.5.19 expects periodic review of the supplier portfolio — to refresh risk classifications, re-test selection criteria, and confirm that monitoring and training arrangements still fit the supplier mix

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.19:rev_date>>
_Why: 27002:5.19e — periodic_

<<TEXT>>

## 2. Reviewer identity and role (typically procurement + InfoSec lead)

<<MUST item:A.5.19:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Outcome per supplier or per tier (no change / re-tiered / added / removed)

<<MUST item:A.5.19:rev_outcome>>
_Why: 27002:5.19e_

<<TEXT>>

## 4. Action items captured where monitoring or training arrangements need adjustment

<<MUST item:A.5.19:rev_actions>>
_Why: 27002:5.19i,k_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc triggers (M&A, market events, new business line, supplier incident) prompting unscheduled review

<<SHOULD item:A.5.19:rev_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.19:rev_next_date>>
_Why: Planning_

<<TEXT>>
