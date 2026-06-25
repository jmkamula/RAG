---
leaf_id: req:A.5.34:pii_processing_register
control_ref: A.5.34
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
table_shape: true
---

# PII Processing Register

> The operational catalog of every processing activity involving PII — what categories, whose, on what legal basis, retained how long, owned by whom, protected how, transferred where. Often shared with (or extended from) the GDPR Art.30 Records of Processing (RoPA) — same operational artefact serves both ISO A.5.34 and GDPR Art.30. Without this register, the privacy policy is theoretical; with it, A.5.34 / Art.30 / Art.25 / Art.5 can all be evidenced from a single source

<!-- TABLE-COLUMNS leaf:req:A.5.34:pii_processing_register -->
<!-- column: item:A.5.34:pii_inventory -->
<!-- column: item:A.5.34:reg_data_subjects -->
<!-- column: item:A.5.34:reg_purposes -->
<!-- column: item:A.5.34:reg_lawful_basis -->
<!-- column: item:A.5.34:reg_retention -->
<!-- column: item:A.5.34:reg_owner_per_activity -->
<!-- column: item:A.5.34:reg_controls_applied -->
<!-- column: item:A.5.34:reg_transfers -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.34:pii_processing_register -->
| Pii Inventory | Reg Data Subjects | Reg Purposes | Reg Lawful Basis | Reg Retention | Reg Owner Per Activity | Reg Controls Applied | Reg Transfers |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.34:pii_processing_register -->

## Column guidance — what to fill in

### Pii Inventory

<<MUST item:A.5.34:pii_inventory>>
_Why: 27002:5.34 — protection of PII / GDPR Art.30.1.c_

> _Standard text:_ PII categories enumerated per processing activity (basic identifiers, contact data, financial, health, biometric, special-category — GDPR Art.9 / sectoral equivalents); links to GDPR Art.30 RoPA

### Reg Data Subjects

<<MUST item:A.5.34:reg_data_subjects>>
_Why: 27002:5.34 — relevant / GDPR Art.30.1.c_

> _Standard text:_ Data subject categories per processing activity (customers, employees, prospects, minors, vulnerable groups — drives extra-safeguard decisions)

### Reg Purposes

<<MUST item:A.5.34:reg_purposes>>
_Why: GDPR Art.30.1.b + Art.5.1.b_

> _Standard text:_ Processing purposes stated per activity (specific, explicit, legitimate — not 'business operations'; cross-link to GDPR Art.5.1.b purpose limitation)

### Reg Lawful Basis

<<MUST item:A.5.34:reg_lawful_basis>>
_Why: GDPR Art.6 + Art.9_

> _Standard text:_ Lawful basis recorded per activity (matches the policy's discipline — consent / contract / legal obligation / vital interests / public task / legitimate interests, with special-category Art.9 basis where applicable)

### Reg Retention

<<MUST item:A.5.34:reg_retention>>
_Why: GDPR Art.30.1.f + A.5.33 coherence_

> _Standard text:_ Retention period per activity (concrete duration with start/end triggers; cross-link to A.5.33 records schedule — no arbitrary numbers)

### Reg Owner Per Activity

<<MUST item:A.5.34:reg_owner_per_activity>>
_Why: Accountability_

> _Standard text:_ Owner per processing activity (named role responsible for the activity — HR for employee processing, Sales for prospect processing, etc.)

### Reg Controls Applied

<<MUST item:A.5.34:reg_controls_applied>>
_Why: GDPR Art.30.1.g + Art.32_

> _Standard text:_ Security controls applied per activity (encryption at rest/in transit, access control class, pseudonymisation where used — cross-link to A.8.x and GDPR Art.32)

### Reg Transfers

<<MUST item:A.5.34:reg_transfers>>
_Why: GDPR Art.30.1.e + Chap V_

> _Standard text:_ Cross-border transfers per activity (destination jurisdictions + legal mechanism — SCCs / adequacy / BCRs / derogations; explicit 'none' where applicable)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Ropa Link

<<SHOULD item:A.5.34:reg_ropa_link>>
_Why: Cross-control coherence_

> _Standard text:_ Direct link to GDPR Art.30 RoPA register where the two are kept as one artefact — saves duplication, prevents drift

### Reg Dpia Status

<<SHOULD item:A.5.34:reg_dpia_status>>
_Why: GDPR Art.35_

> _Standard text:_ DPIA status per activity (required / completed / not required with rationale) — drives high-risk processing reviews

### Reg Last Verified

<<SHOULD item:A.5.34:reg_last_verified>>
_Why: 27002:5.34 — maintained_

> _Standard text:_ Last-verified date per activity (proves the entry is current; missing dates surface stale activities at review)
