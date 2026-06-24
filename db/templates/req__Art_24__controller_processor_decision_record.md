---
leaf_id: req:Art.24:controller_processor_decision_record
control_ref: Art.24
standard_id: GDPR:2016/679
evidence_type: decision_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Controller / Processor Role Decision Record

> Per-relationship record documenting whether the org acts as controller, processor, joint controller, or third-party recipient for each processing activity. Art.24's accountability scope is shaped by this role assignment — without explicit documentation, role disputes during audits become unwinnable

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row processing activity (Art.30 RoPA reference)

<<MUST item:Art.24:role_activity_id>>
_Why: Cross-article_

<<TEXT>>

## 2. Per-row counterparty (customer / vendor / partner)

<<MUST item:Art.24:role_counterparty>>
_Why: Defining the relationship_

<<TEXT>>

## 3. Per-row role chosen (controller / processor / joint controller / third party)

<<MUST item:Art.24:role_chosen>>
_Why: Art.4(7-8) + Art.26_

<<TEXT>>

## 4. Per-row decision basis (who determines means and purposes — EDPB Guidelines 7/2020 test)

<<MUST item:Art.24:role_basis>>
_Why: Defensibility_

<<TEXT>>

## 5. Per-row contract link (DPA Art.28 / Art.26 arrangement / Art.46 transfer mechanism)

<<MUST item:Art.24:role_contract_link>>
_Why: Cross-article_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row review trigger (counterparty service-shape change, M&A)

<<SHOULD item:Art.24:role_review_trigger>>
_Why: Currency_

<<TEXT>>
