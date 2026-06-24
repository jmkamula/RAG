---
leaf_id: req:A.8.32:change_register
control_ref: A.8.32
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Change Register

> Per-change record — change id, target, risk tier, approval lineage, outcome, rollback-invoked flag. The continuous evidence stream

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-change unique identifier

<<MUST item:A.8.32:reg_change_id>>
_Why: Auditability_

<<TEXT>>

## 2. Per-change target (system / config / data; cross-link to A.5.9 asset register)

<<MUST item:A.8.32:reg_target>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-change risk tier (drives approval path applied)

<<MUST item:A.8.32:reg_risk_tier>>
_Why: 27002:8.32 — change management_

<<TEXT>>

## 4. Per-change approval lineage (approver(s) + timestamp)

<<MUST item:A.8.32:reg_approval_lineage>>
_Why: Accountability_

<<TEXT>>

## 5. Per-change outcome (success / partial / rolled-back / failed)

<<MUST item:A.8.32:reg_outcome>>
_Why: Continuous evidence_

<<TEXT>>

## 6. Per-change emergency flag + post-hoc-review reference where emergency

<<MUST item:A.8.32:reg_emergency_flag>>
_Why: Operational reality_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-change actor (person or automated job)

<<SHOULD item:A.8.32:reg_actor>>
_Why: Accountability_

<<TEXT>>
