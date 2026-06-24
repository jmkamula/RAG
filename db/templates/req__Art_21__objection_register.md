---
leaf_id: req:Art.21:objection_register
control_ref: Art.21
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Objection Register

> Per-objection record. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row request id (Art.12 cross-ref)

<<MUST item:Art.21:reg_request_id>>
_Why: Cross-leaf_

<<TEXT>>

## 2. Per-row objection type (direct marketing absolute / legitimate interests balancing / scientific research)

<<MUST item:Art.21:reg_objection_type>>
_Why: Art.21.1-6_

<<TEXT>>

## 3. Per-row outcome (processing ceased / continued with compelling grounds / partial)

<<MUST item:Art.21:reg_outcome>>
_Why: Art.21.1_

<<TEXT>>

## 4. Per-row grounds for continuing (for legitimate-interests objections continued)

<<MUST item:Art.21:reg_grounds>>
_Why: Art.21.1 — defensibility_

<<TEXT>>

## 5. Per-row response date (Art.12.3 SLA tracking)

<<MUST item:Art.21:reg_response_date>>
_Why: Art.12.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row addition to suppression list (direct marketing)

<<SHOULD item:Art.21:reg_suppression_list>>
_Why: Art.21.3 operational_

<<TEXT>>
