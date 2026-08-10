---
leaf_id: req:A.5.2:roles_and_responsibilities
control_ref: A.5.2
standard_id: ISO27001:2022
evidence_type: responsibility_matrix
trigger_type: universal
template_version: 1
must_count: 6
should_count: 4
table_shape: true
---

# Information Security Roles and Responsibilities Matrix

<<DOC_CONTROL>>

> A.5.2 requires information security roles and responsibilities to be defined and allocated according to organization needs. Evidence is a responsibility matrix (or equivalent section in the ISMS charter) enumerating roles, allocating them to named individuals or positions, and stating reporting lines. Approval, communication and periodic review of this allocation are sibling leaves

<!-- TABLE-COLUMNS leaf:req:A.5.2:roles_and_responsibilities -->
<!-- column: item:A.5.2:roles_enumerated -->
<!-- column: item:A.5.2:responsibilities -->
<!-- column: item:A.5.2:allocation -->
<!-- column: item:A.5.2:reporting_lines -->
<!-- column: item:A.5.2:asset_owner_resp -->
<!-- column: item:A.5.2:topic_alignment -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you clearly define and document who is responsible for each information security role in your organization, making it easier to assign tasks and clarify reporting lines.

## When to use it

Use this matrix whenever you need to formally allocate information security responsibilities, and update it whenever roles or reporting lines change to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this from scratch, depending on the number of roles and people involved.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.2:roles_and_responsibilities -->
| Roles Enumerated | Responsibilities | Allocation | Reporting Lines | Asset Owner Resp | Topic Alignment |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.2:roles_and_responsibilities -->

## Column guidance — what to fill in

### Roles Enumerated

<<MUST item:A.5.2:roles_enumerated>>
_Why: 27002:5.2a_

> _Standard text:_ Information security roles enumerated (CISO, ISMS Manager, Asset Owners, Risk Owners, Incident Manager, DPO where applicable)

<<GUIDANCE>>

### Responsibilities

<<MUST item:A.5.2:responsibilities>>
_Why: 27002:5.2b_

> _Standard text:_ Responsibilities described per role (decision rights, oversight, execution)

<<GUIDANCE>>

### Allocation

<<MUST item:A.5.2:allocation>>
_Why: 27002:5.2d / Clause 5.3_

> _Standard text:_ Allocation to named individuals or positions, not just abstract role labels

<<GUIDANCE>>

### Reporting Lines

<<MUST item:A.5.2:reporting_lines>>
_Why: 27002:5.2f_

> _Standard text:_ Reporting and escalation lines stated (who each role reports to)

<<GUIDANCE>>

### Asset Owner Resp

<<MUST item:A.5.2:asset_owner_resp>>
_Why: 27002:5.2g_

> _Standard text:_ Accountability for protection and risk management of specific assets assigned

<<GUIDANCE>>

### Topic Alignment

<<MUST item:A.5.2:topic_alignment>>
_Why: 27002:5.2b_

> _Standard text:_ Allocation covers ISMS operation, asset ownership, risk management, audits and security review topics

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Isp Link

<<SHOULD item:A.5.2:isp_link>>
_Why: Coherence with policy framework_

> _Standard text:_ Links back to the Information Security Policy (A.5.1)

<<GUIDANCE>>

### Segregation Note

<<SHOULD item:A.5.2:segregation_note>>
_Why: 27002:5.2i / A.5.3_

> _Standard text:_ Notes conflicts to be resolved via segregation of duties (A.5.3)

<<GUIDANCE>>

### Cloud Responsibilities

<<SHOULD item:A.5.2:cloud_responsibilities>>
_Why: 27002:5.2k_

> _Standard text:_ For cloud and external services, responsibilities split between the organization and the provider stated

<<GUIDANCE>>

### Competency Link

<<SHOULD item:A.5.2:competency_link>>
_Why: 27002:5.2j / A.6.3_

> _Standard text:_ Notes competency/training requirements per role (cross-ref A.6.3)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
