---
leaf_id: req:A.5.17:credential_register
control_ref: A.5.17
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Credential Register

> A.5.17 requires every credential type to be visible — secret-sprawl is the failure mode where ad-hoc credentials proliferate outside the central vault, escape rotation, and persist past their owner. The register catalogues every credential type deployed: type id, scope, vault location, rotation cadence, MFA factors required, owner. It is the operational record that proves credential governance covers ALL credentials in use, not just the ones IT remembered to onboard to the password manager

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each credential type captured with a unique identifier (user_password / admin_password / api_key / service_token / cert / mfa_factor / break_glass)

<<MUST item:A.5.17:reg_credential_type>>
_Why: 27002:5.17 — visibility_

<<TEXT>>

## 2. Scope per row (which systems/identities use this credential type)

<<MUST item:A.5.17:reg_scope>>
_Why: 27002:5.17 — managed_

<<TEXT>>

## 3. Storage vault per row (named secrets manager / KMS / cert store — never 'spreadsheet' or 'config file' for production credentials)

<<MUST item:A.5.17:reg_vault>>
_Why: 27002:5.17 — storage_

<<TEXT>>

## 4. Rotation cadence per row (manual N-days / automated / on-event-only with stated trigger types)

<<MUST item:A.5.17:reg_rotation_cadence>>
_Why: 27002:5.17 — rotation_

<<TEXT>>

## 5. MFA factor requirement per row where applicable (which factor classes; tied to access tier)

<<MUST item:A.5.17:reg_mfa_required>>
_Why: 27002:5.17 — MFA mandate_

<<TEXT>>

## 6. Named owner per row (human owner accountable for this credential type — covers governance, escalation, retirement decisions)

<<MUST item:A.5.17:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 7. Identity-register linkage per row (which identity types use this credential type — closes the loop with A.5.16)

<<MUST item:A.5.17:reg_identity_link>>
_Why: 27002:5.17 + cross-link to [[A.5.16]]_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Last-rotated timestamp per row where applicable (drives drift detection — stale-rotation alert)

<<SHOULD item:A.5.17:reg_last_rotated>>
_Why: Drift prevention_

<<TEXT>>

### 2. Phishing-resistant flag per row where the credential is phishing-resistant (FIDO2, passkeys, hardware-token) vs phishable (SMS, password)

<<SHOULD item:A.5.17:reg_phishing_resistant>>
_Why: Modern direction tracking_

<<TEXT>>
