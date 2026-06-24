---
leaf_id: req:Art.16:rectification_register
control_ref: Art.16
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Rectification Request Register

> Per-request record proving every Art.16 request was handled per procedure. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row request id (Art.12 cross-ref)

<<MUST item:Art.16:reg_request_id>>
_Why: Cross-leaf_

<<TEXT>>

## 2. Per-row subject identifier (pseudonymous)

<<MUST item:Art.16:reg_subject_id>>
_Why: Audit_

<<TEXT>>

## 3. Per-row systems where rectification was applied

<<MUST item:Art.16:reg_systems_touched>>
_Why: Art.16 — across all instances_

<<TEXT>>

## 4. Per-row response date (Art.12.3 SLA)

<<MUST item:Art.16:reg_response_date>>
_Why: Art.12.3_

<<TEXT>>

## 5. Per-row Art.19 notification reference

<<MUST item:Art.16:reg_art19_xref>>
_Why: Art.19_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row summary of correction made

<<SHOULD item:Art.16:reg_correction_summary>>
_Why: Audit clarity_

<<TEXT>>
