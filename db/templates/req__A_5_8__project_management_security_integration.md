---
leaf_id: req:A.5.8:project_management_security_integration
control_ref: A.5.8
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Information Security in Project Management Procedure

<<DOC_CONTROL>>

> A.5.8 requires information security to be integrated into project management across the full lifecycle: initiation, requirements, design/build, pre-go-live assessment, closure handover. The procedure documents gates, deliverables, roles, tiering rules and acceptance criteria. The project register, periodic program review and per-project closure record are sibling leaves

## What this template gives you

This template helps you document how information security is built into every stage of your project management process, from planning through closure, ensuring you meet ISO 27001 requirements.

## When to use it

Use this procedure whenever you manage projects in your environment, and update it whenever your project management or security practices change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this from scratch, as each required section takes 10-15 minutes to write.

## 1. Security gate at project initiation (risk assessment, classification of information, scope of personal data if applicable)

<<MUST item:A.5.8:initiation_gate>>
_Why: 27002:5.8 — integrated at initiation_

<<GUIDANCE>>

<<TEXT>>

## 2. Security requirements captured in project plan / requirements document (functional + non-functional, including data protection)

<<MUST item:A.5.8:requirements>>
_Why: 27002:5.8 — integrated_

<<GUIDANCE>>

<<TEXT>>

## 3. Security assessment before go-live (pen test, control verification, residual-risk acceptance)

<<MUST item:A.5.8:assessment_pre_golive>>
_Why: 27002:5.8 — throughout lifecycle_

<<GUIDANCE>>

<<TEXT>>

## 4. Information security role defined in the project governance (advisor / reviewer / gate-owner with veto authority where warranted)

<<MUST item:A.5.8:role>>
_Why: 27002:5.8 — defined responsibilities_

<<GUIDANCE>>

<<TEXT>>

## 5. Project closure security sign-off step (handover to operations; outstanding-risk transfer documented)

<<MUST item:A.5.8:closure_signoff>>
_Why: 27002:5.8 — closure_

<<GUIDANCE>>

<<TEXT>>

## 6. Risk-acceptance criteria stated (when residual risk forces escalation; named approver per tier)

<<MUST item:A.5.8:acceptance_criteria>>
_Why: 27002:5.8 — risk acceptance per project_

<<GUIDANCE>>

<<TEXT>>

## 7. In-project change control step (scope/security-impact changes during build trigger re-assessment, not late-detection)

<<MUST item:A.5.8:change_control>>
_Why: 27002:5.8 — throughout lifecycle_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Project tiering (which projects need full vs lightweight security review; criteria based on data sensitivity, regulatory scope, third-party exposure)

<<SHOULD item:A.5.8:tiering>>
_Why: 27002:5.8 — proportionality_

<<GUIDANCE>>

<<TEXT>>

### 2. Standard project templates referenced (security sections in initiation pack, requirements template, closure checklist)

<<SHOULD item:A.5.8:templates>>
_Why: Consistency_

<<GUIDANCE>>

<<TEXT>>

### 3. Adaptation for agile/iterative delivery (continuous security touchpoints rather than waterfall gates only)

<<SHOULD item:A.5.8:agile_integration>>
_Why: Modern delivery practice_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
