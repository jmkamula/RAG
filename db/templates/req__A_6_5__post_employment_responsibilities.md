---
leaf_id: req:A.6.5:post_employment_responsibilities
control_ref: A.6.5
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Post-Employment / Role-Change Information Security Responsibilities

<<DOC_CONTROL>>

> A.6.5 requires surviving information security responsibilities after termination or change of employment to be defined, enforced, and communicated. The procedure documents what obligations persist, for how long, how leavers are briefed, how enforcement happens, and how role-change scenarios are handled. The leaver-briefing register, surviving-obligations scope and periodic review are sibling leaves

## What this template gives you

This template helps you clearly define and communicate the information security responsibilities that remain after an employee leaves or changes roles. It ensures everyone understands their ongoing obligations and how these are enforced.

## When to use it

Use this document whenever someone leaves your organization or moves to a different role, and review it whenever your processes or requirements change to keep it up to date.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours drafting this from scratch, plus extra time if you need to create or update registers for tracking briefings and obligations.

## 1. Surviving duties enumerated (confidentiality — typically indefinite; IP protection; non-disparagement; non-poach where lawful; non-compete where lawful)

<<MUST item:A.6.5:surviving_duties>>
_Why: 27002:6.5 — duties that remain valid_

<<GUIDANCE>>

<<TEXT>>

## 2. Duration of each obligation (indefinite for confidentiality; time-limited for non-compete; per-jurisdiction limits where law caps duration)

<<MUST item:A.6.5:duration>>
_Why: 27002:6.5 — remain valid after termination_

<<GUIDANCE>>

<<TEXT>>

## 3. Communication mechanism to leavers (exit briefing with signed acknowledgment; reminder letter; intranet reference) — drives the leaver-briefing register

<<MUST item:A.6.5:communication>>
_Why: 27002:6.5 — communicated_

<<GUIDANCE>>

<<TEXT>>

## 4. Enforcement approach (legal action for breach, breach of contract claims, regulatory referral where misconduct + sectoral notification obligations apply)

<<MUST item:A.6.5:enforcement>>
_Why: 27002:6.5 — enforced_

<<GUIDANCE>>

<<TEXT>>

## 5. Coverage of role change within the organisation, not just termination (joiner-mover-leaver — mover is the typically-missed leg)

<<MUST item:A.6.5:role_change_scope>>
_Why: 27002:6.5 — termination or change of employment_

<<GUIDANCE>>

<<TEXT>>

## 6. Integration with operational offboarding (A.5.11 asset return, A.5.16 identity revocation, A.5.17 credential revocation, A.5.18 access revocation — A.6.5 is the contractual/HR layer; those are the operational layers)

<<MUST item:A.6.5:offboarding_integration>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 7. Named owner of the procedure (HR with InfoSec + Legal partners)

<<MUST item:A.6.5:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exit interview / role-change checklist with info-security touchpoints

<<SHOULD item:A.6.5:exit_interview_checklist>>
_Why: Operational handle_

<<GUIDANCE>>

<<TEXT>>

### 2. Equivalent process for contractors and interested parties (offboarding clause in supplier agreement A.5.20)

<<SHOULD item:A.6.5:contractor_parallel>>
_Why: Comprehensive coverage_

<<GUIDANCE>>

<<TEXT>>

### 3. NDA continuation note — most NDAs survive employment per A.6.6 templates; the exit briefing reinforces this

<<SHOULD item:A.6.5:nda_continuation>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
