---
leaf_id: req:Art.13:publication_record
control_ref: Art.13
standard_id: GDPR:2016/679
evidence_type: publication_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Privacy Notice Publication Record

> Per-version publication evidence — version number, publication URL / location, effective date, approval. Proves the notice is actually accessible to subjects, not just drafted

<!-- TABLE-COLUMNS leaf:req:Art.13:publication_record -->
<!-- column: item:Art.13:rec_version -->
<!-- column: item:Art.13:rec_publication_url -->
<!-- column: item:Art.13:rec_effective_date -->
<!-- column: item:Art.13:rec_approval -->
<!-- column: item:Art.13:rec_prior_archive -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.13:publication_record -->
| Rec Version | Rec Publication Url | Rec Effective Date | Rec Approval | Rec Prior Archive |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.13:publication_record -->

## Column guidance — what to fill in

### Rec Version

<<MUST item:Art.13:rec_version>>
_Why: Audit trail_

> _Standard text:_ Version identifier per row (when notice content changes)

### Rec Publication Url

<<MUST item:Art.13:rec_publication_url>>
_Why: Art.13.1 — provided at time of collection_

> _Standard text:_ Per-row publication location (URL, app screen, signup flow)

### Rec Effective Date

<<MUST item:Art.13:rec_effective_date>>
_Why: Currency_

> _Standard text:_ Per-row effective date stated

### Rec Approval

<<MUST item:Art.13:rec_approval>>
_Why: Authority_

> _Standard text:_ Per-row approval (DPO / Privacy Lead sign-off)

### Rec Prior Archive

<<MUST item:Art.13:rec_prior_archive>>
_Why: Art.5.2 accountability_

> _Standard text:_ Prior versions retained for audit (proves what subjects saw at the time of collection)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rec Change Summary

<<SHOULD item:Art.13:rec_change_summary>>
_Why: Audit clarity_

> _Standard text:_ Per-row change-summary annotation (what changed vs prior version)
