---
leaf_id: req:A.8.24:crypto_program_review
control_ref: A.8.24
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 1
table_shape: true
---

# Periodic Cryptography Program Review

> Periodic verification — approved-algorithms table still current vs NIST/regulator advisories, key-rotation compliance, PII-key audit, exception inventory (freshness=180; cryptographic landscape evolves; PQC transition window)

<!-- TABLE-COLUMNS leaf:req:A.8.24:crypto_program_review -->
<!-- column: item:A.8.24:rev_date -->
<!-- column: item:A.8.24:rev_reviewer -->
<!-- column: item:A.8.24:rev_algorithm_currency -->
<!-- column: item:A.8.24:rev_rotation_compliance -->
<!-- column: item:A.8.24:rev_pii_audit -->
<!-- column: item:A.8.24:rev_exception_inventory -->
<!-- column: item:A.8.24:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.24:crypto_program_review -->
| Rev Date | Rev Reviewer | Rev Algorithm Currency | Rev Rotation Compliance | Rev Pii Audit | Rev Exception Inventory | Rev Findings Update |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.24:crypto_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.24:rev_date>>
_Why: 27002:8.24 — periodic_

> _Standard text:_ Review date within the planned interval (≤180 days)

### Rev Reviewer

<<MUST item:A.8.24:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Cryptography SME + InfoSec + Data Protection)

### Rev Algorithm Currency

<<MUST item:A.8.24:rev_algorithm_currency>>
_Why: 27002:8.24f_

> _Standard text:_ Algorithm-table currency check vs NIST / national-regulator advisories (deprecated algorithms retired)

### Rev Rotation Compliance

<<MUST item:A.8.24:rev_rotation_compliance>>
_Why: 27002:8.24b_

> _Standard text:_ Key-rotation compliance per key class (no overdue active keys without exception)

### Rev Pii Audit

<<MUST item:A.8.24:rev_pii_audit>>
_Why: GDPR Art.32 / GDPR Art.5.1.f_

> _Standard text:_ PII-key audit (custodianship + DPIA alignment + cross-border transfer Art.5.1.f impact)

### Rev Exception Inventory

<<MUST item:A.8.24:rev_exception_inventory>>
_Why: Drift prevention_

> _Standard text:_ Exception inventory re-confirmed / retired

### Rev Findings Update

<<MUST item:A.8.24:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to policy / scope / register

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.24:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
