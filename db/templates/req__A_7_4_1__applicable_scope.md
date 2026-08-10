---
leaf_id: req:A.7.4.1:applicable_scope
control_ref: A.7.4.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Collection Contexts Scope

<<DOC_CONTROL>>

> The upstream — which collection surfaces are in scope (forms + cookies + APIs + logs + integrations + third-party enrichment).

## What this template gives you

This template helps you clearly define which data collection methods and sources are included in your privacy scope, such as forms, cookies, APIs, logs, integrations, and third-party data enrichment.

## When to use it

Use this document whenever your organization’s data collection profile matches certain criteria or triggers, and update it as needed to reflect any changes in your collection practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as each required section takes roughly 10-15 minutes to fill out thoughtfully.

## 1. Collection surfaces enumerated (customer forms / employee onboarding / marketing forms / cookies / weblogs / API webhooks / integrations)

<<MUST item:A.7.4.1:scope_surfaces>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Indirect-collection map (technical logs + inferred data + third-party enrichment)

<<MUST item:A.7.4.1:scope_indirect_map>>
_Why: §7.4.1 — indirect_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded surfaces with rationale (e.g. anonymous analytics)

<<MUST item:A.7.4.1:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product surface / new integration)

<<SHOULD item:A.7.4.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
