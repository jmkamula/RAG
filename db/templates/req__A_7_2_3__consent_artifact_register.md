---
leaf_id: req:A.7.2.3:consent_artifact_register
control_ref: A.7.2.3
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Consent Mechanism Artifact Register

<<DOC_CONTROL>>

> Per-collection-channel record — the consent-collection artifact (form text, checkbox wording, UI screenshot, verbal script) captured before deployment, versioned on change. Annual review (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.2.3:consent_artifact_register -->
<!-- column: item:A.7.2.3:reg_channel_id -->
<!-- column: item:A.7.2.3:reg_artifact_snapshot -->
<!-- column: item:A.7.2.3:reg_purpose_link -->
<!-- column: item:A.7.2.3:reg_effective_date -->
<!-- column: item:A.7.2.3:reg_review_signoff -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of how and where you collect consent from individuals, including the exact wording or method used. It's useful for tracking changes and ensuring compliance with privacy standards.

## When to use it

Use this register whenever you introduce or update a way of collecting consent, such as a new form, checkbox, or script. Review and update it about once a year, or whenever your consent process changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes to complete the required sections for each consent method you document, with additional time needed as you add more collection channels.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.3:consent_artifact_register -->
| Reg Channel Id | Reg Artifact Snapshot | Reg Purpose Link | Reg Effective Date | Reg Review Signoff |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.3:consent_artifact_register -->

## Column guidance — what to fill in

### Reg Channel Id

<<MUST item:A.7.2.3:reg_channel_id>>
_Why: Traceability_

> _Standard text:_ Channel identifier per row (web signup / iOS app onboarding / support-call recording opt-in)

<<GUIDANCE>>

### Reg Artifact Snapshot

<<MUST item:A.7.2.3:reg_artifact_snapshot>>
_Why: §7.2.4 — record consent_

> _Standard text:_ Consent artifact snapshot (text + UI screenshot + version)

<<GUIDANCE>>

### Reg Purpose Link

<<MUST item:A.7.2.3:reg_purpose_link>>
_Why: §7.2.1 cross-link_

> _Standard text:_ Purpose link (which A.7.2.1 purposes this consent authorises)

<<GUIDANCE>>

### Reg Effective Date

<<MUST item:A.7.2.3:reg_effective_date>>
_Why: Version tracking_

> _Standard text:_ Effective date per artifact version

<<GUIDANCE>>

### Reg Review Signoff

<<MUST item:A.7.2.3:reg_review_signoff>>
_Why: Accountability_

> _Standard text:_ DPO + Legal signoff per artifact version

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Ux Review

<<SHOULD item:A.7.2.3:reg_ux_review>>
_Why: Consent-quality assurance_

> _Standard text:_ UX review notes per version (dark-pattern check)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
