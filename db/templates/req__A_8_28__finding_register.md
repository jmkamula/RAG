---
leaf_id: req:A.8.28:finding_register
control_ref: A.8.28
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Secure Coding Finding Register

> Per-finding tracking — SAST / SCA / review findings, severity, remediation SLA

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-finding unique identifier

<<MUST item:A.8.28:reg_finding_id>>
_Why: Auditability_

<<TEXT>>

## 2. Per-finding source (SAST / SCA / manual review / external researcher)

<<MUST item:A.8.28:reg_source>>
_Why: Identification_

<<TEXT>>

## 3. Per-finding severity

<<MUST item:A.8.28:reg_severity>>
_Why: 27002:8.28 — applied_

<<TEXT>>

## 4. Per-finding SLA due date (matches A.8.8 vulnerability rubric for runtime-exploitable; relaxed for dev-time-only)

<<MUST item:A.8.28:reg_sla_due>>
_Why: Cross-control coherence_

<<TEXT>>

## 5. Per-finding status (open / fixed / accepted-with-expiry)

<<MUST item:A.8.28:reg_status>>
_Why: Continuous evidence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-finding pattern flag (repeating patterns flagged for training feedback)

<<SHOULD item:A.8.28:reg_pattern_signal>>
_Why: Continuous improvement_

<<TEXT>>
