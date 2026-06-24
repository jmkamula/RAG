---
leaf_id: req:Art.48:applicable_scope
control_ref: Art.48
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Foreign Authority Scope

> The upstream — which third-country authorities might request disclosure, which international agreements (MLATs, GDPR-adequacy) are applicable

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Foreign authority types in scope (law enforcement / national security / tax / regulatory)

<<MUST item:Art.48:scope_authority_types>>
_Why: Art.48_

<<TEXT>>

## 2. International agreements catalogued (US-EU MLAT, sector-specific agreements)

<<MUST item:Art.48:scope_agreements>>
_Why: Art.48 — based on agreement_

<<TEXT>>

## 3. Excluded request types (subpoenas without agreement basis — refused absent Art.49 derogation)

<<MUST item:Art.48:scope_excluded>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new MLAT entered into force, new jurisdiction)

<<SHOULD item:Art.48:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
