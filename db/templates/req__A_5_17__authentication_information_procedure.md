---
leaf_id: req:A.5.17:authentication_information_procedure
control_ref: A.5.17
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 9
should_count: 3
---

# Authentication Information Management Procedure

<<DOC_CONTROL>>

> A.5.17 requires authentication information (passwords, tokens, keys, certificates, biometric data) to be allocated and managed by a controlled process, with personnel advised on appropriate handling. The procedure documents allocation, transmission, storage, complexity/rotation, reset/recovery, user advisory, MFA expectations and the connection to identity lifecycle in A.5.16. The credential register, periodic program review and per-credential revocation record are sibling leaves

## What this template gives you

This template helps you set up a clear process for managing authentication information like passwords, tokens, and keys, ensuring your team knows how to handle, store, and rotate credentials securely.

## When to use it

Use this procedure whenever your organization manages authentication information for systems or applications. Review and update it whenever there are changes to your authentication processes or as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 2 to 3 hours drafting this document from scratch, depending on the complexity of your environment and the number of credentials you manage.

## 1. Initial allocation method for authentication information per credential type (in-person, secure channel, ephemeral link, hardware-token enrolment)

<<MUST item:A.5.17:allocation>>
_Why: 27002:5.17 — allocation_

<<GUIDANCE>>

<<TEXT>>

## 2. Transmission method requirements (out-of-band, encrypted, never on the same channel as the identity itself; never via plain email)

<<MUST item:A.5.17:transmission>>
_Why: 27002:5.17 — management process_

<<GUIDANCE>>

<<TEXT>>

## 3. Password / credential complexity and rotation requirements (length, character classes, history, max-age — risk-tiered per scope)

<<MUST item:A.5.17:complexity>>
_Why: 27002:5.17 — management_

<<GUIDANCE>>

<<TEXT>>

## 4. Storage requirements (hashed + salted with modern algorithm — argon2/scrypt/bcrypt; vaulted in secrets manager; never plaintext anywhere)

<<MUST item:A.5.17:storage>>
_Why: 27002:5.17 — management_

<<GUIDANCE>>

<<TEXT>>

## 5. Reset / recovery process with identity re-verification (out-of-band; no static security questions; rate-limited)

<<MUST item:A.5.17:reset>>
_Why: 27002:5.17 — management_

<<GUIDANCE>>

<<TEXT>>

## 6. Advisory guidance to personnel on protecting their authentication information (no sharing, no re-use, password-manager guidance, compromise reporting path)

<<MUST item:A.5.17:user_advisory>>
_Why: 27002:5.17 — advising personnel_

<<GUIDANCE>>

<<TEXT>>

## 7. Multi-factor authentication mandated for in-scope access (admin accounts, remote access, sensitive data access) — promoted from SHOULD because MFA is no longer optional baseline

<<MUST item:A.5.17:mfa>>
_Why: 27002:5.17 — modern baseline_

<<GUIDANCE>>

<<TEXT>>

## 8. Cross-reference to A.5.16 identity lifecycle (credential issuance follows identity creation; credential revocation follows identity termination; pairing enforced not optional)

<<MUST item:A.5.17:identity_link>>
_Why: 27002:5.17 + cross-link to [[A.5.16]]_

<<GUIDANCE>>

<<TEXT>>

## 9. Compromise-response path (when a credential is reported or detected compromised — forced rotation, identity-level investigation, scope expansion check)

<<MUST item:A.5.17:compromise_response>>
_Why: 27002:5.17 — handle compromise_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Authentication factor classes documented (knowledge / possession / inherence) and which combinations satisfy MFA per access tier

<<SHOULD item:A.5.17:factor_classes>>
_Why: Risk-based mapping_

<<GUIDANCE>>

<<TEXT>>

### 2. Passwordless / phishing-resistant authentication noted where deployed (FIDO2, passkeys) — direction-of-travel statement

<<SHOULD item:A.5.17:passwordless>>
_Why: Modern direction_

<<GUIDANCE>>

<<TEXT>>

### 3. Break-glass credentials documented separately (emergency-only accounts with sealed-envelope or vault-with-audit access)

<<SHOULD item:A.5.17:break_glass>>
_Why: Operational continuity_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
