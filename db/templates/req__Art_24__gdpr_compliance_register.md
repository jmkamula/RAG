---
leaf_id: req:Art.24:gdpr_compliance_register
control_ref: Art.24
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# GDPR Compliance Register

> Per-obligation register tracking the org's posture against every GDPR article in scope. Annual refresh (freshness=365). Distinct from the Art.30 RoPA (activities) and the lawful-basis register (Art.6 per-activity): this is the meta-tracker of compliance posture per article

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row GDPR article identifier

<<MUST item:Art.24:reg_article_id>>
_Why: Coverage_

<<TEXT>>

## 2. Per-row applicability assessment (in scope / N/A with reason)

<<MUST item:Art.24:reg_applicability>>
_Why: Defensibility_

<<TEXT>>

## 3. Per-row link to the implementing artefact (procedure / policy / register / DPA / certification)

<<MUST item:Art.24:reg_implementing_artefact>>
_Why: Demonstrability_

<<TEXT>>

## 4. Per-row implementation status (implemented / partial / planned / N/A)

<<MUST item:Art.24:reg_status>>
_Why: Status visibility_

<<TEXT>>

## 5. Per-row owner

<<MUST item:Art.24:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 6. Per-row last-assessed date (drives staleness)

<<MUST item:Art.24:reg_last_assessed>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row residual risk where status is partial

<<SHOULD item:Art.24:reg_residual_risk>>
_Why: Risk visibility_

<<TEXT>>
