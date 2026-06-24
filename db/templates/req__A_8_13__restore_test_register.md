---
leaf_id: req:A.8.13:restore_test_register
control_ref: A.8.13
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Restore Test Register

> Per-restore-test lifecycle-end record — what was restored, when, integrity-verified, target met. Parallels A.5.30 ICT readiness recovery-test pattern

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-test unique identifier

<<MUST item:A.8.13:reg_test_id>>
_Why: Auditability_

<<TEXT>>

## 2. Per-test backup target tested (system / dataset / configuration)

<<MUST item:A.8.13:reg_target>>
_Why: 27002:8.13 — regularly tested_

<<TEXT>>

## 3. Per-test date

<<MUST item:A.8.13:reg_date>>
_Why: Currency_

<<TEXT>>

## 4. Per-test outcome (success / partial / failure)

<<MUST item:A.8.13:reg_outcome>>
_Why: 27002:8.13 — tested_

<<TEXT>>

## 5. Per-test integrity-verification artefact (checksum / hash / functional test of restored data)

<<MUST item:A.8.13:reg_integrity_check>>
_Why: Defensibility_

<<TEXT>>

## 6. Per-test RPO-met flag (data-recoverable-to-RPO confirmed; auditor-critical proof parallels A.5.30 rec_success_status)

<<MUST item:A.8.13:reg_rpo_met>>
_Why: 27002:8.13 — sufficient_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-test findings + corrective actions where target missed

<<SHOULD item:A.8.13:reg_findings>>
_Why: Closes the loop_

<<TEXT>>
