---
leaf_id: req:A.5.26:incident_closure_record
control_ref: A.5.26
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
table_shape: true
---

# Per-Incident Closure Records

> A.5.26 requires incidents to close with documented outcomes that feed § 5.27 lessons-learned. The closure record evidences the actual close: which incident, the root cause, the containment effectiveness, the recovery validation, and the handoff to lessons-learned. One record per incident, traceable back to the incident register

<!-- TABLE-COLUMNS leaf:req:A.5.26:incident_closure_record -->
<!-- column: item:A.5.26:cls_incident_ref -->
<!-- column: item:A.5.26:cls_root_cause -->
<!-- column: item:A.5.26:cls_containment_eff -->
<!-- column: item:A.5.26:cls_recovery_valid -->
<!-- column: item:A.5.26:cls_lessons_handoff -->
<!-- column: item:A.5.26:cls_authoriser -->
<!-- column: item:A.5.26:cls_sla_met -->
<!-- column: item:A.5.26:cls_gdpr_triggered -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.26:incident_closure_record -->
| Cls Incident Ref | Cls Root Cause | Cls Containment Eff | Cls Recovery Valid | Cls Lessons Handoff | Cls Authoriser | Cls Sla Met | Cls Gdpr Triggered |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.26:incident_closure_record -->

## Column guidance — what to fill in

### Cls Incident Ref

<<MUST item:A.5.26:cls_incident_ref>>
_Why: 27002:5.26 — recording_

> _Standard text:_ Incident identifier per record (links to the incident register)

### Cls Root Cause

<<MUST item:A.5.26:cls_root_cause>>
_Why: 27002:5.26h_

> _Standard text:_ Root cause captured (technical + organisational contributors)

### Cls Containment Eff

<<MUST item:A.5.26:cls_containment_eff>>
_Why: 27002:5.26a_

> _Standard text:_ Containment effectiveness assessed (did the actions taken actually limit damage)

### Cls Recovery Valid

<<MUST item:A.5.26:cls_recovery_valid>>
_Why: 27002:5.26e_

> _Standard text:_ Recovery validation evidenced (system returned to secure state; verified, not just attempted)

### Cls Lessons Handoff

<<MUST item:A.5.26:cls_lessons_handoff>>
_Why: 27002:5.26 → 5.27_

> _Standard text:_ Handoff reference into A.5.27 lessons register

### Cls Authoriser

<<MUST item:A.5.26:cls_authoriser>>
_Why: Accountability_

> _Standard text:_ Closure authority per record (named role)

### Cls Sla Met

<<MUST item:A.5.26:cls_sla_met>>
_Why: Auditor-critical timeliness proof — drives the rev_metrics analysis on the review leaf_

> _Standard text:_ MTTC / MTTR / containment-SLA-met flag per record — structured boolean against the targets stated in the procedure or service catalogue; analogous to A.5.16:rev_sla_met

### Cls Gdpr Triggered

<<MUST item:A.5.26:cls_gdpr_triggered>>
_Why: GDPR Art.33.1 / Art.33.5 — pairs with procedure-level gdpr_72h_trigger_check_

> _Standard text:_ GDPR Art.33 breach-notification trigger flag per record (yes/no with notification reference where yes) — proves the personal-data integration with A.5.26 fires reliably

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Cls External Notif

<<SHOULD item:A.5.26:cls_external_notif>>
_Why: 27002:5.26 — communication_

> _Standard text:_ External notifications made per record (regulators, customers, suppliers)

### Cls Evidence Archive

<<SHOULD item:A.5.26:cls_evidence_archive>>
_Why: Forensic preservation_

> _Standard text:_ Evidence package archived per record (link to A.5.28 evidence store)
