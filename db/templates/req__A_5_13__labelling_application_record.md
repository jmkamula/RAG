---
leaf_id: req:A.5.13:labelling_application_record
control_ref: A.5.13
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Per-Platform Labelling Application Record

<<DOC_CONTROL>>

> A.5.13 expects labelling to be applied as the org's information estate grows — every new platform that stores information of any classification level should be brought into scope, not just the platforms IT happened to configure first. The application record evidences each enablement event: platform id, scope, enablement method, coverage verification, training rollout, owner. One record per platform/system onboarding (or major re-config), traceable back to the coverage register

<!-- TABLE-COLUMNS leaf:req:A.5.13:labelling_application_record -->
<!-- column: item:A.5.13:app_system_ref -->
<!-- column: item:A.5.13:app_scope -->
<!-- column: item:A.5.13:app_method -->
<!-- column: item:A.5.13:app_coverage_check -->
<!-- column: item:A.5.13:app_training -->
<!-- column: item:A.5.13:app_owner -->
<!-- column: item:A.5.13:app_enablement_date -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record each time you enable labelling on a new platform or make major changes, ensuring you can show which systems are covered and how labelling was set up.

## When to use it

Use this whenever you bring a new platform into your information environment or make significant changes to an existing one, and update it as needed to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours for each new platform or major reconfiguration, as you’ll need to complete several detailed fields for each entry in the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.13:labelling_application_record -->
| App System Ref | App Scope | App Method | App Coverage Check | App Training | App Owner | App Enablement Date |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.13:labelling_application_record -->

## Column guidance — what to fill in

### App System Ref

<<MUST item:A.5.13:app_system_ref>>
_Why: 27002:5.13 — traceability_

> _Standard text:_ Platform identifier per record (links to coverage register entry)

<<GUIDANCE>>

### App Scope

<<MUST item:A.5.13:app_scope>>
_Why: 27002:5.13 — applied_

> _Standard text:_ Scope per record (which content classes the platform stores)

<<GUIDANCE>>

### App Method

<<MUST item:A.5.13:app_method>>
_Why: 27002:5.13 — implemented_

> _Standard text:_ Enablement method per record (sensitivity-label policy deployed / DLP rule wired / manual-tagging training given)

<<GUIDANCE>>

### App Coverage Check

<<MUST item:A.5.13:app_coverage_check>>
_Why: Program assurance_

> _Standard text:_ Coverage verification per record (sample re-checked post-enablement; legacy items remediated)

<<GUIDANCE>>

### App Training

<<MUST item:A.5.13:app_training>>
_Why: 27002:5.13 — implemented_

> _Standard text:_ Training rollout per record (users of this platform completed labelling refresher; new-joiner integration noted)

<<GUIDANCE>>

### App Owner

<<MUST item:A.5.13:app_owner>>
_Why: Accountability_

> _Standard text:_ Owner per record (platform owner accepts ongoing accountability for labelling on this system)

<<GUIDANCE>>

### App Enablement Date

<<MUST item:A.5.13:app_enablement_date>>
_Why: Operational discipline_

> _Standard text:_ Enablement date recorded

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### App Dlp Wired

<<SHOULD item:A.5.13:app_dlp_wired>>
_Why: Defence-in-depth_

> _Standard text:_ DLP-rule-wired flag per record where the platform supports DLP enforcement of labels

<<GUIDANCE>>

### App Legacy Done

<<SHOULD item:A.5.13:app_legacy_done>>
_Why: Pragmatic adoption_

> _Standard text:_ Legacy-asset remediation completion noted per record (pre-existing items retro-labelled within the timeline)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
