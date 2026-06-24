---
leaf_id: req:9.1:measurement_record
control_ref: 9.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 90
template_version: 1
must_count: 6
should_count: 1
---

# ISMS Measurement Record

> The live measurement output — per-metric values captured over time, analysed against thresholds, fed into 9.3 management review. Distinct from the procedure: the procedure is the plan, this is the data. Quarterly refresh (freshness=90 — measurement tempo)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Metric identifier per row (matches procedure's metric catalog)

<<MUST item:9.1:rec_metric_id>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 2. Per-row measured value

<<MUST item:9.1:rec_value>>
_Why: Clause 9.1 — measurement_

<<TEXT>>

## 3. Per-row measurement date

<<MUST item:9.1:rec_date>>
_Why: Currency_

<<TEXT>>

## 4. Per-row threshold / target value applied

<<MUST item:9.1:rec_threshold>>
_Why: Clause 9.1 — evaluation_

<<TEXT>>

## 5. Per-row status (above-target / on-target / below-target / breach)

<<MUST item:9.1:rec_status>>
_Why: Clause 9.1 — analysis_

<<TEXT>>

## 6. Per-row metric owner

<<MUST item:9.1:rec_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row trend annotation (rising / stable / falling)

<<SHOULD item:9.1:rec_trend>>
_Why: Trend visibility_

<<TEXT>>
