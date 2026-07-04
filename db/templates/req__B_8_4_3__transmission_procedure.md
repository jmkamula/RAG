---
leaf_id: req:B.8.4.3:transmission_procedure
control_ref: B.8.4.3
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Processor Transmission Controls Procedure

> §8.4.3 mirrors §7.4.9 from processor side — customer PII transmitted over networks subject to appropriate controls. Adds an explicit customer-consultation dimension where contract is silent.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Authorised transmission channels per customer

<<MUST item:B.8.4.3:proc_authz_channels>>
_Why: §8.4.3 — only authorized_

<<TEXT>>

## 2. Encryption in transit standard per channel

<<MUST item:B.8.4.3:proc_encryption>>
_Why: GDPR Art.32.1.a + §8.4.3_

<<TEXT>>

## 3. Audit data retention per transmission event

<<MUST item:B.8.4.3:proc_audit_data>>
_Why: §8.4.3 — retention of audit data_

<<TEXT>>

## 4. Contract-terms coverage — customer-contract transmission requirements captured (B.8.2.1)

<<MUST item:B.8.4.3:proc_contract_terms>>
_Why: §8.4.3 — requirements included in contract_

<<TEXT>>

## 5. Customer-advice path — where contract silent on transmission requirements, customer consulted before transmission

<<MUST item:B.8.4.3:proc_customer_advice>>
_Why: §8.4.3 — take advice from customer_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Platform Ops + Security Engineering)

<<SHOULD item:B.8.4.3:proc_owner>>
_Why: Accountability_

<<TEXT>>
