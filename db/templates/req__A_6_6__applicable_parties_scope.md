---
leaf_id: req:A.6.6:applicable_parties_scope
control_ref: A.6.6
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Parties Scope

> The upstream that drives which template variants exist and which parties require NDA before access. Documents the party categories, the info-class threshold that triggers NDA requirement (some orgs require NDA for all visitors; others only for those touching confidential info)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Party categories enumerated (employees, contractors, suppliers, visitors, M&A counterparties, partners with joint-development)

<<MUST item:A.6.6:scope_party_categories>>
_Why: 27002:6.6 — interested parties_

<<TEXT>>

## 2. Trigger threshold per category (which info-class triggers NDA — typically access to confidential class and above; some orgs all-access)

<<MUST item:A.6.6:scope_trigger_threshold>>
_Why: 27002:6.6 — needs for protection_

<<TEXT>>

## 3. Party-to-variant mapping (employees → light employee NDA; contractors → contractor NDA; suppliers → bilateral; M&A → heavy)

<<MUST item:A.6.6:scope_variant_mapping>>
_Why: 27002:6.6 — proportional_

<<TEXT>>

## 4. Jurisdictions covered (where signatories sign / where info is protected — drives governing-law clause and enforceability)

<<MUST item:A.6.6:scope_jurisdictions>>
_Why: 27002:6.6 — applicable laws_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new party category — e.g. open-source-contributor NDA, gig workers, new geography)

<<SHOULD item:A.6.6:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
