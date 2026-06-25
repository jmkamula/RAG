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
table_shape: true
---

# Internal Audit Execution Record

> Per-audit record capturing what was audited, by whom, when, with what findings — the lifecycle-end artefact of each audit engagement. Distinct from the programme: the programme is the plan, the execution record is the proof. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:9.2:audit_execution_record -->
<!-- column: item:9.2:rec_audit_id -->
<!-- column: item:9.2:rec_scope -->
<!-- column: item:9.2:rec_auditor -->
<!-- column: item:9.2:rec_date -->
<!-- column: item:9.2:rec_findings -->
<!-- column: item:9.2:rec_handoff -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:9.2:audit_execution_record -->
| Rec Audit Id | Rec Scope | Rec Auditor | Rec Date | Rec Findings | Rec Handoff |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:9.2:audit_execution_record -->

## Column guidance — what to fill in

### Rec Audit Id

<<MUST item:9.2:rec_audit_id>>
_Why: Audit defensibility_

> _Standard text:_ Unique audit identifier per row

### Rec Scope

<<MUST item:9.2:rec_scope>>
_Why: Clause 9.2a_

> _Standard text:_ Per-audit scope (which ISMS process / area was audited)

### Rec Auditor

<<MUST item:9.2:rec_auditor>>
_Why: Clause 9.2c_

> _Standard text:_ Per-audit auditor identity + independence assertion

### Rec Date

<<MUST item:9.2:rec_date>>
_Why: Currency_

> _Standard text:_ Per-audit execution date

### Rec Findings

<<MUST item:9.2:rec_findings>>
_Why: Clause 9.2d_

> _Standard text:_ Per-audit findings list (conformities + nonconformities + observations)

### Rec Handoff

<<MUST item:9.2:rec_handoff>>
_Why: Clause 9.2e_

> _Standard text:_ Per-audit handoff to 10.2 NC/CA procedure where findings include nonconformities

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rec Mgmt Review Link

<<SHOULD item:9.2:rec_mgmt_review_link>>
_Why: Clause 9.3.2a_

> _Standard text:_ Per-audit reference number cited in the next 9.3 management review
