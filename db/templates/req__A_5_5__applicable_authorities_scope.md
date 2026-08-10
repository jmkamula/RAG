---
leaf_id: req:A.5.5:applicable_authorities_scope
control_ref: A.5.5
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# Applicable Authorities Scope

<<DOC_CONTROL>>

> The upstream that drives the register. Documents which authorities are relevant today and on what basis — jurisdictions of operation, sectoral obligations, types of personal data processed, critical-service classifications. ISO 27002:2022 § 5.5 expects the organisation to know which authorities apply before claiming to maintain contact with them

## What this template gives you

This template helps you clearly identify which laws, regulations, and authorities apply to your organization based on where you operate, your industry, and the types of data you handle.

## When to use it

Use this document whenever you need to define or update the list of authorities and obligations relevant to your business. Review and refresh it whenever your operations, services, or regulatory environment change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 45 to 60 minutes completing this from scratch, as you'll need to gather and describe several key aspects of your organization's regulatory landscape.

## 1. Jurisdictions covered (HQ, places of business, customer locations) — each maps to one or more authorities

<<MUST item:A.5.5:scope_jurisdictions>>
_Why: 27002:5.5a — relevant_

<<GUIDANCE>>

<<TEXT>>

## 2. Sectoral obligations stated (finance, health, critical infrastructure, telecoms) driving sectoral regulators

<<MUST item:A.5.5:scope_sectoral>>
_Why: 27002:5.5a — relevant authorities_

<<GUIDANCE>>

<<TEXT>>

## 3. Personal-data processing flag → drives DPA inclusion per jurisdiction

<<MUST item:A.5.5:scope_personal_data>>
_Why: GDPR Art.51 / 27002:5.5_

<<GUIDANCE>>

<<TEXT>>

## 4. Authority categories mapped — supervisory (DPA), sectoral regulator, law enforcement, national CERT/CSIRT

<<MUST item:A.5.5:scope_authority_categories>>
_Why: 27002:5.5a_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-link to the legal/regulatory register (A.5.31) — same drivers; the two should stay aligned

<<SHOULD item:A.5.5:scope_legal_register_link>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

### 2. Source for change monitoring (legal counsel, regulator alerts) that triggers re-scoping

<<SHOULD item:A.5.5:scope_change_monitoring>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
