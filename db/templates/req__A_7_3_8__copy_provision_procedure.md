---
leaf_id: req:A.7.3.8:copy_provision_procedure
control_ref: A.7.3.8
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# PII Copy Provision Procedure

> §7.3.8 requires the org to provide a copy of processed PII on request. Bridges to Art.15.3 (copy of PII) + Art.20 (portability — structured, commonly used, machine-readable format).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Format selection — structured, commonly used, accessible (Art.15.3 + machine-readable for Art.20)

<<MUST item:A.7.3.8:proc_format_selection>>
_Why: §7.3.8 — structured, commonly used format_

<<TEXT>>

## 2. Scope restriction — copy relates specifically to that subject; no cross-subject leakage

<<MUST item:A.7.3.8:proc_scope_restriction>>
_Why: §7.3.8 — relate specifically to that PII principal_

<<TEXT>>

## 3. Deleted-PII notification — where PII already deleted per retention policy, subject informed of that fact

<<MUST item:A.7.3.8:proc_deleted_notification>>
_Why: §7.3.8 — inform PII principal that PII has been deleted_

<<TEXT>>

## 4. No-re-identification rule — de-identified data not re-identified solely to fulfil this control

<<MUST item:A.7.3.8:proc_no_reidentification>>
_Why: §7.3.8 — should not seek to (re-)identify_

<<TEXT>>

## 5. Direct-transfer capability — where technically feasible, transfer directly to another controller (Art.20.2)

<<MUST item:A.7.3.8:proc_direct_transfer>>
_Why: §7.3.8 — transfer copy from one organization to another_

<<TEXT>>

## 6. Response-time SLA stated + honoured

<<MUST item:A.7.3.8:proc_response_sla>>
_Why: Art.12.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Self-service export where feasible

<<SHOULD item:A.7.3.8:proc_self_service>>
_Why: Efficiency_

<<TEXT>>
