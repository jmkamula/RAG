---
leaf_id: req:A.7.4:physical_security_monitoring
control_ref: A.7.4
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Physical Security Monitoring Procedure

> A.7.4 requires premises to be continuously monitored for unauthorized physical access. The procedure documents monitoring scope, detection systems, continuous-monitoring approach, alert response, and retention. The monitoring event register, applicable-monitoring scope and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Monitoring scope stated (premises perimeter, secure areas, equipment rooms, entry/exit points)

<<MUST item:A.7.4:monitoring_scope>>
_Why: 27002:7.4 — premises monitored_

<<TEXT>>

## 2. Detection systems listed (CCTV, intrusion detection, access control logs, alarms, motion sensors)

<<MUST item:A.7.4:detection_systems>>
_Why: 27002:7.4 — unauthorized access_

<<TEXT>>

## 3. 24/7 / continuous monitoring approach (manned SOC, automated with SOC review, hybrid)

<<MUST item:A.7.4:continuous_24x7>>
_Why: 27002:7.4 — continuously monitored_

<<TEXT>>

## 4. Alert response procedure (who is notified, escalation, on-site response timing)

<<MUST item:A.7.4:alert_response>>
_Why: 27002:7.4 — monitored_

<<TEXT>>

## 5. Retention of footage and access logs (period per regulatory requirement, secure storage)

<<MUST item:A.7.4:retention>>
_Why: 27002:7.4 — retention_

<<TEXT>>

## 6. Integration with SIEM / A.5.26 incident response (physical events route to the same triage)

<<MUST item:A.7.4:siem_integration>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Privacy considerations for monitoring of personnel (GDPR / employment law compliance)

<<SHOULD item:A.7.4:privacy_balance>>
_Why: Legal balance_

<<TEXT>>
