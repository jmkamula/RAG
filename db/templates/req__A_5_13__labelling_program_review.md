---
leaf_id: req:A.5.13:labelling_program_review
control_ref: A.5.13
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
---

# Periodic Labelling Program Review

> The labelling program creates value only if labels actually stick across the estate — systems where coverage drops, transformations that strip labels, training gaps where users mis-apply, and new platforms that came online without labelling enabled all signal the program is leaking. The review captures the planned-interval check: coverage-trend analysis, drop-detection, scheme-alignment audit, training-effectiveness sample, and resulting program adjustments. Annual cadence — cascades from A.5.12 classification scheme review

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned annual interval

<<MUST item:A.5.13:rev_date>>
_Why: 27002:5.13 — periodic_

<<TEXT>>

## 2. Reviewer identity (InfoSec + Data Protection Officer where PII overlays apply jointly)

<<MUST item:A.5.13:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Coverage-trend analysis (per-system coverage % delta since last review; investigate any drop)

<<MUST item:A.5.13:rev_coverage_trend>>
_Why: Program effectiveness_

<<TEXT>>

## 4. Persistence audit (sample of transformed/exported items re-checked — does the label survive copy/export/conversion?)

<<MUST item:A.5.13:rev_persistence_audit>>
_Why: 27002:5.13 — persistence_

<<TEXT>>

## 5. Scheme-alignment audit (labels in active systems match A.5.12 levels; drift triggers re-mapping)

<<MUST item:A.5.13:rev_scheme_alignment>>
_Why: 27002:5.13 + cross-link to [[A.5.12]]_

<<TEXT>>

## 6. Training-effectiveness sample (small sample of newly created items per level — labelled correctly?)

<<MUST item:A.5.13:rev_training_sample>>
_Why: 27002:5.13 — implemented_

<<TEXT>>

## 7. Action items captured (e.g. extend labelling to platform X, tighten automation, refresh training module, address drop)

<<MUST item:A.5.13:rev_actions>>
_Why: 27002:5.13 — program adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Tooling-landscape check (vendor releases, new sensitivity-label features, capability gaps the program should consider)

<<SHOULD item:A.5.13:rev_tooling_landscape>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.13:rev_next_date>>
_Why: Planning_

<<TEXT>>
