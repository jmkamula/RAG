---
leaf_id: req:A.5.23:exit_migration_record
control_ref: A.5.23
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 2
---

# Cloud Service Exit / Migration Records

> A.5.23 requires exit strategies for cloud services and the CSP must support transition + data handover on termination. The exit-migration record evidences the actual execution: trigger captured, migration plan executed, data export and deletion confirmed, transition completed, with authoriser

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Exit trigger captured (termination / replacement / CSP failure / business change)

<<MUST item:A.5.23:exit_trigger>>
_Why: 27002:5.23h_

<<TEXT>>

## 2. Migration plan executed (data export, dependency-rewiring, replacement service stood up)

<<MUST item:A.5.23:exit_migration_plan>>
_Why: 27002:5.23h — transition_

<<TEXT>>

## 3. Data deletion confirmation from the CSP (attestation, log, or audit-trail evidence)

<<MUST item:A.5.23:exit_data_deletion>>
_Why: 27002:5.23 — handover_

<<TEXT>>

## 4. Handover of configuration + data evidence (backup downloaded, config preserved)

<<MUST item:A.5.23:exit_handover>>
_Why: 27002:5.23 — backup/handover_

<<TEXT>>

## 5. Authoriser of the exit (or of the delay + risk acceptance)

<<MUST item:A.5.23:exit_authoriser>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Rolling exit-readiness drill (test exits without actually exiting, for critical services)

<<SHOULD item:A.5.23:exit_drill>>
_Why: Continuity preparedness_

<<TEXT>>

### 2. Per-service exit plan freshness target (re-test on agreement renewal or major service change)

<<SHOULD item:A.5.23:exit_plan_freshness>>
_Why: Drift control_

<<TEXT>>
