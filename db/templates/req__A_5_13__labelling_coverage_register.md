---
leaf_id: req:A.5.13:labelling_coverage_register
control_ref: A.5.13
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Labelling Coverage Register

<<DOC_CONTROL>>

> A.5.13 requires every information-storing platform to actually apply labels — the systems where labelling isn't enabled are the ones where classified info leaks out. The register catalogues every in-scope information platform: system id, scope, labelling-enabled flag, automation level (manual/assisted/automatic), coverage %, owner. It is the operational record that proves labelling is org-wide, not just on the platforms IT remembered to configure

<!-- TABLE-COLUMNS leaf:req:A.5.13:labelling_coverage_register -->
<!-- column: item:A.5.13:reg_system_id -->
<!-- column: item:A.5.13:reg_scope -->
<!-- column: item:A.5.13:reg_enabled_flag -->
<!-- column: item:A.5.13:reg_automation -->
<!-- column: item:A.5.13:reg_coverage_pct -->
<!-- column: item:A.5.13:reg_owner -->
<!-- column: item:A.5.13:reg_classification_levels -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of which systems in your organization have information labelling enabled, showing coverage, automation level, and ownership for each platform. It provides clear evidence that labelling is applied consistently, not just selectively.

## When to use it

Use this register whenever you need to demonstrate or review labelling coverage across all your information systems. Update it whenever you add, remove, or change platforms, or when labelling configurations are updated.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required column for the first row, plus additional time for each system you need to document. Completing the register for a typical environment may take a few hours to a full day, depending on the number of platforms.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.13:labelling_coverage_register -->
| Reg System Id | Reg Scope | Reg Enabled Flag | Reg Automation | Reg Coverage Pct | Reg Owner | Reg Classification Levels |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.13:labelling_coverage_register -->

## Column guidance — what to fill in

### Reg System Id

<<MUST item:A.5.13:reg_system_id>>
_Why: 27002:5.13 — visibility_

> _Standard text:_ Each in-scope information system captured with a unique identifier (file shares, M365 tenants, drive backends, ticketing systems, code repos with sensitive data)

<<GUIDANCE>>

### Reg Scope

<<MUST item:A.5.13:reg_scope>>
_Why: Coverage analysis_

> _Standard text:_ Scope per row (which content classes this system stores — e.g. customer data, HR records, source code, financial)

<<GUIDANCE>>

### Reg Enabled Flag

<<MUST item:A.5.13:reg_enabled_flag>>
_Why: 27002:5.13 — applied_

> _Standard text:_ Labelling-enabled flag per row (yes / partial / no — with remediation date if not yes)

<<GUIDANCE>>

### Reg Automation

<<MUST item:A.5.13:reg_automation>>
_Why: 27002:5.13 — implemented_

> _Standard text:_ Automation level per row (manual / assisted / automatic; drives which gaps need user training vs config)

<<GUIDANCE>>

### Reg Coverage Pct

<<MUST item:A.5.13:reg_coverage_pct>>
_Why: Program effectiveness_

> _Standard text:_ Coverage percentage per row (% of items in this system that carry a label — sampled or auto-measured)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.5.13:reg_owner>>
_Why: Accountability_

> _Standard text:_ System owner per row (named individual accountable for labelling on this platform)

<<GUIDANCE>>

### Reg Classification Levels

<<MUST item:A.5.13:reg_classification_levels>>
_Why: 27002:5.13 + cross-link to [[A.5.12]]_

> _Standard text:_ Classification levels deployed per row (links to A.5.12 scheme — sometimes a system only uses a subset)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Dlp Policy

<<SHOULD item:A.5.13:reg_dlp_policy>>
_Why: Defence-in-depth_

> _Standard text:_ DLP policy link per row where applicable (sensitivity-label-driven DLP rules wired to the system)

<<GUIDANCE>>

### Reg External Ingress

<<SHOULD item:A.5.13:reg_external_ingress>>
_Why: Real-world coverage_

> _Standard text:_ External-ingress flag per row where docs arrive from outside (triggers the external_handling SHOULD path)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
