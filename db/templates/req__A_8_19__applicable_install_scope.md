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

> Upstream — what counts as 'operational system' for A.8.19 scope. Production vs dev vs test handling (dev/test typically governed differently)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Operational systems enumerated (production + customer-facing + business-critical)

<<MUST item:A.8.19:scope_systems>>
_Why: 27002:8.19 — operational systems_

<<TEXT>>

## 2. Cross-link to A.8.31 environment separation — non-prod governed under separate looser rules

<<MUST item:A.8.19:scope_env_separation>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Exclusion rationale (containerised auto-deployed systems with allowlist enforced at image-build time)

<<MUST item:A.8.19:scope_exclusions>>
_Why: Modern reality_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system class, new deployment pattern)

<<SHOULD item:A.8.19:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
