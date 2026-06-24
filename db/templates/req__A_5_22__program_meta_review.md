---
leaf_id: req:A.5.22:program_meta_review
control_ref: A.5.22
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
---

# Periodic Supplier Review Program Meta-Review

> The review program itself needs review — are we covering enough of the portfolio, is the cadence right, are findings being closed, is the program returning value? The meta-review evidences the periodic self-assessment of the program and the resulting adjustments

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Meta-review date within the planned interval

<<MUST item:A.5.22:pgm_date>>
_Why: 27002:5.22 — periodic_

<<TEXT>>

## 2. Reviewer identity (program owner + InfoSec lead jointly)

<<MUST item:A.5.22:pgm_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Coverage rate (fraction of supplier portfolio reviewed in period, by tier)

<<MUST item:A.5.22:pgm_coverage>>
_Why: Operational discipline_

<<TEXT>>

## 4. Findings-closure rate (open / aged / closed) across the portfolio

<<MUST item:A.5.22:pgm_closure>>
_Why: Operational discipline_

<<TEXT>>

## 5. Cadence-adjustment decisions or scope-adjustment decisions (tighten / loosen / re-tier)

<<MUST item:A.5.22:pgm_outcome>>
_Why: 27002:5.22a,j_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External benchmarking or industry-practice input considered

<<SHOULD item:A.5.22:pgm_benchmark>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned meta-review date stated

<<SHOULD item:A.5.22:pgm_next_date>>
_Why: Planning_

<<TEXT>>
