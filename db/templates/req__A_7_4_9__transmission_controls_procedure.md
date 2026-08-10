---
leaf_id: req:A.7.4.9:transmission_controls_procedure
control_ref: A.7.4.9
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# PII Transmission Controls Procedure

<<DOC_CONTROL>>

> §7.4.9 requires appropriate controls on PII transmitted over data-transmission networks (to another organisation / between org locations / etc.). Bridges to 27001 A.8.24 cryptography + A.5.14 information transfer.

## What this template gives you

This template helps you set up clear procedures for protecting personal information when it’s sent over networks, ensuring you meet privacy and security requirements for data transfers.

## When to use it

Use this whenever your organization sends personal data to another company or between your own locations, and review it whenever your data transfer processes or partners change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes to complete this from scratch, as you’ll need to address each required section in detail.

## 1. Authorised transmission channels defined (secure protocols + endpoints + auth requirements)

<<MUST item:A.7.4.9:proc_authz_channels>>
_Why: §7.4.9 — only authorized individuals_

<<GUIDANCE>>

<<TEXT>>

## 2. Encryption-in-transit standard (TLS 1.2+ / VPN / SFTP / etc.) per channel

<<MUST item:A.7.4.9:proc_encryption>>
_Why: GDPR Art.32.1.a + §7.4.9_

<<GUIDANCE>>

<<TEXT>>

## 3. Audit log retention for every transmission (who + what + when + where)

<<MUST item:A.7.4.9:proc_audit_logs>>
_Why: §7.4.9 — retention of audit logs_

<<GUIDANCE>>

<<TEXT>>

## 4. Integrity verification (checksums / signed payloads for critical transmissions)

<<MUST item:A.7.4.9:proc_integrity_verification>>
_Why: GDPR Art.32.1.b_

<<GUIDANCE>>

<<TEXT>>

## 5. Recipient verification — PII reaches intended destination + not intercepted

<<MUST item:A.7.4.9:proc_recipient_verification>>
_Why: §7.4.9 — reaches intended destination_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Infrastructure + Security Engineering)

<<SHOULD item:A.7.4.9:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
