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

> §7.4.9 requires appropriate controls on PII transmitted over data-transmission networks (to another organisation / between org locations / etc.). Bridges to 27001 A.8.24 cryptography + A.5.14 information transfer.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Authorised transmission channels defined (secure protocols + endpoints + auth requirements)

<<MUST item:A.7.4.9:proc_authz_channels>>
_Why: §7.4.9 — only authorized individuals_

<<TEXT>>

## 2. Encryption-in-transit standard (TLS 1.2+ / VPN / SFTP / etc.) per channel

<<MUST item:A.7.4.9:proc_encryption>>
_Why: GDPR Art.32.1.a + §7.4.9_

<<TEXT>>

## 3. Audit log retention for every transmission (who + what + when + where)

<<MUST item:A.7.4.9:proc_audit_logs>>
_Why: §7.4.9 — retention of audit logs_

<<TEXT>>

## 4. Integrity verification (checksums / signed payloads for critical transmissions)

<<MUST item:A.7.4.9:proc_integrity_verification>>
_Why: GDPR Art.32.1.b_

<<TEXT>>

## 5. Recipient verification — PII reaches intended destination + not intercepted

<<MUST item:A.7.4.9:proc_recipient_verification>>
_Why: §7.4.9 — reaches intended destination_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Infrastructure + Security Engineering)

<<SHOULD item:A.7.4.9:proc_owner>>
_Why: Accountability_

<<TEXT>>
