---
leaf_id: req:A.7.12:applicable_runs_scope
control_ref: A.7.12
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Cabling Runs Scope

<<DOC_CONTROL>>

> The upstream — which cabling runs are in scope, what drives protection levels, exclusions

## What this template gives you

This template helps you clearly define which cabling runs are included in your security program, what protection levels apply, and any exclusions. It's useful for understanding and documenting your cabling scope for compliance.

## When to use it

Use this document whenever you need to clarify the cabling runs that are part of your environment, and update it whenever there are changes to your cabling or protection requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and possibly one recommended detail.

## 1. Sites in scope (drawn from A.7.1)

<<MUST item:A.7.12:scope_sites>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Run classes (LAN backbone, intra-rack, perimeter, external/landlord-controlled)

<<MUST item:A.7.12:scope_run_classes>>
_Why: 27002:7.12 — protected_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusions (carrier-provided fibre — provider responsibility for protection)

<<MUST item:A.7.12:scope_exclusions>>
_Why: 27002:7.12 — applicability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (network refresh, new site)

<<SHOULD item:A.7.12:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
