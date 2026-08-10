---
leaf_id: req:A.8.23:applicable_filtering_scope
control_ref: A.8.23
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Web Filtering Scope

<<DOC_CONTROL>>

> Upstream — which devices + traffic paths are in scope. Corporate-managed devices typically yes. On-network traffic yes. BYOD case-by-case. Off-network corporate-managed via remote-proxy

## What this template gives you

This template helps you clearly define which devices and types of network traffic are included in your web filtering program, making it easier to understand and communicate your security boundaries.

## When to use it

Use this document whenever you need to outline or update the scope of web filtering in your environment. It should be reviewed and refreshed whenever there are changes to your device management or network setup.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three key elements about your devices and network traffic.

## 1. Device classes in scope (corporate-managed / contractor / BYOD with approval)

<<MUST item:A.8.23:scope_devices>>
_Why: 27002:8.23 — access to external websites_

<<GUIDANCE>>

<<TEXT>>

## 2. Traffic paths covered (on-network / VPN / remote-proxy / split-tunnel exclusions)

<<MUST item:A.8.23:scope_paths>>
_Why: Realistic coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (e.g. air-gapped systems with no internet access)

<<MUST item:A.8.23:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new device class, new remote-access pattern)

<<SHOULD item:A.8.23:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
