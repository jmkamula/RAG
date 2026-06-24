---
leaf_id: req:A.5.25:triage_decision_record
control_ref: A.5.25
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Per-Event Triage Decision Records

> Every triaged event must close — as a false positive, as a near-miss filed for trend tracking, or by escalation to incident response (A.5.26). The decision record evidences the actual closure: which event, what was decided, the rationale, the authority, and the handoff link where applicable

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Event identifier per record (links back to the triage log row)

<<MUST item:A.5.25:dec_event_ref>>
_Why: 27002:5.25 — documented decision_

<<TEXT>>

## 2. Decision outcome captured (false positive / filed near-miss / escalated to incident)

<<MUST item:A.5.25:dec_outcome>>
_Why: 27002:5.25 — decision_

<<TEXT>>

## 3. Rationale stated (criteria-based reasoning, not just a binary outcome)

<<MUST item:A.5.25:dec_rationale>>
_Why: Audit defensibility_

<<TEXT>>

## 4. Triage decision authority per record (named role or person)

<<MUST item:A.5.25:dec_authority>>
_Why: 27002:5.25 — decision authority_

<<TEXT>>

## 5. Where escalated: handoff reference into A.5.26 incident register

<<MUST item:A.5.25:dec_handoff>>
_Why: 27002:5.25 — incidents_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Timeliness target met (decision within stated triage timeline)

<<SHOULD item:A.5.25:dec_timeliness>>
_Why: Operational discipline_

<<TEXT>>

### 2. Retroactive-review flag where a closed event was later reopened (drives missed-event analysis in the program review)

<<SHOULD item:A.5.25:dec_retro_flag>>
_Why: Closes loop with [[A.5.27]]_

<<TEXT>>
