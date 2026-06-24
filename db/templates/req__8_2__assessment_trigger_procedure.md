---
leaf_id: req:8.2:assessment_trigger_procedure
control_ref: 8.2
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Operational Risk Assessment Trigger Procedure

> The procedure governing when an operational assessment fires — the planned-interval cadence + the catalog of 'significant changes' that trigger ad-hoc reassessments. Without explicit triggers, ad-hoc assessments tend not to happen until incident pressure forces them

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Planned-interval cadence stated per risk tier (annual for low, semi-annual or quarterly for higher-risk)

<<MUST item:8.2:proc_cadence>>
_Why: Clause 8.2 — planned intervals_

<<TEXT>>

## 2. Catalog of significant changes that trigger reassessment (new product, new region, new regulator, major incident, M&A, supplier change)

<<MUST item:8.2:proc_change_catalog>>
_Why: Clause 8.2 — significant changes_

<<TEXT>>

## 3. Invocation path (how a change-driven reassessment gets requested + approved + scheduled)

<<MUST item:8.2:proc_invocation>>
_Why: Operational discipline_

<<TEXT>>

## 4. Link to the 6.1.2 procedure (8.2 uses 6.1.2's methodology, not a separate one)

<<MUST item:8.2:proc_link_to_6_1_2>>
_Why: Clause 8.2 — criteria established in 6.1.2_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner of the trigger procedure

<<SHOULD item:8.2:proc_owner>>
_Why: Accountability_

<<TEXT>>
