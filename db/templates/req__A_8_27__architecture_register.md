---
leaf_id: req:A.8.27:architecture_register
control_ref: A.8.27
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Reference Architecture Register

> Per-pattern catalogue — pattern id, applicable context, security principles embedded, last-review date

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-pattern unique identifier

<<MUST item:A.8.27:reg_pattern_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-pattern applicable context (when to use this pattern)

<<MUST item:A.8.27:reg_context>>
_Why: 27002:8.27 — applied_

<<TEXT>>

## 3. Per-pattern principles embedded (mapping back to policy's principle set)

<<MUST item:A.8.27:reg_principles_embedded>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Per-pattern named owner

<<MUST item:A.8.27:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 5. Per-pattern last-review date

<<MUST item:A.8.27:reg_last_reviewed>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-pattern usage-count (how many projects adopted it — drives 'is this pattern actually used' signal)

<<SHOULD item:A.8.27:reg_usage_count>>
_Why: Operational visibility_

<<TEXT>>
