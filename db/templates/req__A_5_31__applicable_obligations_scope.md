---
leaf_id: req:A.5.31:applicable_obligations_scope
control_ref: A.5.31
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Applicable Obligations Scope

> The upstream that drives the register. Documents the business activity surfaces — jurisdictions, services, customer types, data categories, sectoral classifications — that determine which obligations apply. ISO 27002:2022 § 5.31 expects organisations to know their applicability before listing obligations

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Jurisdictions covered (HQ, places of business, customer locations, data residency, transfer destinations)

<<MUST item:A.5.31:scope_jurisdictions>>
_Why: 27002:5.31a_

<<TEXT>>

## 2. Services offered (regulated activities — payments, health data processing, telco, AI systems under upcoming regimes)

<<MUST item:A.5.31:scope_services>>
_Why: 27002:5.31 — relevant_

<<TEXT>>

## 3. Customer types driving contractual obligations (regulated industries, government, B2C consumers)

<<MUST item:A.5.31:scope_customer_types>>
_Why: 27002:5.31c — contractual_

<<TEXT>>

## 4. Personal/sensitive/regulated data categories processed (drives GDPR, HIPAA, sectoral data laws)

<<MUST item:A.5.31:scope_data_categories>>
_Why: GDPR/sectoral linkage_

<<TEXT>>

## 5. Sectoral classification (NIS2 essential/important, DORA financial-entity, critical-infrastructure designation, etc.)

<<MUST item:A.5.31:scope_sectoral_class>>
_Why: 27002:5.31 — applicability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-link to A.5.5 applicable-authorities scope — same drivers; shared updates

<<SHOULD item:A.5.31:scope_authority_link>>
_Why: Cross-control coherence_

<<TEXT>>

### 2. Trigger list for re-scoping (new geography, new service line, M&A, change in customer mix)

<<SHOULD item:A.5.31:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
