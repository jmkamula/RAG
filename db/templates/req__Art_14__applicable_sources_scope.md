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

<<DOC_CONTROL>>

> The upstream — which third-party data sources the org consumes. Documents what counts as 'not from the subject' (public records, affiliates, brokers, analytics enrichment) and where notice can be delayed under Art.14.5 exceptions

## What this template gives you

This template helps you clearly identify and document all third-party data sources your organization relies on, including public records, affiliates, brokers, and analytics providers, and explains when you can delay notifying individuals under GDPR Article 14.5.

## When to use it

Use this whenever your organization collects data from sources other than the individual, and update it whenever your third-party data sources change or new exceptions to notification apply.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe at least three required elements about your third-party sources and any relevant exceptions.

## 1. Source types enumerated (data brokers, public records, affiliates, enrichment vendors, customer lists)

<<MUST item:Art.14:scope_source_types>>
_Why: Coverage proof_

<<GUIDANCE>>

<<TEXT>>

## 2. Art.14.5 exceptions explicitly mapped (proportionate-impossibility / legal-disclosure-restriction / confidentiality obligation)

<<MUST item:Art.14:scope_exception_cases>>
_Why: Art.14.5_

<<GUIDANCE>>

<<TEXT>>

## 3. Out-of-scope sources (e.g. publicly-aggregated stats with no personal data)

<<MUST item:Art.14:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new vendor onboarded, new enrichment line, M&A)

<<SHOULD item:Art.14:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
