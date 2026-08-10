---
leaf_id: req:A.5.31:obligations_register_maintenance_procedure
control_ref: A.5.31
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Legal/Regulatory Register Maintenance Procedure

<<DOC_CONTROL>>

> A.5.31 expects the register to be 'kept up to date'. The procedure documents who keeps it current, what triggers an update (new regulation, regulator guidance, customer contract change, jurisdiction expansion), and the intake path from trigger to register entry

## What this template gives you

This template helps you document how your organization keeps its legal and regulatory register up to date, including who is responsible and how updates are managed. It's useful for showing compliance with ISO 27001 requirements.

## When to use it

Use this procedure whenever your legal or regulatory obligations change, such as with new laws, regulator guidance, contract updates, or expanding into new regions. Review and update the document as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes drafting this from scratch, depending on the complexity of your register and the number of required elements you need to cover.

## 1. Named maintainer (compliance lead, legal counsel, or designate) with documented responsibility for register accuracy

<<MUST item:A.5.31:proc_maintainer>>
_Why: Accountability — 27002:5.31_

<<GUIDANCE>>

<<TEXT>>

## 2. Update triggers enumerated (new law/regulation, regulator guidance, new customer contract, new jurisdiction, sectoral code change)

<<MUST item:A.5.31:proc_update_triggers>>
_Why: 27002:5.31 — kept up to date_

<<GUIDANCE>>

<<TEXT>>

## 3. Intake path from trigger to register entry (who flags, who interprets, who classifies, who confirms compliance approach)

<<MUST item:A.5.31:proc_intake_path>>
_Why: Operational sufficiency_

<<GUIDANCE>>

<<TEXT>>

## 4. Impact-assessment step when an obligation changes — affected controls and policies identified, gap actions opened

<<MUST item:A.5.31:proc_change_assessment>>
_Why: 27002:5.31b — approach to meet_

<<GUIDANCE>>

<<TEXT>>

## 5. Authority-contact sync — adding an obligation that introduces a new regulator triggers A.5.5 register update

<<MUST item:A.5.31:proc_authority_sync>>
_Why: A.5.5 coherence_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Legal review step before a new entry is finalised (internal or external counsel approval)

<<SHOULD item:A.5.31:proc_legal_review>>
_Why: Interpretation accuracy_

<<GUIDANCE>>

<<TEXT>>

### 2. Horizon-scanning cadence for upcoming obligations (proposed legislation, pending regulator decisions)

<<SHOULD item:A.5.31:proc_horizon_scan>>
_Why: Forward-looking compliance_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
