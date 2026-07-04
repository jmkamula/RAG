---
leaf_id: req:A.7.3.2:notice_artifact_register
control_ref: A.7.3.2
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Notice Artifact Register

> Per-notice-artifact row — the register of subject-facing privacy notices (public notice, layered notice, just-in-time prompts) with version, effective date, applicable audience. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.2:notice_artifact_register -->
<!-- column: item:A.7.3.2:reg_notice_id -->
<!-- column: item:A.7.3.2:reg_audience -->
<!-- column: item:A.7.3.2:reg_field_coverage -->
<!-- column: item:A.7.3.2:reg_version_effective -->
<!-- column: item:A.7.3.2:reg_signoff -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.2:notice_artifact_register -->
| Reg Notice Id | Reg Audience | Reg Field Coverage | Reg Version Effective | Reg Signoff |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.2:notice_artifact_register -->

## Column guidance — what to fill in

### Reg Notice Id

<<MUST item:A.7.3.2:reg_notice_id>>
_Why: Referenceability_

> _Standard text:_ Unique notice identifier per row

### Reg Audience

<<MUST item:A.7.3.2:reg_audience>>
_Why: §7.3.3 — target audience_

> _Standard text:_ Target audience per row (public / customer / employee / minor / EU / US / etc.)

### Reg Field Coverage

<<MUST item:A.7.3.2:reg_field_coverage>>
_Why: §7.3.2 — type of information_

> _Standard text:_ Field coverage per row (which A.7.3.2 fields the notice covers)

### Reg Version Effective

<<MUST item:A.7.3.2:reg_version_effective>>
_Why: Version tracking_

> _Standard text:_ Version + effective date per row

### Reg Signoff

<<MUST item:A.7.3.2:reg_signoff>>
_Why: Accountability_

> _Standard text:_ DPO + Legal signoff per version

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Url

<<SHOULD item:A.7.3.2:reg_url>>
_Why: §7.3.3 — accessible_

> _Standard text:_ Public URL / distribution channel per row
