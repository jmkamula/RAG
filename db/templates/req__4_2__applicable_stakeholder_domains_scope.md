---
leaf_id: req:4.2:applicable_stakeholder_domains_scope
control_ref: 4.2
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Stakeholder Domains Scope

> The upstream that bounds the framework. Documents which stakeholder categories are in scope, the legal vs voluntary split, and what is explicitly excluded with rationale

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Stakeholder categories in scope enumerated (mirrors framework categories or narrows them)

<<MUST item:4.2:scope_categories>>
_Why: Coverage proof_

<<TEXT>>

## 2. Distinction between legal/regulatory requirements and voluntary commitments stated at scope level

<<MUST item:4.2:legal_voluntary>>
_Why: Risk and priority clarity_

<<TEXT>>

## 3. Exclusions stated explicitly with rationale (e.g. retail-consumer party type excluded for a B2B-only org)

<<MUST item:4.2:scope_exclusions>>
_Why: Defensible bounding_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new contract type, new regulator in scope, M&A)

<<SHOULD item:4.2:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
