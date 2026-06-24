---
leaf_id: req:8.1:operational_execution_register
control_ref: 8.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Operational Execution Register

> Per-execution record of operational processes — proof that planned processes were actually carried out. Distinct from the 6.1.1 action register (which tracks ISMS-level planning actions): this tracks per-process execution evidence. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Process identifier per row (matches procedure's process catalog)

<<MUST item:8.1:reg_process_id>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 2. Execution / iteration date per row

<<MUST item:8.1:reg_execution_date>>
_Why: Currency_

<<TEXT>>

## 3. Process owner per row

<<MUST item:8.1:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 4. Criteria-met indicator per row (process ran per the established criteria)

<<MUST item:8.1:reg_criteria_met>>
_Why: Clause 8.1 — implementing control_

<<TEXT>>

## 5. Per-row link to documented evidence retained

<<MUST item:8.1:reg_evidence_link>>
_Why: Clause 8.1 — documented information_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row flag where the process is outsourced (cross-link to A.5.19/A.5.20 supplier evidence)

<<SHOULD item:8.1:reg_outsourced_flag>>
_Why: Cross-control coherence_

<<TEXT>>
