---
leaf_id: req:A.7.8:siting_register
control_ref: A.7.8
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Equipment Siting Register

> The catalogue of in-scope equipment with location, class, protection measures applied, owner

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row equipment identifier (cross-link to A.5.9 asset register)

<<MUST item:A.7.8:reg_equipment_id>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-row location (site + room per A.7.3 register)

<<MUST item:A.7.8:reg_location>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 3. Per-row equipment class (drives required protection level)

<<MUST item:A.7.8:reg_class>>
_Why: 27002:7.8 — proportional_

<<TEXT>>

## 4. Per-row protection measures in place (matches procedure's per-class requirements)

<<MUST item:A.7.8:reg_protection>>
_Why: 27002:7.8 — implemented_

<<TEXT>>

## 5. Per-row owner

<<MUST item:A.7.8:reg_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row remediation log where protection falls short of required

<<SHOULD item:A.7.8:reg_remediation>>
_Why: Operational discipline_

<<TEXT>>
