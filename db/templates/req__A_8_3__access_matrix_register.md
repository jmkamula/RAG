---
leaf_id: req:A.8.3:access_matrix_register
control_ref: A.8.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Per-System Access Matrix Register

> Catalogue of access matrices across systems — who can do what, per repository / dataset / application. Drives the recertification workflow

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Access matrix per system / repository row (who, what permissions, on what resource)

<<MUST item:A.8.3:per_system_matrix>>
_Why: 27002:8.3 — restricted_

<<TEXT>>

## 2. Per-row system identifier (from asset register A.5.9)

<<MUST item:A.8.3:reg_system_id>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-row matrix owner (system owner accountable for accuracy)

<<MUST item:A.8.3:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 4. Per-row last recertification date (drives staleness detection)

<<MUST item:A.8.3:reg_last_recert>>
_Why: Drift detection_

<<TEXT>>

## 5. Per-row classification tier (drives enforcement strictness)

<<MUST item:A.8.3:reg_classification>>
_Why: Cross-leaf coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exception log for temporary elevated access per row

<<SHOULD item:A.8.3:reg_exception_log>>
_Why: Operational discipline_

<<TEXT>>
