---
leaf_id: req:10.2:applicable_nc_sources_scope
control_ref: 10.2
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable NC Sources Scope

> The upstream that bounds the register — which signal sources qualify a finding as a 'nonconformity' (vs an observation that routes to 10.1, or an incident that routes to A.5.26)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Audit sources in scope (9.2 internal audit major + minor NCs; surveillance + re-cert audit NCs; second-party customer-audit NCs)

<<MUST item:10.2:scope_audit_sources>>
_Why: Clause 10.2 — react_

<<TEXT>>

## 2. Operational sources in scope (incident lessons that surface a process gap, measurement breaches indicating control failure)

<<MUST item:10.2:scope_operational_sources>>
_Why: Coverage_

<<TEXT>>

## 3. External sources in scope (regulator findings, customer complaints, supplier breaches affecting our scope)

<<MUST item:10.2:scope_external_sources>>
_Why: Coverage_

<<TEXT>>

## 4. 10.1 boundary — observations / opportunities / non-conforming-but-acceptable findings route to 10.1, NCs route here

<<MUST item:10.2:scope_10_1_boundary>>
_Why: Cross-clause coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Severity tiers (major NC blocks certification; minor NC needs action plan; observation = 10.1 territory)

<<SHOULD item:10.2:scope_severity_tiers>>
_Why: Operational discipline_

<<TEXT>>
