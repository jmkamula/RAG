---
leaf_id: req:A.8.14:failover_test_register
control_ref: A.8.14
standard_id: ISO27001:2022
evidence_type: monitoring_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Failover Test Register

> Per-test record — drilled failover events, real failover events, outcomes. Proves the baseline + procedure work in practice

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-test unique identifier

<<MUST item:A.8.14:reg_test_id>>
_Why: Auditability_

<<TEXT>>

## 2. Per-test service tested

<<MUST item:A.8.14:reg_service>>
_Why: 27002:8.14 — sufficient to meet_

<<TEXT>>

## 3. Per-test type (planned drill / unplanned real / fault-injection)

<<MUST item:A.8.14:reg_type>>
_Why: Distinguishing operational vs test signal_

<<TEXT>>

## 4. Per-test date

<<MUST item:A.8.14:reg_date>>
_Why: Currency_

<<TEXT>>

## 5. Per-test outcome (success / partial / failure) + actual recovery time vs target

<<MUST item:A.8.14:reg_outcome>>
_Why: 27002:8.14 — sufficient_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-test findings + corrective actions where target missed

<<SHOULD item:A.8.14:reg_findings>>
_Why: Closes the loop_

<<TEXT>>
