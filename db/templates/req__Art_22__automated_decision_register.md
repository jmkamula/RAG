---
leaf_id: req:Art.22:automated_decision_register
control_ref: Art.22
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Automated Decision-Making Register

> Per-decision-system record (NOT per individual decision) for every solely-automated decision system in scope. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. System / model identifier per row

<<MUST item:Art.22:reg_system_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Decision categories made (loan approval, employment screening, pricing, etc.)

<<MUST item:Art.22:reg_decisions_made>>
_Why: Defining scope_

<<TEXT>>

## 3. Art.22.2 basis cited per row (contract / MS law / explicit consent)

<<MUST item:Art.22:reg_art22_2_basis>>
_Why: Art.22.2_

<<TEXT>>

## 4. Per-row Art.22.3 safeguards in place (human intervention queue, contest UI, model explanation)

<<MUST item:Art.22:reg_safeguards>>
_Why: Art.22.3_

<<TEXT>>

## 5. Per-row DPIA reference (Art.35 nearly always triggered for Art.22)

<<MUST item:Art.22:reg_dpia_link>>
_Why: Art.35.3.a_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row objection count (Art.22-related rights requests this period)

<<SHOULD item:Art.22:reg_objection_count>>
_Why: Operational visibility_

<<TEXT>>
