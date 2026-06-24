---
leaf_id: req:A.5.26:incident_register
control_ref: A.5.26
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 90
template_version: 1
must_count: 5
should_count: 2
---

# Information Security Incident Register

> A.5.26 expects incidents to be tracked from detection through closure, with the trail of actions preserved. The incident register is the live master record — every incident, its severity, status, owner, and the key lifecycle dates (detection, containment, eradication, recovery, closure) — feeding the periodic IR-program review and the per-incident closure records. Fast-data freshness (90d) per Style v2 — an incident register that's a year stale is not a register

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each incident captured with a unique identifier (links to A.5.25 triage decision)

<<MUST item:A.5.26:reg_incident_id>>
_Why: 27002:5.26 — recording_

<<TEXT>>

## 2. Severity per row (per the classification scale used at triage)

<<MUST item:A.5.26:reg_severity>>
_Why: 27002:5.26 — coordination by severity_

<<TEXT>>

## 3. Status per row (open / contained / eradicated / recovered / closed)

<<MUST item:A.5.26:reg_status>>
_Why: 27002:5.26e_

<<TEXT>>

## 4. Named Incident Manager / owner per row

<<MUST item:A.5.26:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 5. Lifecycle dates per row: detected / contained / eradicated / recovered / closed

<<MUST item:A.5.26:reg_lifecycle_dates>>
_Why: 27002:5.26 — log of decisions_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Public-facing or regulator-relevant impact flag per row (drives notification path)

<<SHOULD item:A.5.26:reg_impact_flag>>
_Why: External notification triggers_

<<TEXT>>

### 2. Reference to evidence package per row (link to A.5.28 evidence store)

<<SHOULD item:A.5.26:reg_evidence_link>>
_Why: Forensic preservation_

<<TEXT>>
