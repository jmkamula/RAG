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
---

# Interested Parties and Requirements Register

> Clause 4.2 requires the organization to determine interested parties relevant to the ISMS and their requirements. The register is the canonical artefact — party rows with category, requirements, ISMS treatment decision, owner. Sibling leaves: stakeholder identification framework, applicable-domains scope, program review

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Interested parties listed per row (regulators, customers, suppliers, personnel, shareholders, communities)

<<MUST item:4.2:parties_listed>>
_Why: Clause 4.2 — interested parties relevant_

<<TEXT>>

## 2. Requirements per party documented (legal, regulatory, contractual, business expectations)

<<MUST item:4.2:requirements>>
_Why: Clause 4.2 — relevant requirements_

<<TEXT>>

## 3. Which requirements the ISMS will address per party (and how)

<<MUST item:4.2:addressed>>
_Why: Clause 4.2 — addressed through the ISMS_

<<TEXT>>

## 4. Named owner of the register

<<MUST item:4.2:owner>>
_Why: Accountability_

<<TEXT>>

## 5. Last assessment date per party row (drives staleness detection)

<<MUST item:4.2:reg_last_assessed>>
_Why: Currency_

<<TEXT>>

## 6. Per-row link to the ISMS scope (4.3) artefacts that address the party

<<MUST item:4.2:reg_scope_link>>
_Why: Cross-clause coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-party priority tag (contractually-bound vs voluntary commitment)

<<SHOULD item:4.2:reg_priority>>
_Why: Risk and priority clarity_

<<TEXT>>
