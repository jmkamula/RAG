---
leaf_id: req:A.7.5.3:applicable_scope
control_ref: A.7.5.3
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Transfer Events Scope

> The upstream — every third-party transfer event that constitutes a recordable transfer (excludes intra-org movements + fully-anonymised aggregate sharing).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Recordable transfer types (batch export / API push / support-driven / M&A / rights-fulfilment cascade)

<<MUST item:A.7.5.3:scope_recordable_events>>
_Why: Coverage_

<<TEXT>>

## 2. Excluded events (intra-org + fully-anonymised aggregates) with rationale

<<MUST item:A.7.5.3:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

## 3. Retention period for transfer records (per A.7.4.7 schedule)

<<MUST item:A.7.5.3:scope_retention_period>>
_Why: §7.5.3 — retention_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new transfer type / new integration)

<<SHOULD item:A.7.5.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
