---
leaf_id: req:Art.17:erasure_register
control_ref: Art.17
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Erasure Request Register

> Per-request record proving Art.17 lifecycle (grounds → exception assessment → erasure → notification). Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row request id (Art.12 cross-ref)

<<MUST item:Art.17:reg_request_id>>
_Why: Cross-leaf_

<<TEXT>>

## 2. Per-row Art.17.1 ground (a-f) recorded

<<MUST item:Art.17:reg_grounds>>
_Why: Art.17.1_

<<TEXT>>

## 3. Per-row Art.17.3 exception assessment (none / cited exception)

<<MUST item:Art.17:reg_exceptions>>
_Why: Art.17.3_

<<TEXT>>

## 4. Per-row systems where erasure was applied (including backups + replicas)

<<MUST item:Art.17:reg_systems_erased>>
_Why: Art.17.1 — all instances_

<<TEXT>>

## 5. Per-row response date (Art.12.3 SLA)

<<MUST item:Art.17:reg_response_date>>
_Why: Art.12.3_

<<TEXT>>

## 6. Per-row Art.19 notification reference

<<MUST item:Art.17:reg_art19_xref>>
_Why: Art.19_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row Art.17.2 public-disclosure action where applicable

<<SHOULD item:Art.17:reg_art17_2_action>>
_Why: Art.17.2_

<<TEXT>>
