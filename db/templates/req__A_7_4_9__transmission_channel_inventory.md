---
leaf_id: req:A.7.4.9:transmission_channel_inventory
control_ref: A.7.4.9
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# PII Transmission Channel Inventory

> Per-channel row — the transmission channels the org uses for PII, with security profile + audit logging status. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.9:transmission_channel_inventory -->
<!-- column: item:A.7.4.9:reg_channel_id -->
<!-- column: item:A.7.4.9:reg_endpoint -->
<!-- column: item:A.7.4.9:reg_encryption -->
<!-- column: item:A.7.4.9:reg_auth_mechanism -->
<!-- column: item:A.7.4.9:reg_audit_log_retention -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.9:transmission_channel_inventory -->
| Reg Channel Id | Reg Endpoint | Reg Encryption | Reg Auth Mechanism | Reg Audit Log Retention |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.9:transmission_channel_inventory -->

## Column guidance — what to fill in

### Reg Channel Id

<<MUST item:A.7.4.9:reg_channel_id>>
_Why: Referenceability_

> _Standard text:_ Unique channel identifier per row

### Reg Endpoint

<<MUST item:A.7.4.9:reg_endpoint>>
_Why: Traceability_

> _Standard text:_ Source + destination endpoints per row

### Reg Encryption

<<MUST item:A.7.4.9:reg_encryption>>
_Why: GDPR Art.32.1.a_

> _Standard text:_ Encryption standard per row (TLS 1.2 / TLS 1.3 / VPN / SFTP / etc.)

### Reg Auth Mechanism

<<MUST item:A.7.4.9:reg_auth_mechanism>>
_Why: §7.4.9 — authorized_

> _Standard text:_ Authentication mechanism per row (mutual TLS / OAuth / API key + IP allowlist / etc.)

### Reg Audit Log Retention

<<MUST item:A.7.4.9:reg_audit_log_retention>>
_Why: §7.4.9 — retention of audit logs_

> _Standard text:_ Audit log retention per row

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Penetration Test

<<SHOULD item:A.7.4.9:reg_last_penetration_test>>
_Why: Assurance_

> _Standard text:_ Last pen-test / security assessment date per row
