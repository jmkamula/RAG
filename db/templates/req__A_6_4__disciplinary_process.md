---
leaf_id: req:A.6.4:disciplinary_process
control_ref: A.6.4
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Information Security Disciplinary Process

> A.6.4 requires a formalised, communicated disciplinary process for personnel and interested parties who violate information security policy. The procedure documents how violations are surfaced, investigated, decided, communicated, and recorded — typically owned jointly with HR. The case register, applicable-jurisdictions scope and periodic process review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Formalised in writing with HR + Legal review (drives consistent application; ad-hoc disciplinary action is a fairness / employment-tribunal risk)

<<MUST item:A.6.4:formalised>>
_Why: 27002:6.4 — formalised_

<<TEXT>>

## 2. Scope of violations covered (policy breach, negligence, deliberate misuse, repeated non-compliance with awareness training, deliberate circumvention of security controls)

<<MUST item:A.6.4:violation_scope>>
_Why: 27002:6.4 — information security policy violation_

<<TEXT>>

## 3. Investigation step before action, with right of explanation (procedural fairness — drives employment-tribunal defensibility)

<<MUST item:A.6.4:investigation_step>>
_Why: Procedural fairness_

<<TEXT>>

## 4. Decision authority named (HR + line management + Legal as appropriate; escalation to executive for senior personnel)

<<MUST item:A.6.4:decision_authority>>
_Why: Accountability_

<<TEXT>>

## 5. Range of actions defined (verbal warning, written warning, suspension, termination, legal referral, regulator notification where mandatory)

<<MUST item:A.6.4:action_range>>
_Why: 27002:6.4 — take actions_

<<TEXT>>

## 6. Communicated to personnel and interested parties (in employment contract, code of conduct, intranet, awareness training)

<<MUST item:A.6.4:communicated>>
_Why: 27002:6.4 — communicated_

<<TEXT>>

## 7. Named owner of the procedure (HR with InfoSec partner)

<<MUST item:A.6.4:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Consideration of contributory factors (intent, recurrence, impact, awareness training status — was the person trained on what they breached?)

<<SHOULD item:A.6.4:contributory_factors>>
_Why: Proportionality_

<<TEXT>>

### 2. Appeals or review process

<<SHOULD item:A.6.4:appeals>>
_Why: Fair process_

<<TEXT>>

### 3. Cross-link to A.5.36 compliance nonconformity register — disciplinary cases are a particular type of compliance NC and should be tracked in concert

<<SHOULD item:A.6.4:a536_link>>
_Why: Cross-control coherence_

<<TEXT>>
