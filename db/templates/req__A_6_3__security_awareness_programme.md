---
leaf_id: req:A.6.3:security_awareness_programme
control_ref: A.6.3
standard_id: ISO27001:2022
evidence_type: training_programme
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 3
---

# Information Security Awareness, Education and Training Programme

> A.6.3 requires personnel and relevant interested parties to receive appropriate awareness, education, and training, with regular updates as policies and procedures change. The programme document describes the audience, curriculum per role, onboarding training, refresh cadence, awareness mechanisms, and training records. The completion register, audience-curriculum scope and periodic programme review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope and audience defined (all personnel + relevant interested parties such as contractors, third parties with access)

<<MUST item:A.6.3:scope_audience>>
_Why: 27002:6.3 — personnel + relevant interested parties_

<<TEXT>>

## 2. Curriculum aligned to job functions (general awareness for all, deeper modules per role — developers, admins, finance, HR, executives)

<<MUST item:A.6.3:curriculum>>
_Why: 27002:6.3 — as relevant for their job function_

<<TEXT>>

## 3. Initial training on onboarding BEFORE access to information assets (gates A.5.18 access grant)

<<MUST item:A.6.3:onboarding>>
_Why: 27002:6.3 — appropriate education and training_

<<TEXT>>

## 4. Refresh cadence (typically annual) plus update on significant policy changes

<<MUST item:A.6.3:refresh_cadence>>
_Why: 27002:6.3 — regular updates_

<<TEXT>>

## 5. Awareness mechanisms beyond formal training (newsletters, phishing simulations, posters, lunch-and-learns, all-hands updates)

<<MUST item:A.6.3:awareness_mechanisms>>
_Why: 27002:6.3 — awareness_

<<TEXT>>

## 6. Training records maintained (who completed what, when) for audit and the completion register leaf

<<MUST item:A.6.3:training_records>>
_Why: Auditability_

<<TEXT>>

## 7. Named owner of the programme (typically Security Awareness Lead within InfoSec; HR partner for delivery logistics)

<<MUST item:A.6.3:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Role-specific deep dives (developers — secure coding from A.8.25; admins — privileged-access discipline from A.8.2; finance — fraud awareness; HR — DSAR handling)

<<SHOULD item:A.6.3:role_specific_deep>>
_Why: Proportionality_

<<TEXT>>

### 2. Effectiveness measurement (quiz pass rates, phishing simulation click rates trend, reporting-rate trend from A.6.8)

<<SHOULD item:A.6.3:effectiveness_metrics>>
_Why: Continuous improvement_

<<TEXT>>

### 3. Programme budget / resource allocation (signals management commitment — under-resourced awareness is a frequent audit finding)

<<SHOULD item:A.6.3:budget>>
_Why: Operational realism_

<<TEXT>>
