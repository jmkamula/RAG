---
leaf_id: req:A.8.16:monitoring_activities_procedure
control_ref: A.8.16
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Monitoring Activities Procedure

> A.8.16 requires monitoring for anomalous behaviour with appropriate actions taken. Procedure documents detection methods, alert routing, triage criteria, incident handoff. Per-detection register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Detection methods (signature / anomaly / threat-intel / behavioural / UEBA / hunting)

<<MUST item:A.8.16:detection_methods>>
_Why: 27002:8.16 — anomalous behaviour_

<<TEXT>>

## 2. Alert routing to Security Operations / on-call (severity-tiered)

<<MUST item:A.8.16:alert_routing>>
_Why: 27002:8.16 — appropriate actions taken_

<<TEXT>>

## 3. Triage criteria for separating events from incidents (cross-link to A.5.25)

<<MUST item:A.8.16:triage_criteria>>
_Why: 27002:8.16 — evaluate potential incidents_

<<TEXT>>

## 4. Incident-response handoff (cross-link to A.5.26 register) when triage confirms incident

<<MUST item:A.8.16:incident_handoff>>
_Why: 27002:8.16 — potential incidents_

<<TEXT>>

## 5. SIEM use-case catalogue with coverage map (each use case mapped to detection method + asset class)

<<MUST item:A.8.16:siem_use_cases>>
_Why: Measurable monitoring (Style v2 promotion)_

<<TEXT>>

## 6. Threat-hunting cadence for proactive detection (quarterly minimum for tier-1 assets)

<<MUST item:A.8.16:threat_hunting>>
_Why: Modern maturity (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (Security Operations lead)

<<SHOULD item:A.8.16:owner>>
_Why: Accountability_

<<TEXT>>
