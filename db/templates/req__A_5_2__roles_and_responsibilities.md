---
leaf_id: req:A.5.2:roles_and_responsibilities
control_ref: A.5.2
standard_id: ISO27001:2022
evidence_type: responsibility_matrix
trigger_type: universal
template_version: 1
must_count: 6
should_count: 4
---

# Information Security Roles and Responsibilities Matrix

> A.5.2 requires information security roles and responsibilities to be defined and allocated according to organization needs. Evidence is a responsibility matrix (or equivalent section in the ISMS charter) enumerating roles, allocating them to named individuals or positions, and stating reporting lines. Approval, communication and periodic review of this allocation are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Information security roles enumerated (CISO, ISMS Manager, Asset Owners, Risk Owners, Incident Manager, DPO where applicable)

<<MUST item:A.5.2:roles_enumerated>>
_Why: 27002:5.2a_

<<TEXT>>

## 2. Responsibilities described per role (decision rights, oversight, execution)

<<MUST item:A.5.2:responsibilities>>
_Why: 27002:5.2b_

<<TEXT>>

## 3. Allocation to named individuals or positions, not just abstract role labels

<<MUST item:A.5.2:allocation>>
_Why: 27002:5.2d / Clause 5.3_

<<TEXT>>

## 4. Reporting and escalation lines stated (who each role reports to)

<<MUST item:A.5.2:reporting_lines>>
_Why: 27002:5.2f_

<<TEXT>>

## 5. Accountability for protection and risk management of specific assets assigned

<<MUST item:A.5.2:asset_owner_resp>>
_Why: 27002:5.2g_

<<TEXT>>

## 6. Allocation covers ISMS operation, asset ownership, risk management, audits and security review topics

<<MUST item:A.5.2:topic_alignment>>
_Why: 27002:5.2b_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Links back to the Information Security Policy (A.5.1)

<<SHOULD item:A.5.2:isp_link>>
_Why: Coherence with policy framework_

<<TEXT>>

### 2. Notes conflicts to be resolved via segregation of duties (A.5.3)

<<SHOULD item:A.5.2:segregation_note>>
_Why: 27002:5.2i / A.5.3_

<<TEXT>>

### 3. For cloud and external services, responsibilities split between the organization and the provider stated

<<SHOULD item:A.5.2:cloud_responsibilities>>
_Why: 27002:5.2k_

<<TEXT>>

### 4. Notes competency/training requirements per role (cross-ref A.6.3)

<<SHOULD item:A.5.2:competency_link>>
_Why: 27002:5.2j / A.6.3_

<<TEXT>>
