---
leaf_id: req:Art.31:interaction_register
control_ref: Art.31
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# SA Interaction Register

> Per-interaction record of all SA engagements (inquiry / investigation / audit / consultation). Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row interaction id

<<MUST item:Art.31:reg_interaction_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row supervisory authority identifier (which MS + which SA)

<<MUST item:Art.31:reg_sa>>
_Why: Defining the relationship_

<<TEXT>>

## 3. Per-row topic (inquiry / complaint investigation / on-site audit / Art.36 consultation)

<<MUST item:Art.31:reg_topic>>
_Why: Art.31 + Art.36_

<<TEXT>>

## 4. Per-row received date

<<MUST item:Art.31:reg_received_date>>
_Why: Currency_

<<TEXT>>

## 5. Per-row response date or status (open / in-progress / closed)

<<MUST item:Art.31:reg_response_date>>
_Why: SLA tracking_

<<TEXT>>

## 6. Per-row outcome (no-action / corrective measures / fine / ongoing)

<<MUST item:Art.31:reg_outcome>>
_Why: Audit clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row lessons / actions feeding into 10.1 continual improvement

<<SHOULD item:Art.31:reg_lessons>>
_Why: Cross-clause_

<<TEXT>>
