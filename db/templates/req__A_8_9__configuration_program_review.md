---
leaf_id: req:A.8.9:configuration_program_review
control_ref: A.8.9
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Configuration Program Review

> Annual review — baseline currency vs vendor/threat updates, deviation inventory, drift-detection effectiveness (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.9:rev_date>>
_Why: 27002:8.9 — reviewed_

<<TEXT>>

## 2. Reviewer identity (Infrastructure leads + InfoSec)

<<MUST item:A.8.9:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Baseline-vs-vendor-current check (CIS / vendor / NIST version drift)

<<MUST item:A.8.9:rev_baseline_currency>>
_Why: 27002:8.9 — reviewed_

<<TEXT>>

## 4. Deviation inventory re-confirmed / retired

<<MUST item:A.8.9:rev_deviation_inventory>>
_Why: Drift prevention_

<<TEXT>>

## 5. Drift-detection effectiveness review (catch rate, MTTR)

<<MUST item:A.8.9:rev_drift_effectiveness>>
_Why: Detection effectiveness_

<<TEXT>>

## 6. Updated baselines published from findings

<<MUST item:A.8.9:rev_baselines_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.9:rev_next_date>>
_Why: Planning_

<<TEXT>>
