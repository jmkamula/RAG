---
leaf_id: req:Art.6:lawful_basis_register
control_ref: Art.6
standard_id: GDPR:2016/679
evidence_type: lawful_basis_register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Lawful Basis Register (Art.6)

> Art.6 obliges the controller to be able to point to a specific lawful basis per processing activity. The register (or RoPA extension) listing each activity with the chosen basis, justification, and supporting records is the canonical Art.6 artefact. Sibling direct-evidence leaves: determination procedure, applicable activities scope, program review

<!-- TABLE-COLUMNS leaf:req:Art.6:lawful_basis_register -->
<!-- column: item:Art.6:activities_enumerated -->
<!-- column: item:Art.6:basis_per_activity -->
<!-- column: item:Art.6:justification -->
<!-- column: item:Art.6:consent_link -->
<!-- column: item:Art.6:lia_link -->
<!-- column: item:Art.6:owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.6:lawful_basis_register -->
| Activities Enumerated | Basis Per Activity | Justification | Consent Link | Lia Link | Owner |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.6:lawful_basis_register -->

## Column guidance — what to fill in

### Activities Enumerated

<<MUST item:Art.6:activities_enumerated>>
_Why: Art.6.1 — basis applies per activity_

> _Standard text:_ Processing activities enumerated (links to Art.30 RoPA)

### Basis Per Activity

<<MUST item:Art.6:basis_per_activity>>
_Why: Art.6.1 — at least one of (a)-(f) applies_

> _Standard text:_ Chosen lawful basis named per activity (one of Art.6.1.a-f)

### Justification

<<MUST item:Art.6:justification>>
_Why: Art.5.2 accountability_

> _Standard text:_ Justification recorded for the chosen basis per activity

### Consent Link

<<MUST item:Art.6:consent_link>>
_Why: Art.7 — conditions for consent_

> _Standard text:_ For consent-based activities, link to Art.7 consent capture record

### Lia Link

<<MUST item:Art.6:lia_link>>
_Why: Art.6.1.f — overriding interests test_

> _Standard text:_ For legitimate-interests activities, link to LIA (necessity + balance test)

### Owner

<<MUST item:Art.6:owner>>
_Why: Accountability_

> _Standard text:_ Named owner of the register (typically DPO or Privacy Lead)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reviewed

<<SHOULD item:Art.6:reviewed>>
_Why: Accountability — kept current_

> _Standard text:_ Register reviewed within freshness window when activities or bases change

### Basis Change Log

<<SHOULD item:Art.6:basis_change_log>>
_Why: Art.5.2 + Art.13 alignment_

> _Standard text:_ Log of lawful basis changes per activity (drives Art.13 notice amendments)
