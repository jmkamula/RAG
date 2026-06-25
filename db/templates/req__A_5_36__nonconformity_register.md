---
leaf_id: req:A.5.36:nonconformity_register
control_ref: A.5.36
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
table_shape: true
---

# Compliance Nonconformity Register

> A.5.36 requires corrective actions tracked to closure — but the corrective-action promise is theoretical without a per-NC lifecycle tracker. The nonconformity register catalogues every NC raised: severity, owner, agreed corrective action, target date, closure status, root cause. This is the audit-defensibility artefact paired with the review records

<!-- TABLE-COLUMNS leaf:req:A.5.36:nonconformity_register -->
<!-- column: item:A.5.36:nc_id -->
<!-- column: item:A.5.36:nc_severity -->
<!-- column: item:A.5.36:nc_owner -->
<!-- column: item:A.5.36:nc_corrective_action -->
<!-- column: item:A.5.36:nc_status -->
<!-- column: item:A.5.36:nc_closure_evidence -->
<!-- column: item:A.5.36:nc_root_cause -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.36:nonconformity_register -->
| Nc Id | Nc Severity | Nc Owner | Nc Corrective Action | Nc Status | Nc Closure Evidence | Nc Root Cause |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.36:nonconformity_register -->

## Column guidance — what to fill in

### Nc Id

<<MUST item:A.5.36:nc_id>>
_Why: 27002:5.36 — review_

> _Standard text:_ Per-NC unique identifier traceable back to the source review record

### Nc Severity

<<MUST item:A.5.36:nc_severity>>
_Why: 27002:5.36 — review_

> _Standard text:_ Severity recorded per NC (matches the review record's severity classification)

### Nc Owner

<<MUST item:A.5.36:nc_owner>>
_Why: Accountability_

> _Standard text:_ Named owner per NC (named individual, not generic team) with target closure date

### Nc Corrective Action

<<MUST item:A.5.36:nc_corrective_action>>
_Why: Closes the loop_

> _Standard text:_ Corrective action stated per NC (the specific change committed — policy update, control implementation, training delivery)

### Nc Status

<<MUST item:A.5.36:nc_status>>
_Why: Operational discipline_

> _Standard text:_ Current status per NC (open / in-progress / closed / aged-overdue / risk-accepted-with-exception) with last-updated date

### Nc Closure Evidence

<<MUST item:A.5.36:nc_closure_evidence>>
_Why: Audit defensibility_

> _Standard text:_ Closure evidence reference per closed NC (link to the artefact that proves the NC was addressed)

### Nc Root Cause

<<MUST item:A.5.36:nc_root_cause>>
_Why: Continual improvement_

> _Standard text:_ Root cause noted per NC where determined (drives systemic improvements vs point fixes)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Nc Exception Register

<<SHOULD item:A.5.36:nc_exception_register>>
_Why: Realistic operations_

> _Standard text:_ Exception register integration — risk-accepted NCs with expiry date (so 'we accept this' doesn't drift into 'we forgot this')

### Nc Aging Alerts

<<SHOULD item:A.5.36:nc_aging_alerts>>
_Why: Operational discipline_

> _Standard text:_ Aged-overdue alerting (notification when target date passes without closure)

### Nc Cross Review Link

<<SHOULD item:A.5.36:nc_cross_review_link>>
_Why: Cross-control coherence_

> _Standard text:_ Cross-link to A.5.35 independent-review finding register where the two are kept as one artefact
