---
leaf_id: req:A.5.37:operating_procedures_register
control_ref: A.5.37
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 3
---

# Documented Operating Procedures Register

> A.5.37 requires operating procedures for information processing facilities to be documented and made available to personnel who need them. The register is the live catalogue: every procedure listed with the facility/system it covers, the owner, version, last-updated and review-due dates, and the availability mechanism. Maintenance procedure, applicable-facilities scope and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Inventory of operating procedures (which facilities/systems they cover — backup, restore, patching, on-call response, change deployment, monitoring response, capacity, log-handling, etc.)

<<MUST item:A.5.37:procedure_inventory>>
_Why: 27002:5.37 — documented_

<<TEXT>>

## 2. Scope coverage stated (every information processing facility represented — gaps surface where a facility exists without a documented procedure)

<<MUST item:A.5.37:scope_coverage>>
_Why: 27002:5.37 — information processing facilities_

<<TEXT>>

## 3. Availability mechanism stated per procedure (where personnel find them — intranet location, runbook system, wiki path with permissions, code-of-conduct package)

<<MUST item:A.5.37:availability>>
_Why: 27002:5.37 — made available to personnel_

<<TEXT>>

## 4. Ownership per procedure (named role or individual responsible for currency — the operator who runs the procedure, not 'IT')

<<MUST item:A.5.37:owner_per_procedure>>
_Why: 27002:5.37 — documented_

<<TEXT>>

## 5. Version control per procedure with last-updated date and review-due date (drives the review leaf)

<<MUST item:A.5.37:version_control>>
_Why: 27002:5.37 — documented_

<<TEXT>>

## 6. Intended audience per procedure (which personnel 'need' the procedure — drives access permissions and training links)

<<MUST item:A.5.37:audience_per_procedure>>
_Why: 27002:5.37 — personnel who need them_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Template adherence flag per procedure (consistent shape across the catalogue — purpose / scope / prerequisites / steps / verification / rollback)

<<SHOULD item:A.5.37:template_adherence>>
_Why: Reviewability_

<<TEXT>>

### 2. Emergency-use flag per procedure (procedures needed under pressure — DR, incident response — get higher visibility and tighter currency)

<<SHOULD item:A.5.37:emergency_flag>>
_Why: Operational realism_

<<TEXT>>

### 3. Cross-link to related controls per procedure (A.5.24/A.5.26 incident, A.5.29 disruption, A.5.30 ICT recovery, A.8.x technical controls)

<<SHOULD item:A.5.37:related_controls_link>>
_Why: Cross-control coherence_

<<TEXT>>
