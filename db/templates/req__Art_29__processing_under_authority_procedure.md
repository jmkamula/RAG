---
leaf_id: req:Art.29:processing_under_authority_procedure
control_ref: Art.29
standard_id: GDPR:2016/679
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Processing Under Authority Procedure

> Art.29 binds processor + person acting under processor's authority + person acting under controller's authority to process personal data ONLY on documented instructions from the controller (unless required by Union/Member State law). The procedure governs how instructions are received, recorded, and enforced internally

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Instructions source documented (DPA terms + change orders / customer support tickets / contract amendments)

<<MUST item:Art.29:instructions_source>>
_Why: Art.29 — documented instructions_

<<TEXT>>

## 2. Internal propagation — how instructions reach engineering / support / ops who actually touch data

<<MUST item:Art.29:internal_propagation>>
_Why: Art.29 — under authority_

<<TEXT>>

## 3. Authority chain — every person touching personal data covered by an authorisation traceable to the controller's instruction

<<MUST item:Art.29:authority_chain>>
_Why: Art.29 — under authority_

<<TEXT>>

## 4. Exception handling — Union/MS law overrides (Art.29 second clause) recorded when invoked

<<MUST item:Art.29:exception_handling>>
_Why: Art.29 exception_

<<TEXT>>

## 5. Link to A.6.3 / A.7.3 awareness training for personnel under authority

<<MUST item:Art.29:training_link>>
_Why: Cross-control_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (DPO + ops lead)

<<SHOULD item:Art.29:proc_owner>>
_Why: Accountability_

<<TEXT>>
