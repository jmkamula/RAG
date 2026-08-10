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

<<DOC_CONTROL>>

> The upstream — every third-party transfer event that constitutes a recordable transfer (excludes intra-org movements + fully-anonymised aggregate sharing).

## What this template gives you

This template helps you clearly define which third-party data transfer events are considered recordable, making it easier to stay aligned with privacy standards and avoid confusion about what needs to be tracked.

## When to use it

Use this document whenever your organization is involved in data transfers with external parties that may trigger privacy compliance requirements. Update it as needed when your data sharing practices or partners change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required elements and optionally add one recommended detail.

## 1. Recordable transfer types (batch export / API push / support-driven / M&A / rights-fulfilment cascade)

<<MUST item:A.7.5.3:scope_recordable_events>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Excluded events (intra-org + fully-anonymised aggregates) with rationale

<<MUST item:A.7.5.3:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

## 3. Retention period for transfer records (per A.7.4.7 schedule)

<<MUST item:A.7.5.3:scope_retention_period>>
_Why: §7.5.3 — retention_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new transfer type / new integration)

<<SHOULD item:A.7.5.3:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
