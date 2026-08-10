---
leaf_id: req:Art.45:applicable_scope
control_ref: Art.45
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Adequacy Scope

<<DOC_CONTROL>>

> The upstream — which destinations covered by Art.45.3 decisions the org actually relies on + recipient-eligibility verification approach

## What this template gives you

This template helps you clearly document which countries or destinations your organization relies on for data transfers under adequacy decisions, and how you verify that recipients are eligible.

## When to use it

Use this document whenever your organization relies on adequacy decisions for international data transfers, and update it as your transfer practices or recipient eligibility checks change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and possibly one recommended element.

## 1. Adequate destinations in use (e.g. UK, Japan, US-DPF certified)

<<MUST item:Art.45:scope_destinations>>
_Why: Art.45.3_

<<GUIDANCE>>

<<TEXT>>

## 2. Eligibility-proof method per destination (Commission register / DPF list / etc.)

<<MUST item:Art.45:scope_eligibility_proof>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

## 3. Destinations specifically NOT relying on adequacy (fall to Art.46/49)

<<MUST item:Art.45:scope_excluded>>
_Why: Defensible bounding_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new adequacy decision, repeal, vendor change of certification)

<<SHOULD item:Art.45:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
