---
leaf_id: req:A.8.15:logging_procedure
control_ref: A.8.15
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 1
---

# Logging Procedure

> A.8.15 requires logs produced, stored, protected, analysed. Procedure documents content standards, retention, protection, central collection, analysis integration. Per-source register, applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Required log content per source class (who / what / when / where / outcome / target)

<<MUST item:A.8.15:content_standard>>
_Why: 27002:8.15 — record activities, exceptions, faults_

<<TEXT>>

## 2. Retention period per log class (regulatory + business + investigation horizon — typically 90d hot, 1y cold)

<<MUST item:A.8.15:retention>>
_Why: 27002:8.15 — stored_

<<TEXT>>

## 3. Protection from tampering (append-only / write-once / hashed / off-host SIEM)

<<MUST item:A.8.15:protection>>
_Why: 27002:8.15 — protected_

<<TEXT>>

## 4. Centralised collection (SIEM or log aggregator) — no source-only retention for security-relevant logs

<<MUST item:A.8.15:central_collection>>
_Why: 27002:8.15 — analysed_

<<TEXT>>

## 5. Analysis integration (cross-link to A.8.16 monitoring — passive logging insufficient)

<<MUST item:A.8.15:analysis_link>>
_Why: 27002:8.15 — analysed_

<<TEXT>>

## 6. Time-sync dependency (cross-link to A.8.17 — logs only correlate when clocks aligned)

<<MUST item:A.8.15:time_sync_link>>
_Why: 27002:8.15 — relevant events_

<<TEXT>>

## 7. Log-integrity verification (hash chain or signing) — forensic defensibility

<<MUST item:A.8.15:log_integrity>>
_Why: Forensic-grade (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Legal-hold integration overriding retention

<<SHOULD item:A.8.15:legal_hold>>
_Why: Litigation readiness_

<<TEXT>>
