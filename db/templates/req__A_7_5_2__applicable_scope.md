---
leaf_id: req:A.7.5.2:applicable_scope
control_ref: A.7.5.2
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Destinations Scope

> The upstream — every jurisdiction where PII may be processed (direct + via subprocessor + via support access + via M&A). Excludes law-enforcement-request destinations documented separately.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Normal-operations destinations (direct + subprocessor + support tier)

<<MUST item:A.7.5.2:scope_normal_operations>>
_Why: §7.5.2 — normal operations_

<<TEXT>>

## 2. Law-enforcement-request handling (not in advance-disclosed list)

<<MUST item:A.7.5.2:scope_law_enforcement>>
_Why: §7.5.2 — cannot be specified in advance_

<<TEXT>>

## 3. Multi-region cloud + backup destinations included

<<MUST item:A.7.5.2:scope_multi_region_cloud>>
_Why: Comprehensiveness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new region / new subprocessor)

<<SHOULD item:A.7.5.2:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
