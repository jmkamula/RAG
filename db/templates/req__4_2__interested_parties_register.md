---
leaf_id: req:4.2:interested_parties_register
control_ref: 4.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Interested Parties and Requirements Register

<<DOC_CONTROL>>

> Clause 4.2 requires the organization to determine interested parties relevant to the ISMS and their requirements. The register is the canonical artefact — party rows with category, requirements, ISMS treatment decision, owner. Sibling leaves: stakeholder identification framework, applicable-domains scope, program review

<!-- TABLE-COLUMNS leaf:req:4.2:interested_parties_register -->
<!-- column: item:4.2:parties_listed -->
<!-- column: item:4.2:requirements -->
<!-- column: item:4.2:addressed -->
<!-- column: item:4.2:owner -->
<!-- column: item:4.2:reg_last_assessed -->
<!-- column: item:4.2:reg_scope_link -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you clearly identify all relevant interested parties and their requirements for your information security management system, making it easier to track responsibilities and ensure compliance with ISO 27001.

## When to use it

Use this register whenever you need to document or review who your interested parties are and what they require from your ISMS. Plan to update it about once a year to keep information current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes to complete the required elements for your initial set of interested parties, with additional time needed as you add more parties or details.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:4.2:interested_parties_register -->
| Parties Listed | Requirements | Addressed | Owner | Reg Last Assessed | Reg Scope Link |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:4.2:interested_parties_register -->

## Column guidance — what to fill in

### Parties Listed

<<MUST item:4.2:parties_listed>>
_Why: Clause 4.2 — interested parties relevant_

> _Standard text:_ Interested parties listed per row (regulators, customers, suppliers, personnel, shareholders, communities)

<<GUIDANCE>>

### Requirements

<<MUST item:4.2:requirements>>
_Why: Clause 4.2 — relevant requirements_

> _Standard text:_ Requirements per party documented (legal, regulatory, contractual, business expectations)

<<GUIDANCE>>

### Addressed

<<MUST item:4.2:addressed>>
_Why: Clause 4.2 — addressed through the ISMS_

> _Standard text:_ Which requirements the ISMS will address per party (and how)

<<GUIDANCE>>

### Owner

<<MUST item:4.2:owner>>
_Why: Accountability_

> _Standard text:_ Named owner of the register

<<GUIDANCE>>

### Reg Last Assessed

<<MUST item:4.2:reg_last_assessed>>
_Why: Currency_

> _Standard text:_ Last assessment date per party row (drives staleness detection)

<<GUIDANCE>>

### Reg Scope Link

<<MUST item:4.2:reg_scope_link>>
_Why: Cross-clause coherence_

> _Standard text:_ Per-row link to the ISMS scope (4.3) artefacts that address the party

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Priority

<<SHOULD item:4.2:reg_priority>>
_Why: Risk and priority clarity_

> _Standard text:_ Per-party priority tag (contractually-bound vs voluntary commitment)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
