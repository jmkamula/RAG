---
leaf_id: req:A.8.11:masking_register
control_ref: A.8.11
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Per-Dataset Masking Register

> Per-dataset application of masking — which production datasets feed which non-production environments via what technique, when last refreshed

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row source dataset identifier (from A.5.9 + A.5.34 PII inventory)

<<MUST item:A.8.11:reg_dataset>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-row target non-production environment

<<MUST item:A.8.11:reg_target_env>>
_Why: Identification_

<<TEXT>>

## 3. Per-row masking technique applied (from procedure's approved-techniques list)

<<MUST item:A.8.11:reg_technique>>
_Why: 27002:8.11 — applicable techniques_

<<TEXT>>

## 4. Per-row PII classes present (drives technique selection — strong pseudonymisation for special-category PII)

<<MUST item:A.8.11:reg_pii_classes>>
_Why: GDPR Art.32 alignment_

<<TEXT>>

## 5. Per-row last refresh timestamp (drives stale-mask detection)

<<MUST item:A.8.11:reg_last_refreshed>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row verification-sample link (re-identification residual-risk sample retained)

<<SHOULD item:A.8.11:reg_verification_sample>>
_Why: Audit defensibility_

<<TEXT>>
