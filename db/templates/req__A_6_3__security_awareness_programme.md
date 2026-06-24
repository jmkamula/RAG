---
leaf_id: req:A.6.3:security_awareness_programme
control_ref: A.6.3
standard_id: ISO27001:2022
evidence_type: training_programme
trigger_type: universal
template_version: 2
must_count: 7
should_count: 3
---

# Security Awareness, Education and Training Programme

## What this template gives you

The **plan** for how every person who touches your systems learns
what's expected of them. Auditors check that (a) the programme
exists, (b) it actually runs (completion records prove it), (c)
content is current (not 2014 phishing slides), (d) effectiveness
is measured (phishing-sim click-through, attestation refresh).
Strong awareness reduces the most common breach vector — human
error.

## When to use it

You're producing the programme required by **ISO/IEC 27001:2022
A.6.3**. Pairs with the training-completion register sibling
leaf + the audience-curriculum scope.

## Before you start

- [ ] **4.3 ISMS Scope** — drives scope of audience
- [ ] **A.5.1 InfoSec Policy** — the policy this training conveys
- [ ] **5.3 Roles** + **A.5.2 Operational Roles** — drives
      role-specific curriculum
- [ ] **A.5.10 AUP** + **A.5.12 Classification** + **A.5.15
      Access Control** policies — content references these

## Cross-references

- **A.6.1 Screening** (joiner prerequisite)
- **A.6.2 Employment Terms** (training obligation in contract)
- **A.6.4 Disciplinary Process** (failure-to-train consequences)
- **A.6.5 Post-Employment** (NDA + obligations communicated at exit)
- **A.6.6 Confidentiality / NDA**
- **A.5.18 Access Rights Procedure** (joiner training gates access)

## Estimated effort

**1-2 weeks** for v1 (curriculum design + content production +
delivery platform setup); **ongoing operational cost** for
refresh + delivery.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Define scope and audience

<<MUST item:A.6.3:scope_audience>>
_Who has to take this training — and at what depth._

State the audiences + which curricula apply.

**✓ Good** (audience matrix):

| Audience | Required modules |
|---|---|
| All employees | General awareness (1h) + privacy basics (30 min) |
| All contractors with access | General awareness (1h) before access |
| Engineers + admins | Above + secure development (1h) + privileged-access training (30 min) |
| Finance / HR / Legal | Above + classified-data handling (30 min) + records discipline (30 min) |
| Executives | Above + crisis-response briefing (30 min) + regulator-comms briefing (30 min) |
| DPO + privacy team | Above + GDPR deep-dive + EDPB updates (4h annually) |
| Third-party with sustained access | General awareness adapted for non-employees + NDA briefing (1h before access) |

<<TEXT>>

## 2. Align curriculum to job functions

<<MUST item:A.6.3:curriculum>>
_Role-specific content — generic training degrades for technical
roles + executives._

State the per-role module list + delivery format.

**✓ Good**: "Curriculum modules: (a) **General awareness** —
phishing recognition, password hygiene, classified-data handling,
incident reporting, policy overview. Delivery: e-learning + annual
refresh; 1h. (b) **Privacy basics** — GDPR principles, data-
subject rights, breach reporting, PII recognition. 30 min.
(c) **Secure development** (engineers) — OWASP Top 10, secure
SDLC checkpoints, secret-management, dependency hygiene. 1h.
(d) **Privileged access** (admins) — least-privilege discipline,
break-glass, A.8.2 PAM rules. 30 min. (e) **Crisis response**
(executives) — IR escalation, communication discipline, regulator
posture. 30 min. (f) **GDPR deep-dive** (DPO + privacy team) —
4h annually."

<<TEXT>>

## 3. Train at onboarding BEFORE access granted

<<MUST item:A.6.3:onboarding>>
_Onboarding gate — training is a precondition for the A.5.18
access grant._

State the gating mechanism.

**✓ Good**: "Onboarding gate: New-joiner identity (per A.5.16) is
created in 'pre-trained' state with no application access. General
awareness + privacy basics + role-specific module must be
completed within 5 business days of start. A.5.18 provisioning is
blocked at the identity-state check until completion. Manager
attestation of completion required to unlock access. Contractor
joiners follow the same gate with NDA acknowledgement (A.6.6)
included."

<<TEXT>>

## 4. State refresh cadence

<<MUST item:A.6.3:refresh_cadence>>
_Annual minimum + event-triggered._

State cadence + triggers.

**✓ Good**: "Refresh cadence: (a) Annual: all modules refreshed at
content level (updated phishing examples, recent regulator
guidance, current threat landscape); all personnel complete
refresh within 30 days of release. (b) Event-triggered: significant
policy change → targeted refresh on the affected topic (e.g. AUP
revision triggers 15-min focused module). (c) Role-change-
triggered: A.5.18 mover lifecycle includes verifying the new role's
modules are current; gaps closed before access change."

<<TEXT>>

## 5. Provide awareness mechanisms beyond formal training

<<MUST item:A.6.3:awareness_mechanisms>>
_Training is a touchpoint; awareness is a habit — mechanisms
sustain it._

State the always-on channels.

**✓ Good**: "Awareness mechanisms: (a) Phishing simulations —
monthly automated campaigns rotating tactics; click-rates reported
+ trained-on individually. (b) Security newsletter — monthly,
covering recent threats, internal incidents (sanitised), policy
updates. (c) Channel #security-aware on Slack — open Q&A + tip
of the week. (d) Lunch-and-learn — quarterly deep-dives on
topics of interest (open to all). (e) All-hands updates —
quarterly SecOps slot at company all-hands. (f) Posters /
intranet banners — physical (where applicable) + digital reminders
in collaboration tools."

<<TEXT>>

## 6. Maintain training records

<<MUST item:A.6.3:training_records>>
_Who took what, when — audit evidence + drives the completion
register leaf._

State the records system + retention.

**✓ Good**: "Records maintenance: LMS captures per-person
completion records: module ID, completion date, score/result.
Records exported to the A.6.3 training_completion_register sibling
leaf monthly. Retention: 6 years after employment ends (per A.5.33
records retention). Access: managers see their own team; ISMS
Manager + DPO see all; subject access on request per GDPR Art.15."

<<TEXT>>

## 7. Name programme owner

<<MUST item:A.6.3:owner>>
_Accountability — every controlled doc needs a named owner._

The Security Awareness Lead (typically within InfoSec) owns
content; HR partner owns delivery logistics + manager engagement.

**✓ Good**: "Programme owner: Security Awareness Lead
(<<AWARENESS_LEAD_NAME>>) — owns content, vendor management for
LMS / phishing-sim, programme effectiveness metrics. HR Partner
(<<HR_PARTNER_NAME>>) — owns delivery logistics (joiner
enrolment, manager prompts, escalation on overdue). Sponsor:
ISMS Manager + Head of People."

<<TEXT>>

---

## Recommended additions

### Role-specific deep-dives documented

<<SHOULD item:A.6.3:role_specific_deep>>
_For high-risk roles, depth above the standard role module._

State the deep-dive programmes for engineers (secure SDLC), admins
(PAM), DPO (GDPR), execs (crisis posture).

<<TEXT>>

### Effectiveness metrics

<<SHOULD item:A.6.3:effectiveness_metrics>>
_Measure outcomes, not just completion._

State the metrics: phishing-sim click rate trend, security-question
results, reporting rate, attestation refresh on-time rate.

<<TEXT>>

### Programme budget

<<SHOULD item:A.6.3:budget>>
_Programme sustainability — budget signals organisational
commitment._

State the annual budget for content, LMS, phishing-sim,
lunch-and-learns.

<<TEXT>>
