---
leaf_id: req:A.5.36:compliance_program_meta_review
control_ref: A.5.36
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
---

# Periodic Compliance Review Program Meta-Review

> The compliance review program itself needs review — is the catalogue current, is the method choice right, are findings being closed, are continuous-compliance signals being used effectively? The meta-review evidences periodic self-assessment and the resulting adjustments

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Meta-review date within the planned interval

<<MUST item:A.5.36:pgm_date>>
_Why: 27002:5.36 — periodic_

<<TEXT>>

## 2. Reviewer identity (compliance program owner + InfoSec lead jointly)

<<MUST item:A.5.36:pgm_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Catalogue currency check — did new policies / rules / standards land without entering the schedule? are retired items still scheduled?

<<MUST item:A.5.36:pgm_catalogue_check>>
_Why: 27002:5.36 — InfoSec policy + topic-specific policies + rules + standards_

<<TEXT>>

## 4. Coverage check — did the schedule actually run? what fraction of catalogue reviewed in period?

<<MUST item:A.5.36:pgm_coverage>>
_Why: 27002:5.36 — regularly_

<<TEXT>>

## 5. Findings-closure rate across the program (open / aged / closed)

<<MUST item:A.5.36:pgm_closure>>
_Why: Operational discipline_

<<TEXT>>

## 6. Method effectiveness review — are the chosen methods surfacing real nonconformities, or is the program rubber-stamping?

<<MUST item:A.5.36:pgm_method_review>>
_Why: 27002:5.36 — adjustments_

<<TEXT>>

## 7. Cadence-adjustment or method-adjustment decisions (tighten / loosen / change method per item type)

<<MUST item:A.5.36:pgm_outcome>>
_Why: 27002:5.36 — adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Alignment check with A.5.35 independent review program (shared reviewer pool? shared finding register? leverage opportunities)

<<SHOULD item:A.5.36:pgm_a535_alignment>>
_Why: Cross-control coherence_

<<TEXT>>

### 2. Next planned meta-review date stated

<<SHOULD item:A.5.36:pgm_next_date>>
_Why: Planning_

<<TEXT>>
