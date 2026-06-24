---
leaf_id: req:6.1.2:risk_register
control_ref: 6.1.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Information Security Risk Register

> The live output of the assessment procedure — every identified risk with owner, scoring, treatment status. Distinct from the procedure: the procedure is the methodology, the register is the data. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique risk identifier per row

<<MUST item:6.1.2:reg_risk_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Risk description per row (asset, threat, vulnerability)

<<MUST item:6.1.2:reg_description>>
_Why: Clause 6.1.2c — identified_

<<TEXT>>

## 3. Risk owner per row

<<MUST item:6.1.2:reg_owner>>
_Why: Clause 6.1.2c_

<<TEXT>>

## 4. Likelihood + consequence scores per row applied per the procedure's criteria

<<MUST item:6.1.2:reg_scoring>>
_Why: Clause 6.1.2d-e_

<<TEXT>>

## 5. Treatment status per row (accept / mitigate / transfer / avoid; link to 6.1.3 plan)

<<MUST item:6.1.2:reg_treatment_status>>
_Why: Cross-clause coherence_

<<TEXT>>

## 6. Last assessment date per row (drives staleness)

<<MUST item:6.1.2:reg_last_assessed>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Link from each risk back to the issues register (4.1) entry that surfaced it where applicable

<<SHOULD item:6.1.2:reg_4_1_link>>
_Why: Traceability_

<<TEXT>>
