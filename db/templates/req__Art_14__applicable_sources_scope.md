---
leaf_id: req:Art.14:applicable_sources_scope
control_ref: Art.14
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Third-Party Sources Scope

> The upstream — which third-party data sources the org consumes. Documents what counts as 'not from the subject' (public records, affiliates, brokers, analytics enrichment) and where notice can be delayed under Art.14.5 exceptions

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Source types enumerated (data brokers, public records, affiliates, enrichment vendors, customer lists)

<<MUST item:Art.14:scope_source_types>>
_Why: Coverage proof_

<<TEXT>>

## 2. Art.14.5 exceptions explicitly mapped (proportionate-impossibility / legal-disclosure-restriction / confidentiality obligation)

<<MUST item:Art.14:scope_exception_cases>>
_Why: Art.14.5_

<<TEXT>>

## 3. Out-of-scope sources (e.g. publicly-aggregated stats with no personal data)

<<MUST item:Art.14:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new vendor onboarded, new enrichment line, M&A)

<<SHOULD item:Art.14:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
