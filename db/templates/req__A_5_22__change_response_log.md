---
leaf_id: req:A.5.22:change_response_log
control_ref: A.5.22
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Supplier Service Change Response Log

> A.5.22 requires the org to manage changes in supplier service delivery — network/tech changes, new dev tools, location changes, change of sub-contractors, re-tendering. Each change is evidenced by a log entry: change type captured, impact assessed, treatment decided, with escalation to termination where findings warrant

<!-- TABLE-COLUMNS leaf:req:A.5.22:change_response_log -->
<!-- column: item:A.5.22:chg_type -->
<!-- column: item:A.5.22:chg_impact -->
<!-- column: item:A.5.22:chg_treatment -->
<!-- column: item:A.5.22:chg_escalation -->
<!-- column: item:A.5.22:chg_authoriser -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.22:change_response_log -->
| Chg Type | Chg Impact | Chg Treatment | Chg Escalation | Chg Authoriser |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.22:change_response_log -->

## Column guidance — what to fill in

### Chg Type

<<MUST item:A.5.22:chg_type>>
_Why: 27002:5.22k_

> _Standard text:_ Change type captured (network / technology / dev tools / location / sub-contractor / re-tendering)

### Chg Impact

<<MUST item:A.5.22:chg_impact>>
_Why: 27002:5.22k_

> _Standard text:_ Impact assessment on InfoSec arrangements (which controls affected, which threats opened or closed)

### Chg Treatment

<<MUST item:A.5.22:chg_treatment>>
_Why: 27002:5.22k_

> _Standard text:_ Treatment decided (accept / mitigate / re-paper agreement / terminate relationship)

### Chg Escalation

<<MUST item:A.5.22:chg_escalation>>
_Why: 27002:5.22j,k_

> _Standard text:_ Escalation criteria for findings — when a finding terminates the relationship

### Chg Authoriser

<<MUST item:A.5.22:chg_authoriser>>
_Why: Accountability_

> _Standard text:_ Authoriser of the treatment decision (proportional to residual risk)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Chg Regulatory

<<SHOULD item:A.5.22:chg_regulatory>>
_Why: 27002:5.22 — compliance_

> _Standard text:_ Regulatory-notification check (where the change triggers a regulator-notify obligation)

### Chg Lessons

<<SHOULD item:A.5.22:chg_lessons>>
_Why: Continual improvement_

> _Standard text:_ Lessons-learned feeding back to the procedure or template (link to A.5.19 / A.5.20)
