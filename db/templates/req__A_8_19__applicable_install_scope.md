---
leaf_id: req:A.8.19:applicable_install_scope
control_ref: A.8.19
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Installation Scope

<<DOC_CONTROL>>

> Upstream — what counts as 'operational system' for A.8.19 scope. Production vs dev vs test handling (dev/test typically governed differently)

## What this template gives you

This template helps you clearly define which parts of your IT environment count as an 'operational system' for compliance purposes, making it easier to separate production from development and test systems.

## When to use it

Use this document whenever you need to clarify the scope of your operational systems for compliance, and update it whenever there are changes to your environment or how systems are managed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and possibly add a recommended one.

## 1. Operational systems enumerated (production + customer-facing + business-critical)

<<MUST item:A.8.19:scope_systems>>
_Why: 27002:8.19 — operational systems_

<<GUIDANCE>>

<<TEXT>>

## 2. Cross-link to A.8.31 environment separation — non-prod governed under separate looser rules

<<MUST item:A.8.19:scope_env_separation>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (containerised auto-deployed systems with allowlist enforced at image-build time)

<<MUST item:A.8.19:scope_exclusions>>
_Why: Modern reality_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system class, new deployment pattern)

<<SHOULD item:A.8.19:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
