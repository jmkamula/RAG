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

<<DOC_CONTROL>>

> §8.4.3 mirrors §7.4.9 from processor side — customer PII transmitted over networks subject to appropriate controls. Adds an explicit customer-consultation dimension where contract is silent.

## What this template gives you

This template helps you document how your organization controls the transmission of customer personal data over networks, including steps for consulting with customers when your contract doesn’t specify requirements.

## When to use it

Use this procedure whenever your organization handles customer personal data as a processor and needs to ensure secure transmission, especially if your contract doesn’t clearly address these controls. Update it whenever your processes or agreements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes to complete this template from scratch, as you’ll need to address five required elements and one recommended section.

## 1. Authorised transmission channels per customer

<<MUST item:B.8.4.3:proc_authz_channels>>
_Why: §8.4.3 — only authorized_

<<GUIDANCE>>

<<TEXT>>

## 2. Encryption in transit standard per channel

<<MUST item:B.8.4.3:proc_encryption>>
_Why: GDPR Art.32.1.a + §8.4.3_

<<GUIDANCE>>

<<TEXT>>

## 3. Audit data retention per transmission event

<<MUST item:B.8.4.3:proc_audit_data>>
_Why: §8.4.3 — retention of audit data_

<<GUIDANCE>>

<<TEXT>>

## 4. Contract-terms coverage — customer-contract transmission requirements captured (B.8.2.1)

<<MUST item:B.8.4.3:proc_contract_terms>>
_Why: §8.4.3 — requirements included in contract_

<<GUIDANCE>>

<<TEXT>>

## 5. Customer-advice path — where contract silent on transmission requirements, customer consulted before transmission

<<MUST item:B.8.4.3:proc_customer_advice>>
_Why: §8.4.3 — take advice from customer_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Platform Ops + Security Engineering)

<<SHOULD item:B.8.4.3:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
