---
leaf_id: req:A.7.4.9:applicable_scope
control_ref: A.7.4.9
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Transmission Contexts Scope

> The upstream — which transmission contexts carry PII (customer-facing APIs / integrations / partner exchanges / cross-region backups / email / etc.).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Customer-facing APIs carrying PII

<<MUST item:A.7.4.9:scope_customer_apis>>
_Why: Coverage_

<<TEXT>>

## 2. Integration endpoints (partner APIs + processor exchanges + third-party enrichment)

<<MUST item:A.7.4.9:scope_integrations>>
_Why: Coverage_

<<TEXT>>

## 3. Internal transfers (cross-region backup / DR replication / data warehouse loads)

<<MUST item:A.7.4.9:scope_internal_transfers>>
_Why: Coverage_

<<TEXT>>

## 4. Email + file-sharing paths where PII may be transmitted

<<MUST item:A.7.4.9:scope_email_paths>>
_Why: Comprehensiveness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new integration / new region / new partner)

<<SHOULD item:A.7.4.9:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
