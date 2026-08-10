---
leaf_id: req:A.5.17:credential_register
control_ref: A.5.17
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Credential Register

<<DOC_CONTROL>>

> A.5.17 requires every credential type to be visible — secret-sprawl is the failure mode where ad-hoc credentials proliferate outside the central vault, escape rotation, and persist past their owner. The register catalogues every credential type deployed: type id, scope, vault location, rotation cadence, MFA factors required, owner. It is the operational record that proves credential governance covers ALL credentials in use, not just the ones IT remembered to onboard to the password manager

<!-- TABLE-COLUMNS leaf:req:A.5.17:credential_register -->
<!-- column: item:A.5.17:reg_credential_type -->
<!-- column: item:A.5.17:reg_scope -->
<!-- column: item:A.5.17:reg_vault -->
<!-- column: item:A.5.17:reg_rotation_cadence -->
<!-- column: item:A.5.17:reg_mfa_required -->
<!-- column: item:A.5.17:reg_owner -->
<!-- column: item:A.5.17:reg_identity_link -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a complete, up-to-date list of all credential types in your environment, making it easier to manage, rotate, and secure access credentials across your organization.

## When to use it

Use this register at all times to track every credential in your environment, updating it whenever new credentials are created, changed, or retired to ensure nothing is missed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each credential type you need to document, so the total time will depend on how many credentials you have to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.17:credential_register -->
| Reg Credential Type | Reg Scope | Reg Vault | Reg Rotation Cadence | Reg Mfa Required | Reg Owner | Reg Identity Link |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.17:credential_register -->

## Column guidance — what to fill in

### Reg Credential Type

<<MUST item:A.5.17:reg_credential_type>>
_Why: 27002:5.17 — visibility_

> _Standard text:_ Each credential type captured with a unique identifier (user_password / admin_password / api_key / service_token / cert / mfa_factor / break_glass)

<<GUIDANCE>>

### Reg Scope

<<MUST item:A.5.17:reg_scope>>
_Why: 27002:5.17 — managed_

> _Standard text:_ Scope per row (which systems/identities use this credential type)

<<GUIDANCE>>

### Reg Vault

<<MUST item:A.5.17:reg_vault>>
_Why: 27002:5.17 — storage_

> _Standard text:_ Storage vault per row (named secrets manager / KMS / cert store — never 'spreadsheet' or 'config file' for production credentials)

<<GUIDANCE>>

### Reg Rotation Cadence

<<MUST item:A.5.17:reg_rotation_cadence>>
_Why: 27002:5.17 — rotation_

> _Standard text:_ Rotation cadence per row (manual N-days / automated / on-event-only with stated trigger types)

<<GUIDANCE>>

### Reg Mfa Required

<<MUST item:A.5.17:reg_mfa_required>>
_Why: 27002:5.17 — MFA mandate_

> _Standard text:_ MFA factor requirement per row where applicable (which factor classes; tied to access tier)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.5.17:reg_owner>>
_Why: Accountability_

> _Standard text:_ Named owner per row (human owner accountable for this credential type — covers governance, escalation, retirement decisions)

<<GUIDANCE>>

### Reg Identity Link

<<MUST item:A.5.17:reg_identity_link>>
_Why: 27002:5.17 + cross-link to [[A.5.16]]_

> _Standard text:_ Identity-register linkage per row (which identity types use this credential type — closes the loop with A.5.16)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Rotated

<<SHOULD item:A.5.17:reg_last_rotated>>
_Why: Drift prevention_

> _Standard text:_ Last-rotated timestamp per row where applicable (drives drift detection — stale-rotation alert)

<<GUIDANCE>>

### Reg Phishing Resistant

<<SHOULD item:A.5.17:reg_phishing_resistant>>
_Why: Modern direction tracking_

> _Standard text:_ Phishing-resistant flag per row where the credential is phishing-resistant (FIDO2, passkeys, hardware-token) vs phishable (SMS, password)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
