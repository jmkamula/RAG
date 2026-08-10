---
leaf_id: req:A.5.25:event_assessment_procedure
control_ref: A.5.25
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
---

# Security Event Assessment and Triage Procedure

<<DOC_CONTROL>>

> A.5.25 requires the organization to assess information security events and decide whether to categorise them as incidents. The procedure documents detection sources, assessment criteria, decision authority, classification scale and handoff to incident response (A.5.26). The event triage log, periodic triage-program review and per-event triage decision record are sibling leaves

## What this template gives you

This template helps you document how your organization assesses and categorizes security events, ensuring you have a clear process for deciding when an event becomes an incident and how to handle it.

## When to use it

Use this procedure whenever you need to evaluate information security events in your environment, and update it whenever your assessment process or decision criteria change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this from scratch, as you'll need to cover several required elements and provide details for each step in your assessment process.

## 1. Detection sources enumerated (monitoring, user reports, third parties)

<<MUST item:A.5.25:detection_sources>>
_Why: 27002:5.25 — events_

<<GUIDANCE>>

<<TEXT>>

## 2. Assessment criteria (impact, scope, certainty) for classifying severity

<<MUST item:A.5.25:assessment_criteria>>
_Why: 27002:5.25 — categorising_

<<GUIDANCE>>

<<TEXT>>

## 3. Decision authority named (who decides event vs incident vs false positive)

<<MUST item:A.5.25:decision_authority>>
_Why: 27002:5.25 — decision_

<<GUIDANCE>>

<<TEXT>>

## 4. Classification scale used (event, near-miss, incident with severity)

<<MUST item:A.5.25:classification_scale>>
_Why: 27002:5.25 — agreed classification scheme_

<<GUIDANCE>>

<<TEXT>>

## 5. Timeline for triage decision after detection

<<MUST item:A.5.25:triage_timeline>>
_Why: 27002:5.25 — assess and decide_

<<GUIDANCE>>

<<TEXT>>

## 6. Handoff to incident response process (A.5.26) when classified as incident

<<MUST item:A.5.25:handoff>>
_Why: 27002:5.25 — incidents_

<<GUIDANCE>>

<<TEXT>>

## 7. Correlation / aggregation of events for trend identification (links to A.8.16 monitoring)

<<MUST item:A.5.25:correlation>>
_Why: 27002:5.25 — correlation_

<<GUIDANCE>>

<<TEXT>>

## 8. Competent personnel given access to event/incident/weakness records

<<MUST item:A.5.25:competent_access>>
_Why: 27002:5.25 — competent personnel_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Severity matrix with concrete examples

<<SHOULD item:A.5.25:severity_matrix>>
_Why: Consistency across triagers_

<<GUIDANCE>>

<<TEXT>>

### 2. Automation or playbook references for common event types

<<SHOULD item:A.5.25:automation>>
_Why: Scalability_

<<GUIDANCE>>

<<TEXT>>

### 3. Considers who may need to be informed (legal, operational, comms) even at triage stage

<<SHOULD item:A.5.25:legal_advisory>>
_Why: 27002:5.25 — informing_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
