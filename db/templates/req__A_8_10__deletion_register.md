---
leaf_id: req:A.8.10:deletion_register
control_ref: A.8.10
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Per-Deletion Disposal Register

> Per-deletion lifecycle-end record — what was deleted, when, by what method, with verification artefact. Parallels A.5.28 evidence handling disposal pattern and A.7.14 secure disposal

<!-- TABLE-COLUMNS leaf:req:A.8.10:deletion_register -->
<!-- column: item:A.8.10:reg_event_id -->
<!-- column: item:A.8.10:reg_target -->
<!-- column: item:A.8.10:reg_trigger -->
<!-- column: item:A.8.10:reg_method -->
<!-- column: item:A.8.10:reg_verification -->
<!-- column: item:A.8.10:reg_backup_sweep -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.10:deletion_register -->
| Reg Event Id | Reg Target | Reg Trigger | Reg Method | Reg Verification | Reg Backup Sweep |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.10:deletion_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:A.8.10:reg_event_id>>
_Why: Auditability_

> _Standard text:_ Per-deletion unique identifier

### Reg Target

<<MUST item:A.8.10:reg_target>>
_Why: 27002:8.10 — deleted_

> _Standard text:_ Per-deletion target identifier (dataset / record class / asset / media id)

### Reg Trigger

<<MUST item:A.8.10:reg_trigger>>
_Why: 27002:8.10 — when no longer required_

> _Standard text:_ Per-deletion trigger (retention expiry / DSAR / asset retirement / legal-hold release / explicit instruction)

### Reg Method

<<MUST item:A.8.10:reg_method>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-deletion method used (matches procedure's method table for the media class)

### Reg Verification

<<MUST item:A.8.10:reg_verification>>
_Why: 27002:8.10 — deleted_

> _Standard text:_ Per-deletion verification artefact reference (log id / certificate / signed attestation)

### Reg Backup Sweep

<<MUST item:A.8.10:reg_backup_sweep>>
_Why: Common GDPR audit failure point_

> _Standard text:_ Per-deletion backup-sweep confirmation (or rationale if deferred to next backup-cycle deletion)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Actor

<<SHOULD item:A.8.10:reg_actor>>
_Why: Accountability_

> _Standard text:_ Per-deletion actor (person or automated job identifier)
