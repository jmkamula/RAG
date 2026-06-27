---
leaf_id: req:A.6.7:remote_working_procedure
control_ref: A.6.7
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 7
should_count: 2
---

# Remote Working Approval and Management Procedure

> Operational steps for granting, modifying and revoking remote-working arrangements per worker. Owns the joiner-mover-leaver flow for remote workers: who approves, on what evidence (suitable workspace, equipment provided, training completed), with what conditions. Pairs with A.6.7 policy (rules) and the remote-working register (who has access right now)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-worker approval workflow before remote-working starts (line manager + InfoSec sign-off, suitable-workspace attestation, equipment-provisioning checkpoint, awareness-training completion check)

<<MUST item:A.6.7:proc_approval_workflow>>
_Why: 27002:6.7 — controlled approval_

<<TEXT>>

## 2. Conditions per approval recorded (location category — home / co-working / abroad; permitted hours; data-class restrictions; supervision requirements; expiry / review date)

<<MUST item:A.6.7:proc_grant_conditions>>
_Why: 27002:6.7 — appropriate conditions_

<<TEXT>>

## 3. Equipment provisioning step (corporate device only / BYOD permitted with MDM / specific peripheral restrictions like external monitors / printers), cross-link to A.5.9 asset register so remote-issued equipment is tracked

<<MUST item:A.6.7:proc_equipment_provision>>
_Why: 27002:6.7 — equipment + A.5.9 link_

<<TEXT>>

## 4. Modification path when worker's situation changes (relocation, role change, equipment swap, extended absence) — drives register update + may trigger re-approval

<<MUST item:A.6.7:proc_modification_path>>
_Why: 27002:6.7 — change handling_

<<TEXT>>

## 5. Revocation path on termination / extended leave / approval expiry / policy breach — includes equipment return per A.5.11 and access revocation per A.5.18 (cross-link to leaver flows)

<<MUST item:A.6.7:proc_revocation_path>>
_Why: 27002:6.7 — return / A.5.11 + A.5.18 link_

<<TEXT>>

## 6. Incident-handling route for remote-context incidents (lost device, suspected unauthorised access at remote site, family-access exposure) — cross-link to A.5.24 incident response

<<MUST item:A.6.7:proc_incident_route>>
_Why: 27002:6.7 — A.5.24 link_

<<TEXT>>

## 7. Named owner of the procedure (typically Head of IT / InfoSec with HR partner for approval workflow)

<<MUST item:A.6.7:proc_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Specific travel-briefing step for high-risk destinations (countries with elevated surveillance / corporate-espionage risk — burner laptop, restricted credentials, encrypted comms only)

<<SHOULD item:A.6.7:proc_travel_briefing>>
_Why: 27002:6.7f + Practical guidance_

<<TEXT>>

### 2. Family/visitor access briefing (verbal explanation to the worker that family members must not use the corporate device — drives the policy's family-access rule into operational reality)

<<SHOULD item:A.6.7:proc_family_briefing>>
_Why: Practical guidance_

<<TEXT>>
