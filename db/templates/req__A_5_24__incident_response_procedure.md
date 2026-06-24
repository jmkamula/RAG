---
leaf_id: req:A.5.24:incident_response_procedure
control_ref: A.5.24
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 9
should_count: 3
---

# Information Security Incident Management Planning Framework

> A.5.24 requires the org to plan and prepare for incidents — not just react when they happen. The framework documents roles, authorities, detection-and-reporting paths, classification criteria, escalation thresholds, communication paths (internal + external + regulator), evidence-handling integration (A.5.28), lessons-learned integration (A.5.27), and exercise/test cadence. The IR team register, periodic program review and per-exercise activation record are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Roles and responsibilities defined (IR lead, deputies, comms lead, legal liaison, exec sponsor; named individuals or stable roles, not 'TBD')

<<MUST item:A.5.24:roles>>
_Why: 27002:5.24a_

<<TEXT>>

## 2. Detection and reporting process (where reports come from — A.5.25 triage, monitoring/SOC, user reports, supplier notifications, A.5.7 threat intel)

<<MUST item:A.5.24:detection>>
_Why: 27002:5.24b + cross-link to [[A.5.25]]_

<<TEXT>>

## 3. Incident assessment and classification criteria (severity tiers; what triggers each tier; alignment with A.5.25 triage decision criteria)

<<MUST item:A.5.24:assessment>>
_Why: 27002:5.24c + cross-link to [[A.5.25]]_

<<TEXT>>

## 4. Response and escalation procedures (decision authority per severity tier; out-of-hours handling; cross-team coordination)

<<MUST item:A.5.24:response>>
_Why: 27002:5.24d_

<<TEXT>>

## 5. Step to determine if personal data breach occurred (DPIA-aware classification, controller/processor analysis)

<<MUST item:A.5.24:personal_data>>
_Why: GDPR Art.33 alignment — 72hr notification trigger_

<<TEXT>>

## 6. Notification process for personal data breaches (supervisory authority < 72h; data subjects when high-risk; notification content per Art.33(3))

<<MUST item:A.5.24:notification>>
_Why: GDPR Art.33/34 alignment_

<<TEXT>>

## 7. Evidence collection and preservation requirements (cross-link to A.5.28 evidence-handling procedure; chain-of-custody mandatory from initiation)

<<MUST item:A.5.24:evidence>>
_Why: 27002:5.24e + cross-link to [[A.5.28]]_

<<TEXT>>

## 8. Exercise / test cadence stated explicitly (annual minimum, more frequent for high-risk org; promoted from SHOULD because untested plans degrade)

<<MUST item:A.5.24:exercise_cadence>>
_Why: 27002:5.24 — preparation_

<<TEXT>>

## 9. External communication paths (regulator, legal, PR, law enforcement) with thresholds and named owners

<<MUST item:A.5.24:communications>>
_Why: 27002:5.24 — communication_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Lessons learned process (cross-link to A.5.27 lessons register; how lessons feed back into framework revisions)

<<SHOULD item:A.5.24:lessons>>
_Why: Closing loop with [[A.5.27]]_

<<TEXT>>

### 2. External contact list maintained (regulator, legal counsel, PR firm, forensic specialists, CSP support) with rotation review

<<SHOULD item:A.5.24:contacts>>
_Why: Response effectiveness_

<<TEXT>>

### 3. Supplier-driven incident path documented (A.5.21 supplier-side incidents trigger our framework even when we're not directly hit)

<<SHOULD item:A.5.24:supplier_path>>
_Why: Cross-link to [[A.5.21]]_

<<TEXT>>
