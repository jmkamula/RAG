---
leaf_id: req:A.6.6:nda_signature_register
control_ref: A.6.6
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# NDA Signature Register

> The operational catalogue of NDA signings. Each row: signatory identifier, NDA variant signed, template version, signature date. Drives the 'every party with access has signed a current NDA' completeness check; the audit-defensibility gate for A.5.18 access grants to non-employees

<!-- TABLE-COLUMNS leaf:req:A.6.6:nda_signature_register -->
<!-- column: item:A.6.6:reg_signatory_id -->
<!-- column: item:A.6.6:reg_variant -->
<!-- column: item:A.6.6:reg_template_version -->
<!-- column: item:A.6.6:reg_signature_date -->
<!-- column: item:A.6.6:reg_signature_method -->
<!-- column: item:A.6.6:reg_expiry_or_active -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.6:nda_signature_register -->
| Reg Signatory Id | Reg Variant | Reg Template Version | Reg Signature Date | Reg Signature Method | Reg Expiry Or Active |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.6:nda_signature_register -->

## Column guidance — what to fill in

### Reg Signatory Id

<<MUST item:A.6.6:reg_signatory_id>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row signatory identifier (links to identity register A.5.16 for employees; supplier register A.5.19 for contractors; visitor-log for visitors)

### Reg Variant

<<MUST item:A.6.6:reg_variant>>
_Why: 27002:6.6 — proportional_

> _Standard text:_ Per-row NDA variant (employee / contractor / supplier-bilateral / M&A / visitor — matches the template variant_tiers SHOULD)

### Reg Template Version

<<MUST item:A.6.6:reg_template_version>>
_Why: 27002:6.6 — current_

> _Standard text:_ Per-row template version (drives currency check — old-version signers may need re-signing on material template changes)

### Reg Signature Date

<<MUST item:A.6.6:reg_signature_date>>
_Why: 27002:6.6 — before access_

> _Standard text:_ Per-row signature date (proves signing happened BEFORE access granted per A.5.18)

### Reg Signature Method

<<MUST item:A.6.6:reg_signature_method>>
_Why: Audit defensibility_

> _Standard text:_ Per-row signature method (wet / e-signature platform reference — ensures non-repudiation)

### Reg Expiry Or Active

<<MUST item:A.6.6:reg_expiry_or_active>>
_Why: Operational discipline_

> _Standard text:_ Per-row status (active / expired-with-surviving-obligations / superseded-by-new-version)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Termination Link

<<SHOULD item:A.6.6:reg_termination_link>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row cross-link to the offboarding event where applicable (A.6.5 leaver briefing reinforces surviving NDA obligations)

### Reg Breach Log

<<SHOULD item:A.6.6:reg_breach_log>>
_Why: Continual assurance_

> _Standard text:_ Per-row breach log (any suspected breach of NDA terms recorded with investigation outcome and enforcement decision)
