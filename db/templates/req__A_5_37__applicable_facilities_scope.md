---
leaf_id: req:A.5.37:applicable_facilities_scope
control_ref: A.5.37
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# Applicable Information Processing Facilities Scope

> The upstream that drives the register. Documents the information processing facilities the organisation operates — what counts as a 'facility' (production systems, staging where production data is touched, key SaaS environments, on-prem infrastructure). ISO 27002:2022 § 5.37 expects every facility to have a documented procedure — drift between scope and register is the audit failure mode this leaf catches

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Systems in scope enumerated (production applications, databases, key infrastructure components — drives 'which facilities need a procedure')

<<MUST item:A.5.37:scope_systems>>
_Why: 27002:5.37 — information processing facilities_

<<TEXT>>

## 2. Key SaaS environments where the org operates the configuration (M365, Salesforce, ServiceNow, etc.) — even SaaS-hosted facilities need operating procedures for the org-side operator

<<MUST item:A.5.37:scope_saas>>
_Why: 27002:5.37 — relevant_

<<TEXT>>

## 3. Facility classes / categories (compute, storage, network, security tooling, identity, observability) — drives template variations and operator personas

<<MUST item:A.5.37:scope_facility_classes>>
_Why: 27002:5.37 — facilities_

<<TEXT>>

## 4. Cross-link to A.5.9 asset register — every information asset that is a facility should map to one or more procedures

<<MUST item:A.5.37:scope_asset_link>>
_Why: A.5.9 coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system entering production, SaaS adoption, M&A bringing new facilities, decommission)

<<SHOULD item:A.5.37:scope_change_drivers>>
_Why: Currency_

<<TEXT>>

### 2. Emergency-use subset identified (which facilities need procedures available even when normal tooling is down — DR scenarios)

<<SHOULD item:A.5.37:scope_emergency_set>>
_Why: Operational realism_

<<TEXT>>
