---
leaf_id: req:A.8.19:installation_register
control_ref: A.8.19
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Software Installation Register

> Per-installation record — what was installed, when, where, by whom, verification artefact

<!-- TABLE-COLUMNS leaf:req:A.8.19:installation_register -->
<!-- column: item:A.8.19:reg_install_id -->
<!-- column: item:A.8.19:reg_software -->
<!-- column: item:A.8.19:reg_target -->
<!-- column: item:A.8.19:reg_actor -->
<!-- column: item:A.8.19:reg_verification -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.19:installation_register -->
| Reg Install Id | Reg Software | Reg Target | Reg Actor | Reg Verification |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.19:installation_register -->

## Column guidance — what to fill in

### Reg Install Id

<<MUST item:A.8.19:reg_install_id>>
_Why: Auditability_

> _Standard text:_ Per-install unique identifier

### Reg Software

<<MUST item:A.8.19:reg_software>>
_Why: 27002:8.19 — securely manage_

> _Standard text:_ Per-install software name + version + source (from approved list)

### Reg Target

<<MUST item:A.8.19:reg_target>>
_Why: 27002:8.19 — operational systems_

> _Standard text:_ Per-install target system

### Reg Actor

<<MUST item:A.8.19:reg_actor>>
_Why: Accountability_

> _Standard text:_ Per-install authorised actor (privileged role assignment)

### Reg Verification

<<MUST item:A.8.19:reg_verification>>
_Why: 27002:8.19 — securely_

> _Standard text:_ Per-install verification artefacts (signature check / functional test / vuln-scan result)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Change Link

<<SHOULD item:A.8.19:reg_change_link>>
_Why: Cross-control coherence_

> _Standard text:_ Per-install cross-link to A.8.32 change record where applicable
