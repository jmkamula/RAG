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

<<DOC_CONTROL>>

> Per-relationship record documenting whether the org acts as controller, processor, joint controller, or third-party recipient for each processing activity. Art.24's accountability scope is shaped by this role assignment — without explicit documentation, role disputes during audits become unwinnable

<!-- TABLE-COLUMNS leaf:req:Art.24:controller_processor_decision_record -->
<!-- column: item:Art.24:role_activity_id -->
<!-- column: item:Art.24:role_counterparty -->
<!-- column: item:Art.24:role_chosen -->
<!-- column: item:Art.24:role_basis -->
<!-- column: item:Art.24:role_contract_link -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you clearly document your organization's role—such as controller, processor, joint controller, or third-party recipient—for each data processing activity. It makes your responsibilities transparent and helps avoid confusion during audits.

## When to use it

Use this template whenever you need to record your organization's role in a data processing relationship. Update it whenever your processing activities or relationships change, to keep your records accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each processing activity you document. Completing the register from scratch may take 1-2 hours for a small number of activities, and longer as you add more rows.

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

<<GUIDANCE>>

### Role Counterparty

<<MUST item:Art.24:role_counterparty>>
_Why: Defining the relationship_

> _Standard text:_ Per-row counterparty (customer / vendor / partner)

<<GUIDANCE>>

### Role Chosen

<<MUST item:Art.24:role_chosen>>
_Why: Art.4(7-8) + Art.26_

> _Standard text:_ Per-row role chosen (controller / processor / joint controller / third party)

<<GUIDANCE>>

### Role Basis

<<MUST item:Art.24:role_basis>>
_Why: Defensibility_

> _Standard text:_ Per-row decision basis (who determines means and purposes — EDPB Guidelines 7/2020 test)

<<GUIDANCE>>

### Role Contract Link

<<MUST item:Art.24:role_contract_link>>
_Why: Cross-article_

> _Standard text:_ Per-row contract link (DPA Art.28 / Art.26 arrangement / Art.46 transfer mechanism)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Role Review Trigger

<<SHOULD item:Art.24:role_review_trigger>>
_Why: Currency_

> _Standard text:_ Per-row review trigger (counterparty service-shape change, M&A)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
