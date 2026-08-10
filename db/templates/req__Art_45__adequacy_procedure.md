---
leaf_id: req:Art.45:adequacy_procedure
control_ref: Art.45
standard_id: GDPR:2016/679
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Adequacy Reliance Procedure

<<DOC_CONTROL>>

> Art.45 permits transfers to third countries / international organisations covered by an EU Commission adequacy decision. The procedure governs how adequacy is verified per transfer, including sub-decision conditions (e.g. US Data Privacy Framework requires recipient self-certification status)

## What this template gives you

This template helps you document your process for checking if data transfers to other countries or international organizations are allowed under EU adequacy decisions, including any special conditions like US recipient self-certification.

## When to use it

Use this whenever you need to transfer personal data outside the EU and want to confirm the destination is covered by an adequacy decision. Update the document whenever your transfer practices or adequacy decisions change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this template from scratch, as it covers several required elements that each need careful attention.

## 1. Adequacy-decision check — Art.45.3 Commission decision verified against current EU register

<<MUST item:Art.45:adequacy_decision_check>>
_Why: Art.45.3_

<<GUIDANCE>>

<<TEXT>>

## 2. Partial / sector / territory-specific adequacy handled (e.g. US-DPF applies only to certified entities, not US-wide)

<<MUST item:Art.45:partial_adequacy>>
_Why: Art.45.3 — specified territory or sector_

<<GUIDANCE>>

<<TEXT>>

## 3. Recipient eligibility check (e.g. US-DPF requires recipient on active list with current self-certification)

<<MUST item:Art.45:recipient_eligibility>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

## 4. Repeal monitoring — Schrems-style invalidations (Schrems I/II) and Commission Art.45.5 amend/repeal/suspend actions tracked

<<MUST item:Art.45:repeal_monitoring>>
_Why: Art.45.5_

<<GUIDANCE>>

<<TEXT>>

## 5. Named owner (DPO + legal counsel)

<<MUST item:Art.45:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic Art.45.4 review awareness — Commission reviews adequacy at least every 4 years

<<SHOULD item:Art.45:periodic_review>>
_Why: Art.45.4_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
