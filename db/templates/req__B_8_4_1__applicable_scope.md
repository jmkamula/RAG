---
leaf_id: req:B.8.4.1:applicable_scope
control_ref: B.8.4.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Processor Temp-File Scope

<<DOC_CONTROL>>

> The upstream — infrastructure serving customer processing (application tier + database + cache + queue).

## What this template gives you

This template helps you clearly define which parts of your infrastructure are included when handling customer data, focusing on application, database, cache, and queue layers.

## When to use it

Use this document whenever your environment matches certain processing triggers, and update it whenever there are changes to your infrastructure or data handling practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as each required section takes roughly 10 to 15 minutes to draft.

## 1. Customer-serving infrastructure enumerated

<<MUST item:B.8.4.1:scope_infrastructure>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Shared paths where cross-tenant temp file leakage is possible (with mitigation)

<<MUST item:B.8.4.1:scope_shared_paths>>
_Why: Multi-tenant discipline_

<<GUIDANCE>>

<<TEXT>>

## 3. Undeletable-file circumstances with rationale + compensating controls

<<MUST item:B.8.4.1:scope_undeletable>>
_Why: §8.4.1 — circumstances in which cannot be deleted_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new infrastructure)

<<SHOULD item:B.8.4.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
