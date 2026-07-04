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

> The upstream — every context transmitting customer PII (customer-facing APIs / partner exchanges / cross-region backups / subprocessor integrations).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Customer-facing transmission (APIs + webhooks)

<<MUST item:B.8.4.3:scope_customer_facing>>
_Why: Coverage_

<<TEXT>>

## 2. Subprocessor flows (data-sharing with subprocessors)

<<MUST item:B.8.4.3:scope_subprocessor_flows>>
_Why: Coverage_

<<TEXT>>

## 3. Internal + cross-region flows (backup replication / DR / warehouse)

<<MUST item:B.8.4.3:scope_internal_flows>>
_Why: Coverage_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new subprocessor / new region)

<<SHOULD item:B.8.4.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
