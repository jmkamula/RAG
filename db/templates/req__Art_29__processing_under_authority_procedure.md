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

<<DOC_CONTROL>>

> Art.29 binds processor + person acting under processor's authority + person acting under controller's authority to process personal data ONLY on documented instructions from the controller (unless required by Union/Member State law). The procedure governs how instructions are received, recorded, and enforced internally

## What this template gives you

This template helps you set up a clear, step-by-step procedure for making sure your team only processes personal data when instructed by your client or as required by law. It ensures everyone knows how to receive, record, and follow those instructions.

## When to use it

Use this document whenever your organization processes personal data on behalf of another company and needs to show you only act on their documented instructions. Update it whenever your procedures or legal requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes drafting this procedure from scratch, as you'll need to cover several required steps and ensure your process is clearly described.

## 1. Instructions source documented (DPA terms + change orders / customer support tickets / contract amendments)

<<MUST item:Art.29:instructions_source>>
_Why: Art.29 — documented instructions_

<<GUIDANCE>>

<<TEXT>>

## 2. Internal propagation — how instructions reach engineering / support / ops who actually touch data

<<MUST item:Art.29:internal_propagation>>
_Why: Art.29 — under authority_

<<GUIDANCE>>

<<TEXT>>

## 3. Authority chain — every person touching personal data covered by an authorisation traceable to the controller's instruction

<<MUST item:Art.29:authority_chain>>
_Why: Art.29 — under authority_

<<GUIDANCE>>

<<TEXT>>

## 4. Exception handling — Union/MS law overrides (Art.29 second clause) recorded when invoked

<<MUST item:Art.29:exception_handling>>
_Why: Art.29 exception_

<<GUIDANCE>>

<<TEXT>>

## 5. Link to A.6.3 / A.7.3 awareness training for personnel under authority

<<MUST item:Art.29:training_link>>
_Why: Cross-control_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (DPO + ops lead)

<<SHOULD item:Art.29:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
