---
leaf_id: req:A.5.23:cloud_service_register
control_ref: A.5.23
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 7
should_count: 3
table_shape: true
---

# Cloud Service Register

<<DOC_CONTROL>>

> A.5.23 expects the org to know which cloud services are in use, where they store and process data, what classification of data they hold, what the shared-responsibility split looks like in practice, and what the agreement says. The register is the live source of truth — feeding the periodic posture review and exit-migration leaves

<!-- TABLE-COLUMNS leaf:req:A.5.23:cloud_service_register -->
<!-- column: item:A.5.23:reg_service -->
<!-- column: item:A.5.23:reg_classification -->
<!-- column: item:A.5.23:reg_geo -->
<!-- column: item:A.5.23:reg_responsibility -->
<!-- column: item:A.5.23:reg_owner -->
<!-- column: item:A.5.23:reg_agreement -->
<!-- column: item:A.5.23:reg_exit_readiness -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an up-to-date list of all cloud services your organization uses, including where your data is stored, how it’s classified, and what each provider is responsible for.

## When to use it

Use this register whenever your organization starts using a new cloud service, changes how a service is used, or reviews its cloud setup. Update it as needed to keep your records accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1-2 hours to complete the required details for each new cloud service, plus additional time for each service you add to the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.23:cloud_service_register -->
| Reg Service | Reg Classification | Reg Geo | Reg Responsibility | Reg Owner | Reg Agreement | Reg Exit Readiness |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.23:cloud_service_register -->

## Column guidance — what to fill in

### Reg Service

<<MUST item:A.5.23:reg_service>>
_Why: 27002:5.23a — scope_

> _Standard text:_ Each cloud service identified per row (provider, service name, deployment model)

<<GUIDANCE>>

### Reg Classification

<<MUST item:A.5.23:reg_classification>>
_Why: 27002:5.23 — sensitive info_

> _Standard text:_ Data classification per service (which org-classification levels are processed)

<<GUIDANCE>>

### Reg Geo

<<MUST item:A.5.23:reg_geo>>
_Why: 27002:5.23 — geo_

> _Standard text:_ Geographic location of data per service (region, sub-region)

<<GUIDANCE>>

### Reg Responsibility

<<MUST item:A.5.23:reg_responsibility>>
_Why: 27002:5.23d_

> _Standard text:_ Shared-responsibility split recorded per service (what is CSP-managed, what is org-managed)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.5.23:reg_owner>>
_Why: Accountability_

> _Standard text:_ Named internal owner accountable per service (typically platform / SRE / business owner)

<<GUIDANCE>>

### Reg Agreement

<<MUST item:A.5.23:reg_agreement>>
_Why: Cross-control consistency_

> _Standard text:_ Reference to the agreement / contract in force per service (link to A.5.20 coverage register)

<<GUIDANCE>>

### Reg Exit Readiness

<<MUST item:A.5.23:reg_exit_readiness>>
_Why: 27002:5.23 — exit_

> _Standard text:_ Exit-plan readiness flag per service (Yes / No / Stale)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Subprocessors

<<SHOULD item:A.5.23:reg_subprocessors>>
_Why: 27002:5.23 — sub-processing_

> _Standard text:_ Disclosed sub-processors per service tracked

<<GUIDANCE>>

### Reg Attestation

<<SHOULD item:A.5.23:reg_attestation>>
_Why: 27002:5.23 — CSP assurance_

> _Standard text:_ Most recent CSP attestation / certification reference per service (with date)

<<GUIDANCE>>

### Reg Dependency Map

<<SHOULD item:A.5.23:reg_dependency_map>>
_Why: Continuity awareness_

> _Standard text:_ Business-process dependency map (which processes depend on which service)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
