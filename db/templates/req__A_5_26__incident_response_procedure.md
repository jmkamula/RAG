---
leaf_id: req:A.5.26:incident_response_procedure
control_ref: A.5.26
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 12
should_count: 2
---

# Incident Response Procedure

> A.5.26 requires documented procedures for responding to information security incidents end-to-end. The procedure covers roles, containment, investigation, eradication and recovery, communication, evidence collection, action logging and closure. The incident register, periodic IR-program review and per-incident closure record are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Roles and responsibilities for incident response defined (Incident Manager, security team, comms lead, legal)

<<MUST item:A.5.26:roles>>
_Why: 27002:5.26 — coordination_

<<TEXT>>

## 2. Containment steps documented (immediate actions to limit damage)

<<MUST item:A.5.26:containment>>
_Why: 27002:5.26a_

<<TEXT>>

## 3. Investigation steps defined (root cause analysis, timeline reconstruction)

<<MUST item:A.5.26:investigation>>
_Why: 27002:5.26h_

<<TEXT>>

## 4. Eradication and recovery steps documented (restore secure state)

<<MUST item:A.5.26:eradication>>
_Why: 27002:5.26e_

<<TEXT>>

## 5. Internal and external communication criteria specified (who is informed, when, by whom)

<<MUST item:A.5.26:communication>>
_Why: 27002:5.26c,g_

<<TEXT>>

## 6. Evidence collection step embedded in response (links to A.5.28 evidence-handling procedure)

<<MUST item:A.5.26:evidence_collection>>
_Why: 27002:5.26b_

<<TEXT>>

## 7. All response decisions and actions logged (for evidence preservation and post-incident review)

<<MUST item:A.5.26:action_logging>>
_Why: 27002:5.26f_

<<TEXT>>

## 8. Post-incident review step required after closure (handoff to A.5.27 lessons-learned)

<<MUST item:A.5.26:post_review>>
_Why: 27002:5.26 — closing + § 5.27_

<<TEXT>>

## 9. References incident classification used at triage (links to A.5.25)

<<MUST item:A.5.26:classification_link>>
_Why: 27002:5.25 → 5.26 handoff_

<<TEXT>>

## 10. Severity-tier matrix defined explicitly (P1/P2/P3 or equivalent, with criteria for each tier and the response cadence each triggers)

<<MUST item:A.5.26:severity_tier_matrix>>
_Why: 27002:5.26 — coordination by severity (was implicit on register; promoted to procedure-level definition)_

<<TEXT>>

## 11. Where the incident touches personal data, Art.33 72h notification trigger fires and the breach-notification path activates (links to req:Art.33:breach_notification)

<<MUST item:A.5.26:gdpr_72h_trigger_check>>
_Why: GDPR Art.33.1 / cross-control integration with breach notification_

<<TEXT>>

## 12. Authority/regulator contact list referenced (links to A.5.5) — load-bearing for breach-notification path

<<MUST item:A.5.26:authority_contacts>>
_Why: 27002:5.26 — external notification (promoted SHOULD→MUST Phase C batch 1)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Tabletop or simulation frequency stated (semi-annual or more often); A.5.24 is the formal home for the exercise programme

<<SHOULD item:A.5.26:exercise_freq>>
_Why: Validates the procedure works under pressure; cross-link to A.5.24_

<<TEXT>>

### 2. Nominated incident-handling contact named (for internal + supplier-side reporting)

<<SHOULD item:A.5.26:nominated_contact>>
_Why: 27002:5.26 — coordination_

<<TEXT>>
