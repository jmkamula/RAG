---
leaf_id: req:9.2:audit_execution_record
control_ref: 9.2
standard_id: ISO27001:2022
evidence_type: audit_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Internal Audit Execution Record

> Per-audit record capturing what was audited, by whom, when, with what findings — the lifecycle-end artefact of each audit engagement. Distinct from the programme: the programme is the plan, the execution record is the proof. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique audit identifier per row

<<MUST item:9.2:rec_audit_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-audit scope (which ISMS process / area was audited)

<<MUST item:9.2:rec_scope>>
_Why: Clause 9.2a_

<<TEXT>>

## 3. Per-audit auditor identity + independence assertion

<<MUST item:9.2:rec_auditor>>
_Why: Clause 9.2c_

<<TEXT>>

## 4. Per-audit execution date

<<MUST item:9.2:rec_date>>
_Why: Currency_

<<TEXT>>

## 5. Per-audit findings list (conformities + nonconformities + observations)

<<MUST item:9.2:rec_findings>>
_Why: Clause 9.2d_

<<TEXT>>

## 6. Per-audit handoff to 10.2 NC/CA procedure where findings include nonconformities

<<MUST item:9.2:rec_handoff>>
_Why: Clause 9.2e_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-audit reference number cited in the next 9.3 management review

<<SHOULD item:9.2:rec_mgmt_review_link>>
_Why: Clause 9.3.2a_

<<TEXT>>
