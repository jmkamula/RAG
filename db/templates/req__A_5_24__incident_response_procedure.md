---
leaf_id: req:A.5.24:incident_response_procedure
control_ref: A.5.24
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 2
must_count: 9
should_count: 3
---

# Information Security Incident Management Procedure

## What this template gives you

The **runbook** for handling security incidents — from detection
through closure. Auditors check that the procedure exists, that
exercises have actually been run (untested plans degrade), and that
real incidents trace through it cleanly. A weak procedure causes a
breach to become a crisis; a good one keeps it an incident.

## When to use it

You're producing the procedure required by **ISO/IEC 27001:2022
A.5.24**. Sits above the operational A.5.25-28 incident family
(triage, response, lessons-learned, evidence). Pairs with the GDPR
Art.33 breach notification process if you handle PII.

## Before you start

- [ ] **A.5.25 Triage Procedure** + **A.5.27 Lessons-Learned
      Procedure** in place
- [ ] **A.5.28 Evidence Handling Procedure** in place (chain-of-
      custody is mandatory from initiation)
- [ ] **A.5.7 Threat Intel** sources connected — feeds detection
- [ ] **A.5.5 Authority Contacts** + **A.5.6 SIG Contacts**
      registers up to date — you need to know who to call
- [ ] **5.3 RACI** + **A.5.2 Roles** — IR roles named per role

## Cross-references

- **A.5.25 Information Security Event Triage** — operational triage
- **A.5.26 Incident Response** — operational response
- **A.5.27 Lessons Learned**
- **A.5.28 Evidence Handling** — chain-of-custody
- **A.5.29 ICT during Disruption** + **A.5.30 ICT Readiness** — BCP
- **GDPR Art.33** — personal-data breach notification < 72h
- **GDPR Art.34** — data-subject notification when high-risk

## Estimated effort

**6-10 hours** for v1; **2 hours** for refresh; **plus** scheduled
exercise cost (annual tabletop minimum, often quarterly).

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Define roles + responsibilities

<<MUST item:A.5.24:roles>>
_Named roles — incidents don't wait for "we'll figure out who's
in charge"._

State the IR team roles: Incident Manager / Lead, deputies (24/7
on-call rotation), comms lead, legal liaison, DPO if PII, exec
sponsor for major incidents. Named stable roles, not "TBD".

**✓ Good**: "IR roles: (1) Incident Manager (on-call rotation: SRE
Lead primary, Security Lead secondary); (2) Deputies (2 in
rotation); (3) Communications Lead — Marketing Director (external)
+ HR Director (internal); (4) Legal Liaison — General Counsel;
(5) DPO — <<DPO_NAME>> (mandatory for PII incidents); (6)
Executive Sponsor — CTO (Sev 1-2), CEO (Sev 1 with public
impact); (7) Subject-matter responders pulled in per scenario
playbook. Roles documented in IR Roster (live document); incumbents
rotate — role definitions stable."

<<TEXT>>

## 2. Define detection + reporting process

<<MUST item:A.5.24:detection>>
_Where reports come from — A.5.25 triage feeds; monitoring/SOC;
user reports; supplier notifications; A.5.7 threat intel._

State the intake sources + the routing rule for each.

**✓ Good**: "Detection + reporting sources: (a) SIEM / monitoring
alerts → automatic triage queue → IR on-call. (b) User reports
(email security@, IT helpdesk, slack channel) → triaged by
SecOps within 30 min. (c) Supplier breach notifications →
auto-routed to IR + DPO if PII. (d) Threat-intel feeds (A.5.7)
trigger proactive scans → IR notified of any hits. (e) Customer
reports → support escalation path to SecOps within 30 min.
(f) Regulator / law enforcement contacts → routed via legal +
exec sponsor."

<<TEXT>>

## 3. Define assessment + classification

<<MUST item:A.5.24:assessment>>
_Severity tiers — drive the response intensity + notification
obligations._

State severity criteria. Each tier has different SLAs, comms,
escalation, regulator-notification triggers.

**✓ Good** (severity matrix):

| Tier | Definition | Examples |
|---|---|---|
| Sev 1 | Confirmed unauthorised access to restricted-class data, OR confirmed personal-data breach with risk to subjects, OR full production outage > 1h | Customer-data exfiltration confirmed; ransomware in production |
| Sev 2 | Suspected confirmed-unauthorised access, OR partial production degradation, OR personal-data event (not yet a "breach") | Unusual data-egress pattern under investigation; auth provider intermittent outage |
| Sev 3 | Security event with no production impact + no confirmed data exposure | Phishing attempt blocked; failed login spike |
| Sev 4 | Informational / observed | Vulnerability disclosure; near-miss |

Assessment criteria run continuously — events can promote/demote
between tiers as the investigation evolves.

<<TEXT>>

## 4. Define response + escalation

<<MUST item:A.5.24:response>>
_Per-severity response playbook + escalation authority._

State who decides what at each tier + the time SLAs.

**✓ Good**: "Per-tier response: (a) Sev 1: IR Manager activates
within 15 min; war-room within 30 min; exec sponsor notified within
1h; comms lead engaged; legal + DPO if PII; status update cadence
30 min until containment. (b) Sev 2: IR Manager assesses within
1h; war-room within 2h if rising; exec sponsor notified within 4h;
cadence 2h. (c) Sev 3: SecOps owns; reported to IR Manager in
daily standup. (d) Sev 4: logged + reviewed weekly. Out-of-hours:
on-call IR Manager has Sev 1-2 authority; can spend up to
£XX,XXX for containment; CEO notified for any over-budget
decision."

<<TEXT>>

## 5. Determine whether a personal-data breach occurred

<<MUST item:A.5.24:personal_data>>
_GDPR alignment — every incident assessed for personal-data
implications. This is the 72h clock trigger._

State the assessment step + who makes the call.

**✓ Good**: "Personal-data breach determination: At every incident
intake (regardless of tier), the IR Manager classifies whether
personal data is in scope (Y/N). If Y: DPO is engaged within 1h
to determine whether the event constitutes a 'breach' under GDPR
Art.4(12) — confidentiality + integrity + availability of personal
data. If breach: the 72h clock starts at the moment of awareness
(not the moment of occurrence); decision recorded with timestamps."

<<TEXT>>

## 6. Define notification process for personal-data breaches

<<MUST item:A.5.24:notification>>
_GDPR Art.33 (supervisory authority < 72h) + Art.34 (data subjects
when high-risk)._

State both Art.33 + Art.34 obligations + the content required
(Art.33(3)).

**✓ Good**: "Personal-data breach notifications: (a) **Art.33 SA
notification** — within 72h of awareness. Format includes per
Art.33(3): nature of breach, categories + approx. numbers of data
subjects, contact details (DPO), likely consequences, measures
taken/proposed. Approver: DPO + Legal. Submitted via ICO online
portal (or relevant EU SA). If incomplete information available,
notify within 72h with what's known + commitment to update.
(b) **Art.34 subject notification** — when breach is likely to
result in high risk to rights/freedoms. Plain-language description,
DPO contact, mitigations, recommended actions. Approver: DPO +
Legal + Comms Lead. Channel: direct (email to affected) primary;
public notice fallback if direct impractical."

<<TEXT>>

## 7. Mandate evidence collection + preservation

<<MUST item:A.5.24:evidence>>
_Chain-of-custody from initiation — late evidence preservation
loses cases._

State the evidence rules + cross-link to A.5.28.

**✓ Good**: "Evidence handling: (a) Chain-of-custody is mandatory
from the moment an event is classified Sev 1-2; recorded in the
A.5.28 evidence register. (b) System logs from affected components
exported within 1h to immutable storage. (c) Volatile evidence
(in-memory, network state) captured per A.5.28 playbooks if
technical capability available + judged proportionate to severity.
(d) Forensic imaging coordinated with external IR partner when
required (Sev 1 ransomware, suspected nation-state). (e) Evidence
retention: 6 years for Sev 1-2 closure records."

<<TEXT>>

## 8. State exercise + test cadence

<<MUST item:A.5.24:exercise_cadence>>
_Untested plans degrade — this is required, not optional._

State the cadence + the test types.

**✓ Good**: "Exercise cadence: (a) Tabletop exercise: quarterly,
covering different scenario types over the year (data breach,
ransomware, insider, supplier compromise). (b) Technical
playbook walkthrough: semi-annual, validating runbooks against
current infrastructure. (c) Full simulation: annual, with
external IR partner participating. (d) Out-of-hours drill: at
least one per year. Exercises produce A.5.24 framework_exercise_
record outputs; gaps feed A.5.27 lessons-learned and 10.1
improvement actions."

<<TEXT>>

## 9. Define external communication paths

<<MUST item:A.5.24:communications>>
_Regulator, legal, PR, law enforcement — pre-built channels prevent
ad-hoc panic decisions._

State per-recipient: who authorises, who sends, what format.

**✓ Good**: "External communication paths: (a) **Regulator (ICO /
EU SA)**: DPO authors + Legal approves; submitted via SA portal;
approver: DPO + Legal. (b) **Affected customers**: Account
Manager + Comms Lead author; Legal review; CEO approval for
Sev 1. (c) **Public statement**: Comms Lead authors; Legal +
CEO + Board approval for Sev 1; channel: customer trust centre +
press release. (d) **Law enforcement**: Legal authors; CEO
approves; channel: written referral to NCA / NCSC / sector CERT.
(e) **Sector / peer disclosure (CISO-share)**: ISMS Manager
authors after immediate response phase; CISO approves; lessons
shared without specifics 3-6 months post-resolution."

<<TEXT>>

---

## Recommended additions

### Lessons-learned cross-link

<<SHOULD item:A.5.24:lessons>>
_A.5.27 hook — every Sev 1-2 incident produces a lessons-learned
output._

State the trigger + the artefact location.

<<TEXT>>

### Authority + sector contact register

<<SHOULD item:A.5.24:contacts>>
_Cross-link to A.5.5 + A.5.6 — your contacts must be current
BEFORE you need them._

State that contacts are maintained + reviewed quarterly.

<<TEXT>>

### Supplier-side incident path

<<SHOULD item:A.5.24:supplier_path>>
_Cross-link to A.5.19 incident_joint_mgmt — bi-directional path._

State that supplier-side incidents flow through the same procedure
with vendor as the source.

<<TEXT>>
