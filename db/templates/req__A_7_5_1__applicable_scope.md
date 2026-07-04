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

> The upstream — every PII flow that crosses a jurisdictional boundary. Includes internal cross-border transfers within multi-region org.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. PII flow inventory — every flow map row (from A.7.5.2) with jurisdiction pair

<<MUST item:A.7.5.1:scope_flow_inventory>>
_Why: Coverage_

<<TEXT>>

## 2. Internal cross-region transfers (multi-region cloud + branch offices)

<<MUST item:A.7.5.1:scope_internal_transfers>>
_Why: Comprehensiveness_

<<TEXT>>

## 3. Excluded flows (intra-jurisdiction) with rationale

<<MUST item:A.7.5.1:scope_exclusions>>
_Why: §7.5.1 NOTE_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new region / new processor / M&A)

<<SHOULD item:A.7.5.1:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
