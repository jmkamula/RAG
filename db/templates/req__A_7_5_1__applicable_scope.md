---
leaf_id: req:A.7.5.1:applicable_scope
control_ref: A.7.5.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Cross-Jurisdiction Transfers Scope

<<DOC_CONTROL>>

> The upstream — every PII flow that crosses a jurisdictional boundary. Includes internal cross-border transfers within multi-region org.

## What this template gives you

This template helps you clearly define and document every instance where personal data crosses jurisdictional boundaries, including transfers within your organization across different regions. It's designed to support compliance with privacy standards like ISO 27701.

## When to use it

Use this template whenever your organization handles personal data that moves between countries or regions, especially if your operations span multiple jurisdictions. Update it as needed whenever your data flows or organizational structure change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this template from scratch, as each required section takes roughly 10 to 15 minutes to fill out thoughtfully.

## 1. PII flow inventory — every flow map row (from A.7.5.2) with jurisdiction pair

<<MUST item:A.7.5.1:scope_flow_inventory>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Internal cross-region transfers (multi-region cloud + branch offices)

<<MUST item:A.7.5.1:scope_internal_transfers>>
_Why: Comprehensiveness_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded flows (intra-jurisdiction) with rationale

<<MUST item:A.7.5.1:scope_exclusions>>
_Why: §7.5.1 NOTE_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new region / new processor / M&A)

<<SHOULD item:A.7.5.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
