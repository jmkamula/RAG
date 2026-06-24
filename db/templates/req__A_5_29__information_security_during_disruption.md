---
leaf_id: req:A.5.29:information_security_during_disruption
control_ref: A.5.29
standard_id: ISO27001:2022
evidence_type: plan
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
---

# Information Security During Disruption Plan

> A.5.29 requires planning to maintain information security at an APPROPRIATE LEVEL during disruption — graceful degradation, not all-or-nothing. The plan documents disruption scenarios, controls that must keep operating, fallback / compensating measures, communication paths, and restoration steps. The scenario register, periodic program review and per-activation record are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Disruption scenarios considered (cyber attack [link to A.5.7 threat intel], natural event, supplier failure [link to A.5.21], regulatory action, key-personnel loss)

<<MUST item:A.5.29:scenarios>>
_Why: 27002:5.29 — scenario coverage_

<<TEXT>>

## 2. Security controls that must continue operating during disruption (named explicitly — encryption, access control, audit logging at minimum)

<<MUST item:A.5.29:must_continue>>
_Why: 27002:5.29 — maintain information security_

<<TEXT>>

## 3. Acceptable degradation levels stated (which controls can drop to compensating, which must hold at full — risk-tiered)

<<MUST item:A.5.29:degradation_levels>>
_Why: 27002:5.29 — appropriate level (graceful degradation)_

<<TEXT>>

## 4. Fallback / compensating security measures when primary controls fail (per-control: what replaces it, what residual risk it accepts)

<<MUST item:A.5.29:fallback>>
_Why: 27002:5.29 — appropriate level_

<<TEXT>>

## 5. Communication during disruption (internal personnel, external customers, regulators, suppliers; out-of-band channels when corp comms compromised)

<<MUST item:A.5.29:communication>>
_Why: 27002:5.29 — plan + cross-link to [[A.5.24]]_

<<TEXT>>

## 6. Restoration of normal security controls after disruption ends (sequenced, verified — re-encryption, audit-log replay, access-control reactivation)

<<MUST item:A.5.29:restoration>>
_Why: 27002:5.29 — maintain + cross-link to [[A.5.30]]_

<<TEXT>>

## 7. Activation authority defined (who declares the plan active; who declares it stood down; criteria for each)

<<MUST item:A.5.29:activation_authority>>
_Why: 27002:5.29 — preparation discipline_

<<TEXT>>

## 8. Test schedule for the plan (cadence stated; promoted from SHOULD because untested continuity plans fail when actually needed)

<<MUST item:A.5.29:test_schedule>>
_Why: 27002:5.29 — preparation effectiveness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Integration with the broader Business Continuity Plan (this is the security ANNEX to the BCP — BCP itself is out of scope)

<<SHOULD item:A.5.29:bcp_integration>>
_Why: Coherence with BCP framework_

<<TEXT>>

### 2. Residual-risk register for disruption scenarios where degradation creates accepted exposure (named risk owner per scenario)

<<SHOULD item:A.5.29:residual_risk>>
_Why: Risk discipline_

<<TEXT>>

### 3. Third-party-dependent controls flagged (where the plan relies on supplier action — cross-link to A.5.22 review)

<<SHOULD item:A.5.29:third_party>>
_Why: Cross-link to [[A.5.22]]_

<<TEXT>>
