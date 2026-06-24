---
leaf_id: req:Art.46:safeguards_register
control_ref: Art.46
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Safeguards Register

> Per-transfer record proving Art.46 safeguard is in place with TIA + supplementary measures where applicable. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row transfer id (Art.44 register cross-ref)

<<MUST item:Art.46:reg_transfer_id>>
_Why: Cross-leaf_

<<TEXT>>

## 2. Per-row safeguard type (Art.46.2 a-f / Art.46.3 a-b)

<<MUST item:Art.46:reg_safeguard>>
_Why: Art.46.2-3_

<<TEXT>>

## 3. Per-row SCC module where applicable (1: C2C / 2: C2P / 3: P2P / 4: P2C)

<<MUST item:Art.46:reg_sccs_module>>
_Why: Commission Decision 2021/914_

<<TEXT>>

## 4. Per-row TIA outcome (acceptable / acceptable-with-supplementary-measures / not-acceptable)

<<MUST item:Art.46:reg_tia_outcome>>
_Why: Schrems II_

<<TEXT>>

## 5. Per-row supplementary measures applied (where TIA required)

<<MUST item:Art.46:reg_supplementary_measures>>
_Why: EDPB 01/2020_

<<TEXT>>

## 6. Per-row safeguard signed / countersigned date

<<MUST item:Art.46:reg_signed_date>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row SA authorisation reference (Art.46.3)

<<SHOULD item:Art.46:reg_authorisation>>
_Why: Art.46.3_

<<TEXT>>
