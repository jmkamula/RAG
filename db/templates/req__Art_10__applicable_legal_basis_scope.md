---
leaf_id: req:Art.10:applicable_legal_basis_scope
control_ref: Art.10
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Legal Basis Scope (Member State Law)

> The upstream — Member State law citations authorising the org's criminal-data processing. Documents which laws have been mapped, what safeguards each law mandates, where the org is the 'official authority' vs operating under specific authorisation

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Member State law register — every applicable MS law cited with title, article, scope

<<MUST item:Art.10:scope_ms_law_register>>
_Why: Art.10_

<<TEXT>>

## 2. Official-authority vs specific-authorisation split — which activities fall in each

<<MUST item:Art.10:scope_authority_vs_authorised>>
_Why: Art.10_

<<TEXT>>

## 3. Out-of-scope activities (e.g. journalistic / non-EU jurisdictions)

<<MUST item:Art.10:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new MS entry, new business line attracting Art.10 data)

<<SHOULD item:Art.10:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
