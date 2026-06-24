---
leaf_id: req:A.5.26:incident_closure_record
control_ref: A.5.26
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
---

# Per-Incident Closure Records

> A.5.26 requires incidents to close with documented outcomes that feed § 5.27 lessons-learned. The closure record evidences the actual close: which incident, the root cause, the containment effectiveness, the recovery validation, and the handoff to lessons-learned. One record per incident, traceable back to the incident register

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Incident identifier per record (links to the incident register)

<<MUST item:A.5.26:cls_incident_ref>>
_Why: 27002:5.26 — recording_

<<TEXT>>

## 2. Root cause captured (technical + organisational contributors)

<<MUST item:A.5.26:cls_root_cause>>
_Why: 27002:5.26h_

<<TEXT>>

## 3. Containment effectiveness assessed (did the actions taken actually limit damage)

<<MUST item:A.5.26:cls_containment_eff>>
_Why: 27002:5.26a_

<<TEXT>>

## 4. Recovery validation evidenced (system returned to secure state; verified, not just attempted)

<<MUST item:A.5.26:cls_recovery_valid>>
_Why: 27002:5.26e_

<<TEXT>>

## 5. Handoff reference into A.5.27 lessons register

<<MUST item:A.5.26:cls_lessons_handoff>>
_Why: 27002:5.26 → 5.27_

<<TEXT>>

## 6. Closure authority per record (named role)

<<MUST item:A.5.26:cls_authoriser>>
_Why: Accountability_

<<TEXT>>

## 7. MTTC / MTTR / containment-SLA-met flag per record — structured boolean against the targets stated in the procedure or service catalogue; analogous to A.5.16:rev_sla_met

<<MUST item:A.5.26:cls_sla_met>>
_Why: Auditor-critical timeliness proof — drives the rev_metrics analysis on the review leaf_

<<TEXT>>

## 8. GDPR Art.33 breach-notification trigger flag per record (yes/no with notification reference where yes) — proves the personal-data integration with A.5.26 fires reliably

<<MUST item:A.5.26:cls_gdpr_triggered>>
_Why: GDPR Art.33.1 / Art.33.5 — pairs with procedure-level gdpr_72h_trigger_check_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External notifications made per record (regulators, customers, suppliers)

<<SHOULD item:A.5.26:cls_external_notif>>
_Why: 27002:5.26 — communication_

<<TEXT>>

### 2. Evidence package archived per record (link to A.5.28 evidence store)

<<SHOULD item:A.5.26:cls_evidence_archive>>
_Why: Forensic preservation_

<<TEXT>>
