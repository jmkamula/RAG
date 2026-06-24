---
leaf_id: req:A.8.33:test_dataset_register
control_ref: A.8.33
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Test Dataset Register

> Per-dataset catalogue — dataset id, source, current treatment (synthetic / masked / live-PII-banned), location, last-refresh, retention status

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row dataset identifier

<<MUST item:A.8.33:reg_dataset_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-row source (synthetic-generator / production-snapshot / vendor-provided / contributed-by-user)

<<MUST item:A.8.33:reg_source>>
_Why: 27002:8.33 — selected_

<<TEXT>>

## 3. Per-row treatment applied (synthetic / static-masked / dynamic-masked / pseudonymised)

<<MUST item:A.8.33:reg_treatment>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Per-row storage location + access-control reference

<<MUST item:A.8.33:reg_location>>
_Why: 27002:8.33 — managed_

<<TEXT>>

## 5. Per-row last refresh timestamp (drives stale-test-data detection)

<<MUST item:A.8.33:reg_last_refresh>>
_Why: Drift detection_

<<TEXT>>

## 6. Per-row retention status (active / scheduled-for-deletion / archived)

<<MUST item:A.8.33:reg_retention_status>>
_Why: 27002:8.33 — managed_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row named owner

<<SHOULD item:A.8.33:reg_owner>>
_Why: Accountability_

<<TEXT>>
