---
leaf_id: req:A.5.13:labelling_coverage_register
control_ref: A.5.13
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Labelling Coverage Register

> A.5.13 requires every information-storing platform to actually apply labels — the systems where labelling isn't enabled are the ones where classified info leaks out. The register catalogues every in-scope information platform: system id, scope, labelling-enabled flag, automation level (manual/assisted/automatic), coverage %, owner. It is the operational record that proves labelling is org-wide, not just on the platforms IT remembered to configure

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each in-scope information system captured with a unique identifier (file shares, M365 tenants, drive backends, ticketing systems, code repos with sensitive data)

<<MUST item:A.5.13:reg_system_id>>
_Why: 27002:5.13 — visibility_

<<TEXT>>

## 2. Scope per row (which content classes this system stores — e.g. customer data, HR records, source code, financial)

<<MUST item:A.5.13:reg_scope>>
_Why: Coverage analysis_

<<TEXT>>

## 3. Labelling-enabled flag per row (yes / partial / no — with remediation date if not yes)

<<MUST item:A.5.13:reg_enabled_flag>>
_Why: 27002:5.13 — applied_

<<TEXT>>

## 4. Automation level per row (manual / assisted / automatic; drives which gaps need user training vs config)

<<MUST item:A.5.13:reg_automation>>
_Why: 27002:5.13 — implemented_

<<TEXT>>

## 5. Coverage percentage per row (% of items in this system that carry a label — sampled or auto-measured)

<<MUST item:A.5.13:reg_coverage_pct>>
_Why: Program effectiveness_

<<TEXT>>

## 6. System owner per row (named individual accountable for labelling on this platform)

<<MUST item:A.5.13:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 7. Classification levels deployed per row (links to A.5.12 scheme — sometimes a system only uses a subset)

<<MUST item:A.5.13:reg_classification_levels>>
_Why: 27002:5.13 + cross-link to [[A.5.12]]_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. DLP policy link per row where applicable (sensitivity-label-driven DLP rules wired to the system)

<<SHOULD item:A.5.13:reg_dlp_policy>>
_Why: Defence-in-depth_

<<TEXT>>

### 2. External-ingress flag per row where docs arrive from outside (triggers the external_handling SHOULD path)

<<SHOULD item:A.5.13:reg_external_ingress>>
_Why: Real-world coverage_

<<TEXT>>
