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
---

# Periodic Cryptography Program Review

> Periodic verification — approved-algorithms table still current vs NIST/regulator advisories, key-rotation compliance, PII-key audit, exception inventory (freshness=180; cryptographic landscape evolves; PQC transition window)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (≤180 days)

<<MUST item:A.8.24:rev_date>>
_Why: 27002:8.24 — periodic_

<<TEXT>>

## 2. Reviewer identity (Cryptography SME + InfoSec + Data Protection)

<<MUST item:A.8.24:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Algorithm-table currency check vs NIST / national-regulator advisories (deprecated algorithms retired)

<<MUST item:A.8.24:rev_algorithm_currency>>
_Why: 27002:8.24f_

<<TEXT>>

## 4. Key-rotation compliance per key class (no overdue active keys without exception)

<<MUST item:A.8.24:rev_rotation_compliance>>
_Why: 27002:8.24b_

<<TEXT>>

## 5. PII-key audit (custodianship + DPIA alignment + cross-border transfer Art.5.1.f impact)

<<MUST item:A.8.24:rev_pii_audit>>
_Why: GDPR Art.32 / GDPR Art.5.1.f_

<<TEXT>>

## 6. Exception inventory re-confirmed / retired

<<MUST item:A.8.24:rev_exception_inventory>>
_Why: Drift prevention_

<<TEXT>>

## 7. Findings propagated to policy / scope / register

<<MUST item:A.8.24:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.24:rev_next_date>>
_Why: Planning_

<<TEXT>>
