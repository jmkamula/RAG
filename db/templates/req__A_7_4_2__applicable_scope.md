---
leaf_id: req:A.7.4.2:applicable_scope
control_ref: A.7.4.2
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processing Operations Scope

> The upstream — all internal + integration processing operations that touch PII. Excludes fully-anonymised data operations.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Internal processing operations enumerated (application queries / reports / dashboards / ML pipelines / exports)

<<MUST item:A.7.4.2:scope_internal_operations>>
_Why: Coverage_

<<TEXT>>

## 2. Integration processing (webhooks + third-party enrichment + backup + DR)

<<MUST item:A.7.4.2:scope_integrations>>
_Why: Coverage_

<<TEXT>>

## 3. Excluded operations (anonymised / aggregate) with rationale

<<MUST item:A.7.4.2:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product feature / new analytics pipeline)

<<SHOULD item:A.7.4.2:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
