---
leaf_id: req:A.7.14:disposal_record
control_ref: A.7.14
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 1
---

# Per-Equipment Disposal Record

> Lifecycle-end variant — one record per piece of equipment disposed of. Proves the chain-of-custody from collection through to destruction-or-handover. Parallel to A.5.28 evidence-disposal pattern

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-record equipment identifier (cross-link to A.5.9 asset register, retired entry)

<<MUST item:A.7.14:disp_equipment_id>>
_Why: 27002:7.14 — traceability_

<<TEXT>>

## 2. Per-record disposal trigger

<<MUST item:A.7.14:disp_trigger>>
_Why: 27002:7.14 — disposal_

<<TEXT>>

## 3. Per-record method actually used (overwrite tool + verification, degauss, physical destruction with witness)

<<MUST item:A.7.14:disp_method>>
_Why: 27002:7.14 — secure removal_

<<TEXT>>

## 4. Per-record authoriser

<<MUST item:A.7.14:disp_authoriser>>
_Why: Accountability_

<<TEXT>>

## 5. Per-record destination (which approved provider OR internal-witness destruction)

<<MUST item:A.7.14:disp_destination>>
_Why: 27002:7.14 — securely_

<<TEXT>>

## 6. Per-record certificate of destruction (where externally destroyed) or witness signature (where internally destroyed)

<<MUST item:A.7.14:disp_certificate>>
_Why: Auditability_

<<TEXT>>

## 7. Per-record software-removal step evidence (license-key handoff or wipe)

<<MUST item:A.7.14:disp_software_step>>
_Why: 27002:7.14 — licensed software_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-record re-use status where the equipment goes to internal re-use (new owner + re-provisioned configuration link)

<<SHOULD item:A.7.14:disp_re_use_status>>
_Why: Re-use case_

<<TEXT>>
