---
leaf_id: req:B.8.4.1:temp_files_procedure
control_ref: B.8.4.1
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Processor Temp Files Disposal Procedure

> §8.4.1 mirrors §7.4.6 from processor side — temp files created during processing of customer PII must be disposed of within a specified, documented period.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Temp file taxonomy (customer-facing multi-tenant apps + shared infrastructure + integration middleware)

<<MUST item:B.8.4.1:proc_temp_taxonomy>>
_Why: §8.4.1_

<<TEXT>>

## 2. Disposal period stated per taxonomy category

<<MUST item:B.8.4.1:proc_period>>
_Why: §8.4.1 — specified, documented period_

<<TEXT>>

## 3. Garbage collection procedure identifying unused files + last-use timestamp

<<MUST item:B.8.4.1:proc_gc_procedure>>
_Why: §8.4.1 — garbage collection_

<<TEXT>>

## 4. Tenant isolation of temp files — no cross-tenant leakage in shared infrastructure

<<MUST item:B.8.4.1:proc_tenant_isolation>>
_Why: Multi-tenant discipline_

<<TEXT>>

## 5. Periodic check that temp files are deleted

<<MUST item:B.8.4.1:proc_periodic_check>>
_Why: §8.4.1 — periodic verification_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Platform Ops)

<<SHOULD item:B.8.4.1:proc_owner>>
_Why: Accountability_

<<TEXT>>
