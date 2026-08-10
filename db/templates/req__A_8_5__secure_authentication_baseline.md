---
leaf_id: req:A.8.5:secure_authentication_baseline
control_ref: A.8.5
standard_id: ISO27001:2022
evidence_type: configuration_baseline
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Secure Authentication Baseline

<<DOC_CONTROL>>

> A.8.5 baseline — the authentication configuration state. Factor requirements per access tier, MFA enforcement, session management, lockout thresholds. The procedure, auth log and review are sibling leaves

## What this template gives you

This template helps you document your authentication setup, including requirements for multi-factor authentication, session controls, and lockout policies, making it easier to demonstrate compliance with ISO 27001 control A.8.5.

## When to use it

Use this template whenever you need to describe or update your authentication configuration for your environment. Review and refresh the document as needed to reflect any changes in your authentication practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this template from scratch, as each required section will take roughly 10 to 15 minutes to fill out.

## 1. Authentication factor requirements per risk tier (single / MFA / step-up)

<<MUST item:A.8.5:bl_factor_requirements>>
_Why: 27002:8.5 — based on information access restrictions_

<<GUIDANCE>>

<<TEXT>>

## 2. MFA scope — universal for privileged + remote + cross-tenant; risk-based elsewhere (modern baseline; phishing-resistant MFA preferred)

<<MUST item:A.8.5:bl_mfa_scope>>
_Why: 27002:8.5 — secure authentication_

<<GUIDANCE>>

<<TEXT>>

## 3. Password standard configured (length, breach-list checking, no rotation unless compromise — NIST 800-63B alignment)

<<MUST item:A.8.5:bl_password_standard>>
_Why: 27002:8.5 — secure authentication_

<<GUIDANCE>>

<<TEXT>>

## 4. Session management (timeout, re-authentication for sensitive actions, concurrent-session limits)

<<MUST item:A.8.5:bl_session_mgmt>>
_Why: 27002:8.5 — implemented_

<<GUIDANCE>>

<<TEXT>>

## 5. Lockout / throttling configured for failed attempts

<<MUST item:A.8.5:bl_lockout>>
_Why: 27002:8.5 — secure_

<<GUIDANCE>>

<<TEXT>>

## 6. Secure transmission enforced (TLS only, no plaintext credentials anywhere — including legacy protocols)

<<MUST item:A.8.5:bl_secure_transmission>>
_Why: 27002:8.5 — secure authentication_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Passwordless / phishing-resistant authentication available for privileged users

<<SHOULD item:A.8.5:bl_passwordless>>
_Why: Modern direction_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
