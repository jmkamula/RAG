---
leaf_id: req:A.7.4.3:accuracy_incident_register
control_ref: A.7.4.3
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Accuracy Incident Register

> Per-incident row — detected inaccuracies + resolutions. Includes internal-detected + subject-reported cases. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.3:accuracy_incident_register -->
<!-- column: item:A.7.4.3:reg_incident_id -->
<!-- column: item:A.7.4.3:reg_detection_source -->
<!-- column: item:A.7.4.3:reg_pii_scope -->
<!-- column: item:A.7.4.3:reg_resolution -->
<!-- column: item:A.7.4.3:reg_root_cause -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.3:accuracy_incident_register -->
| Reg Incident Id | Reg Detection Source | Reg Pii Scope | Reg Resolution | Reg Root Cause |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.3:accuracy_incident_register -->

## Column guidance — what to fill in

### Reg Incident Id

<<MUST item:A.7.4.3:reg_incident_id>>
_Why: Audit trail_

> _Standard text:_ Unique incident identifier per row

### Reg Detection Source

<<MUST item:A.7.4.3:reg_detection_source>>
_Why: Traceability_

> _Standard text:_ Detection source per row (internal audit / subject rectification / integration reconciliation / external notification)

### Reg Pii Scope

<<MUST item:A.7.4.3:reg_pii_scope>>
_Why: Coverage_

> _Standard text:_ PII scope per row (which fields / how many subjects affected)

### Reg Resolution

<<MUST item:A.7.4.3:reg_resolution>>
_Why: §7.4.3 — respond to inaccurate PII_

> _Standard text:_ Resolution per row (corrected / cannot-correct-with-reason / erased / pending)

### Reg Root Cause

<<MUST item:A.7.4.3:reg_root_cause>>
_Why: Continuous improvement_

> _Standard text:_ Root cause per row (where a systemic issue emerged, remediation link)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Third Party Notified

<<SHOULD item:A.7.4.3:reg_third_party_notified>>
_Why: Downstream_

> _Standard text:_ Third-party notification flag if A.7.3.7 fired
