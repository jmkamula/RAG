---
leaf_id: req:A.7.5:threat_register
control_ref: A.7.5
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Per-Site Threat Register

> The catalogue of identified physical/environmental threats per site with protection measures, last assessment date, residual risk

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row site + threat pair (one row per applicable threat per site)

<<MUST item:A.7.5:reg_site_threat>>
_Why: 27002:7.5 — assessment_

<<TEXT>>

## 2. Per-row likelihood rating (informed by geography / historical events / climate projections)

<<MUST item:A.7.5:reg_likelihood>>
_Why: 27002:7.5 — assessment_

<<TEXT>>

## 3. Per-row impact rating (worst-case + most-likely scenarios)

<<MUST item:A.7.5:reg_impact>>
_Why: 27002:7.5 — assessment_

<<TEXT>>

## 4. Per-row protection measures actually deployed (matches procedure's per-threat list)

<<MUST item:A.7.5:reg_protection_in_place>>
_Why: 27002:7.5 — implemented_

<<TEXT>>

## 5. Per-row residual risk after controls (accepted / requires-treatment)

<<MUST item:A.7.5:reg_residual_risk>>
_Why: Risk discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row last actual event of this threat type (drives re-assessment cadence)

<<SHOULD item:A.7.5:reg_last_event>>
_Why: Empirical input_

<<TEXT>>
