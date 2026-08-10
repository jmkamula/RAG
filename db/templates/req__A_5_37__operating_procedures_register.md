---
leaf_id: req:A.5.37:operating_procedures_register
control_ref: A.5.37
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 3
table_shape: true
---

# Documented Operating Procedures Register

<<DOC_CONTROL>>

> A.5.37 requires operating procedures for information processing facilities to be documented and made available to personnel who need them. The register is the live catalogue: every procedure listed with the facility/system it covers, the owner, version, last-updated and review-due dates, and the availability mechanism. Maintenance procedure, applicable-facilities scope and periodic review are sibling leaves

<!-- TABLE-COLUMNS leaf:req:A.5.37:operating_procedures_register -->
<!-- column: item:A.5.37:procedure_inventory -->
<!-- column: item:A.5.37:scope_coverage -->
<!-- column: item:A.5.37:availability -->
<!-- column: item:A.5.37:owner_per_procedure -->
<!-- column: item:A.5.37:version_control -->
<!-- column: item:A.5.37:audience_per_procedure -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, up-to-date list of all your documented operating procedures, showing who owns each one, which systems they cover, and when they were last reviewed.

## When to use it

Use this register whenever you need to track and manage operating procedures for your information processing facilities, and update it whenever procedures change or new ones are added.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each procedure you list, so the total time depends on how many procedures and systems you need to include.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.37:operating_procedures_register -->
| Procedure Inventory | Scope Coverage | Availability | Owner Per Procedure | Version Control | Audience Per Procedure |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.37:operating_procedures_register -->

## Column guidance — what to fill in

### Procedure Inventory

<<MUST item:A.5.37:procedure_inventory>>
_Why: 27002:5.37 — documented_

> _Standard text:_ Inventory of operating procedures (which facilities/systems they cover — backup, restore, patching, on-call response, change deployment, monitoring response, capacity, log-handling, etc.)

<<GUIDANCE>>

### Scope Coverage

<<MUST item:A.5.37:scope_coverage>>
_Why: 27002:5.37 — information processing facilities_

> _Standard text:_ Scope coverage stated (every information processing facility represented — gaps surface where a facility exists without a documented procedure)

<<GUIDANCE>>

### Availability

<<MUST item:A.5.37:availability>>
_Why: 27002:5.37 — made available to personnel_

> _Standard text:_ Availability mechanism stated per procedure (where personnel find them — intranet location, runbook system, wiki path with permissions, code-of-conduct package)

<<GUIDANCE>>

### Owner Per Procedure

<<MUST item:A.5.37:owner_per_procedure>>
_Why: 27002:5.37 — documented_

> _Standard text:_ Ownership per procedure (named role or individual responsible for currency — the operator who runs the procedure, not 'IT')

<<GUIDANCE>>

### Version Control

<<MUST item:A.5.37:version_control>>
_Why: 27002:5.37 — documented_

> _Standard text:_ Version control per procedure with last-updated date and review-due date (drives the review leaf)

<<GUIDANCE>>

### Audience Per Procedure

<<MUST item:A.5.37:audience_per_procedure>>
_Why: 27002:5.37 — personnel who need them_

> _Standard text:_ Intended audience per procedure (which personnel 'need' the procedure — drives access permissions and training links)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Template Adherence

<<SHOULD item:A.5.37:template_adherence>>
_Why: Reviewability_

> _Standard text:_ Template adherence flag per procedure (consistent shape across the catalogue — purpose / scope / prerequisites / steps / verification / rollback)

<<GUIDANCE>>

### Emergency Flag

<<SHOULD item:A.5.37:emergency_flag>>
_Why: Operational realism_

> _Standard text:_ Emergency-use flag per procedure (procedures needed under pressure — DR, incident response — get higher visibility and tighter currency)

<<GUIDANCE>>

### Related Controls Link

<<SHOULD item:A.5.37:related_controls_link>>
_Why: Cross-control coherence_

> _Standard text:_ Cross-link to related controls per procedure (A.5.24/A.5.26 incident, A.5.29 disruption, A.5.30 ICT recovery, A.8.x technical controls)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
