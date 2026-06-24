---
leaf_id: req:9.1:applicable_measurement_scope
control_ref: 9.1
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Measurement Scope

> The upstream that bounds the record — which ISMS processes and controls are being measured, what 'good' looks like (target derivation), what's out of scope (controls without a measurable signal)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. ISMS processes in measurement scope (risk-assessment cadence, treatment progress, audit cycle, incident response timeliness, etc.)

<<MUST item:9.1:scope_isms_processes>>
_Why: Clause 9.1 a)_

<<TEXT>>

## 2. Annex A controls in measurement scope (e.g. MFA coverage, patch SLA, awareness completion rate)

<<MUST item:9.1:scope_controls>>
_Why: Clause 9.1 a)_

<<TEXT>>

## 3. Target derivation rationale per metric (regulatory, contractual, internal-baseline, benchmark)

<<MUST item:9.1:scope_target_derivation>>
_Why: Defensible targets_

<<TEXT>>

## 4. Out-of-scope controls (those without measurable signal — usually 'design' or 'governance' controls)

<<MUST item:9.1:scope_exclusions>>
_Why: Defensible bounding_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Scope evolution plan (which un-measured areas are being instrumented next)

<<SHOULD item:9.1:scope_evolution>>
_Why: Maturity trajectory_

<<TEXT>>
