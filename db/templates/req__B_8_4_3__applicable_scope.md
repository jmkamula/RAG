---
leaf_id: req:B.8.4.3:applicable_scope
control_ref: B.8.4.3
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processor Transmission Scope

<<DOC_CONTROL>>

> The upstream — every context transmitting customer PII (customer-facing APIs / partner exchanges / cross-region backups / subprocessor integrations).

## What this template gives you

This template helps you clearly define which systems and processes transmit customer personal data, making it easier to demonstrate compliance with privacy standards like ISO 27701.

## When to use it

Use this document whenever your organization handles customer personal data through APIs, partner exchanges, backups, or integrations, and update it whenever there are changes to these data flows.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required elements about your data transmission practices.

## 1. Customer-facing transmission (APIs + webhooks)

<<MUST item:B.8.4.3:scope_customer_facing>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Subprocessor flows (data-sharing with subprocessors)

<<MUST item:B.8.4.3:scope_subprocessor_flows>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. Internal + cross-region flows (backup replication / DR / warehouse)

<<MUST item:B.8.4.3:scope_internal_flows>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new subprocessor / new region)

<<SHOULD item:B.8.4.3:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
