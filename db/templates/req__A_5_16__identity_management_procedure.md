---
leaf_id: req:A.5.16:identity_management_procedure
control_ref: A.5.16
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
---

# Identity Lifecycle Management Procedure

> A.5.16 requires the full lifecycle of identities to be managed — creation, modification, suspension, termination — across human, contractor, service, shared and non-human account types. The procedure documents each lifecycle step, timeliness expectations, ownership chain (HR triggers, IT executes, manager approves), and the connection to authentication-information lifecycle in A.5.17. The identity register, periodic program review and per-identity revocation record are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Identity creation steps (verification of person, naming convention, initial entitlements — least-privilege at issuance)

<<MUST item:A.5.16:creation>>
_Why: 27002:5.16 — lifecycle creation_

<<TEXT>>

## 2. Modification steps for role changes (add/remove entitlements; same-day or next-business-day SLA)

<<MUST item:A.5.16:modification>>
_Why: 27002:5.16 — lifecycle modification_

<<TEXT>>

## 3. Suspension steps for leave of absence, risk events (under investigation), or extended inactivity (auto-suspend at N days idle)

<<MUST item:A.5.16:suspension>>
_Why: 27002:5.16 — lifecycle suspension_

<<TEXT>>

## 4. Termination steps with stated deactivation timeline (e.g. within 24h of last day; immediate on involuntary termination)

<<MUST item:A.5.16:termination>>
_Why: 27002:5.16 — lifecycle termination_

<<TEXT>>

## 5. Unique identity per person (no shared user accounts for individuals; named accountability)

<<MUST item:A.5.16:unique_identity>>
_Why: 27002:5.16 — managed_

<<TEXT>>

## 6. Ownership of each lifecycle phase (HR triggers from leaver register; IT executes; manager approves; InfoSec oversight)

<<MUST item:A.5.16:ownership>>
_Why: Accountability + cross-link to [[A.5.11]]_

<<TEXT>>

## 7. Service / shared / non-human account governance (named human owner, expiry, scope, monitoring) — promoted from SHOULD because this is the weakest spot in most identity hygiene programs

<<MUST item:A.5.16:service_accounts>>
_Why: 27002:5.16 — managed (all identity types)_

<<TEXT>>

## 8. Cross-reference to A.5.17 authentication-information lifecycle (credential issuance and revocation are paired with identity events)

<<MUST item:A.5.16:authn_link>>
_Why: 27002:5.16 + cross-link to [[A.5.17]]_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic identity attestation cadence (e.g. annual recertification of each identity by its owner) referenced

<<SHOULD item:A.5.16:attestation>>
_Why: Drift prevention + cross-link to [[A.5.18]]_

<<TEXT>>

### 2. Contractor-specific path documented (fixed expiry, automatic disable; no manual extension without re-approval)

<<SHOULD item:A.5.16:contractor_path>>
_Why: High-risk workforce segment_

<<TEXT>>

### 3. Emergency-disable path (break-glass deactivation when standard SLA is too slow — e.g. immediate revocation on incident escalation)

<<SHOULD item:A.5.16:emergency_disable>>
_Why: Real-world coverage_

<<TEXT>>
