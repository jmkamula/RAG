---
leaf_id: req:A.5.30:ict_readiness_for_business_continuity
control_ref: A.5.30
standard_id: ISO27001:2022
evidence_type: plan
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# ICT Readiness for Business Continuity Plan

> A.5.30 requires ICT readiness to be planned, implemented, maintained, and tested per business continuity objectives. The plan documents per-service RTO/RPO targets (BIA-derived), recovery procedures, backup arrangements, failover/redundancy provisions, and test cadence. The service register, periodic program review and per-recovery event record are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Recovery Time and Recovery Point Objectives per ICT service (BIA-derived; RTO = how long can it be down; RPO = how much data loss is acceptable)

<<MUST item:A.5.30:rto_rpo>>
_Why: 27002:5.30 — business continuity objectives_

<<TEXT>>

## 2. Recovery procedures documented per ICT service (step-by-step, runbook-style — not 'restart the system' aspirational text)

<<MUST item:A.5.30:recovery_procedures>>
_Why: 27002:5.30 — ICT readiness_

<<TEXT>>

## 3. Backup arrangements (frequency aligned to RPO, retention, geographic separation, restore tested and verified)

<<MUST item:A.5.30:backup>>
_Why: 27002:5.30 — implemented_

<<TEXT>>

## 4. Failover / redundancy arrangements for critical services (active-active / active-passive / cold-standby per service tier)

<<MUST item:A.5.30:failover>>
_Why: 27002:5.30 — readiness_

<<TEXT>>

## 5. Test cadence and records (last test date per service, outcome, gaps identified, remediation status)

<<MUST item:A.5.30:test_records>>
_Why: 27002:5.30 — tested_

<<TEXT>>

## 6. BIA-link explicit (RTO/RPO targets traceable to the Business Impact Assessment — not arbitrarily chosen numbers; cross-link to A.5.29 scenario register)

<<MUST item:A.5.30:bia_link>>
_Why: 27002:5.30 — BIA derivation_

<<TEXT>>

## 7. Alignment with A.5.29 disruption-security plan stated explicitly (this is the ICT mechanical layer; A.5.29 is the security-annex layer; both must reconcile)

<<MUST item:A.5.30:bcp_alignment>>
_Why: 27002:5.30 + cross-link to [[A.5.29]]_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Test scenarios cover BOTH partial-failure AND full-outage cases (most orgs only test partial — auditor-tested concern)

<<SHOULD item:A.5.30:scenario_coverage>>
_Why: Test realism_

<<TEXT>>

### 2. Communication tree for ICT outages (who is informed, escalation thresholds, status-page update cadence)

<<SHOULD item:A.5.30:communication_tree>>
_Why: Coordination_

<<TEXT>>

### 3. Third-party-dependent recovery noted (where recovery relies on supplier action — cross-link to A.5.22 supplier review)

<<SHOULD item:A.5.30:third_party_recovery>>
_Why: Cross-link to [[A.5.22]]_

<<TEXT>>
