---
leaf_id: req:A.5.13:labelling_application_record
control_ref: A.5.13
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Per-Platform Labelling Application Record

> A.5.13 expects labelling to be applied as the org's information estate grows — every new platform that stores information of any classification level should be brought into scope, not just the platforms IT happened to configure first. The application record evidences each enablement event: platform id, scope, enablement method, coverage verification, training rollout, owner. One record per platform/system onboarding (or major re-config), traceable back to the coverage register

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Platform identifier per record (links to coverage register entry)

<<MUST item:A.5.13:app_system_ref>>
_Why: 27002:5.13 — traceability_

<<TEXT>>

## 2. Scope per record (which content classes the platform stores)

<<MUST item:A.5.13:app_scope>>
_Why: 27002:5.13 — applied_

<<TEXT>>

## 3. Enablement method per record (sensitivity-label policy deployed / DLP rule wired / manual-tagging training given)

<<MUST item:A.5.13:app_method>>
_Why: 27002:5.13 — implemented_

<<TEXT>>

## 4. Coverage verification per record (sample re-checked post-enablement; legacy items remediated)

<<MUST item:A.5.13:app_coverage_check>>
_Why: Program assurance_

<<TEXT>>

## 5. Training rollout per record (users of this platform completed labelling refresher; new-joiner integration noted)

<<MUST item:A.5.13:app_training>>
_Why: 27002:5.13 — implemented_

<<TEXT>>

## 6. Owner per record (platform owner accepts ongoing accountability for labelling on this system)

<<MUST item:A.5.13:app_owner>>
_Why: Accountability_

<<TEXT>>

## 7. Enablement date recorded

<<MUST item:A.5.13:app_enablement_date>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. DLP-rule-wired flag per record where the platform supports DLP enforcement of labels

<<SHOULD item:A.5.13:app_dlp_wired>>
_Why: Defence-in-depth_

<<TEXT>>

### 2. Legacy-asset remediation completion noted per record (pre-existing items retro-labelled within the timeline)

<<SHOULD item:A.5.13:app_legacy_done>>
_Why: Pragmatic adoption_

<<TEXT>>
