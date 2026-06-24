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

> Upstream — which devices + traffic paths are in scope. Corporate-managed devices typically yes. On-network traffic yes. BYOD case-by-case. Off-network corporate-managed via remote-proxy

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Device classes in scope (corporate-managed / contractor / BYOD with approval)

<<MUST item:A.8.23:scope_devices>>
_Why: 27002:8.23 — access to external websites_

<<TEXT>>

## 2. Traffic paths covered (on-network / VPN / remote-proxy / split-tunnel exclusions)

<<MUST item:A.8.23:scope_paths>>
_Why: Realistic coverage_

<<TEXT>>

## 3. Exclusion rationale (e.g. air-gapped systems with no internet access)

<<MUST item:A.8.23:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new device class, new remote-access pattern)

<<SHOULD item:A.8.23:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
