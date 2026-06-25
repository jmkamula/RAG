---
leaf_id: req:Art.24:controller_processor_decision_record
control_ref: Art.24
standard_id: GDPR:2016/679
evidence_type: decision_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Controller / Processor Role Decision Record

> Per-relationship record documenting whether the org acts as controller, processor, joint controller, or third-party recipient for each processing activity. Art.24's accountability scope is shaped by this role assignment — without explicit documentation, role disputes during audits become unwinnable

<!-- TABLE-COLUMNS leaf:req:Art.24:controller_processor_decision_record -->
<!-- column: item:Art.24:role_activity_id -->
<!-- column: item:Art.24:role_counterparty -->
<!-- column: item:Art.24:role_chosen -->
<!-- column: item:Art.24:role_basis -->
<!-- column: item:Art.24:role_contract_link -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.24:controller_processor_decision_record -->
| Role Activity Id | Role Counterparty | Role Chosen | Role Basis | Role Contract Link |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.24:controller_processor_decision_record -->

## Column guidance — what to fill in

### Role Activity Id

<<MUST item:Art.24:role_activity_id>>
_Why: Cross-article_

> _Standard text:_ Per-row processing activity (Art.30 RoPA reference)

### Role Counterparty

<<MUST item:Art.24:role_counterparty>>
_Why: Defining the relationship_

> _Standard text:_ Per-row counterparty (customer / vendor / partner)

### Role Chosen

<<MUST item:Art.24:role_chosen>>
_Why: Art.4(7-8) + Art.26_

> _Standard text:_ Per-row role chosen (controller / processor / joint controller / third party)

### Role Basis

<<MUST item:Art.24:role_basis>>
_Why: Defensibility_

> _Standard text:_ Per-row decision basis (who determines means and purposes — EDPB Guidelines 7/2020 test)

### Role Contract Link

<<MUST item:Art.24:role_contract_link>>
_Why: Cross-article_

> _Standard text:_ Per-row contract link (DPA Art.28 / Art.26 arrangement / Art.46 transfer mechanism)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Role Review Trigger

<<SHOULD item:Art.24:role_review_trigger>>
_Why: Currency_

> _Standard text:_ Per-row review trigger (counterparty service-shape change, M&A)
