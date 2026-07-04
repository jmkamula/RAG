---
leaf_id: req:A.7.4.4:applicable_scope
control_ref: A.7.4.4
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Minimization Contexts Scope

> The upstream — which processing activities are candidates for minimisation (analytics + reporting + ML training + testing / dev environments) vs those needing full PII (operational transactions with the subject).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Minimisation candidates enumerated (analytics + reporting + ML + test environments + logs)

<<MUST item:A.7.4.4:scope_candidates>>
_Why: Coverage_

<<TEXT>>

## 2. Full-PII contexts (operational transactions + notifications + support) with justification

<<MUST item:A.7.4.4:scope_full_pii_needed>>
_Why: §7.4.4 — non-de-identified processing_

<<TEXT>>

## 3. Re-identification risk considerations per context (combinations of attributes / auxiliary data / linkage)

<<MUST item:A.7.4.4:scope_reidentification_risk>>
_Why: Effectiveness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new analytics use / new ML model)

<<SHOULD item:A.7.4.4:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
