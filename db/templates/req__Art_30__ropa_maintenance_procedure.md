---
leaf_id: req:Art.30:ropa_maintenance_procedure
control_ref: Art.30
standard_id: GDPR:2016/679
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 3
---

# RoPA Maintenance Procedure

> Art.30 implies an ongoing obligation — the register must reflect current reality. The maintenance procedure documents who keeps it current, what changes trigger an update, the path from trigger to register entry, and the link to other GDPR gates (Art.28 DPA on new processor, Art.35 DPIA on high-risk new purpose)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Named maintainer (DPO, privacy lead, or controller's designate) with documented responsibility for register accuracy

<<MUST item:Art.30:proc_maintainer>>
_Why: Accountability — Art.5.2_

<<TEXT>>

## 2. Update triggers enumerated (new system, new purpose, new processor, new third-country transfer, retention change, DPIA outcome)

<<MUST item:Art.30:proc_triggers>>
_Why: Art.30.1 — must reflect current state_

<<TEXT>>

## 3. Path from trigger to register entry stated (who notifies, who reviews, who approves the entry)

<<MUST item:Art.30:proc_update_path>>
_Why: Operational sufficiency_

<<TEXT>>

## 4. Linkage to Art.28 DPA process — adding a new processor cannot complete without DPA and register update

<<MUST item:Art.30:proc_dpa_gate>>
_Why: Art.28 / Art.30.1.d coherence_

<<TEXT>>

## 5. Linkage to Art.35 DPIA — high-risk new processing requires DPIA before register entry is finalised

<<MUST item:Art.30:proc_dpia_gate>>
_Why: Art.35 / Art.30 coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Processor-side update path stated if org also acts as processor (Art.30.2 records)

<<SHOULD item:Art.30:proc_processor_side>>
_Why: Art.30.2_

<<TEXT>>

### 2. Cadence for ad-hoc review when no specific trigger fires (e.g. quarterly sweep)

<<SHOULD item:Art.30:proc_review_cadence>>
_Why: Preventive maintenance_

<<TEXT>>

### 3. Escalation path if maintainer is unavailable or a trigger is missed

<<SHOULD item:Art.30:proc_escalation>>
_Why: Continuity_

<<TEXT>>
