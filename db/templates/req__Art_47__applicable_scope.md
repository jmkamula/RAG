---
leaf_id: req:Art.47:applicable_scope
control_ref: Art.47
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable BCR Scope

<<DOC_CONTROL>>

> The upstream — which intra-group flows are covered by BCRs, which entities are bound, third-country expansion handling

## What this template gives you

This template helps you clearly define which parts of your organization and which data flows are covered by Binding Corporate Rules, including how you handle expansion into countries outside the EU.

## When to use it

Use this document whenever your organization’s data processing activities or group structure change in ways that might affect which entities or data flows are covered by your BCRs. Update it as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you’ll need to describe three key aspects of your BCR scope.

## 1. Intra-group flows covered (controller-to-controller / controller-to-processor)

<<MUST item:Art.47:scope_intra_group_flows>>
_Why: Art.47 — group of enterprises_

<<GUIDANCE>>

<<TEXT>>

## 2. Bound entities enumerated (jurisdictions + roles)

<<MUST item:Art.47:scope_entities>>
_Why: Art.47.1.a_

<<GUIDANCE>>

<<TEXT>>

## 3. New-entity onboarding rule — how a newly-acquired or newly-spun-up entity joins the BCRs (or moves to alternative safeguard)

<<MUST item:Art.47:scope_extension>>
_Why: Lifecycle_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (M&A, divestment, regulatory change)

<<SHOULD item:Art.47:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
