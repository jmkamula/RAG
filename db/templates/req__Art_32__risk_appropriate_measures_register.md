---
leaf_id: req:Art.32:risk_appropriate_measures_register
control_ref: Art.32
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
template_version: 2
must_count: 5
should_count: 1
freshness_days: 365
table_shape: true
---

# Art.32 Risk-Appropriate T&O Measures Register

<<DOC_CONTROL>>

## What this template gives you

The **per-activity ledger** of technical and organisational
security measures justifying that they are *appropriate to the
risk* — the language Art.32 uses. Where Art.30 RoPA lists what
processing happens, this register defends why the security on top
of each activity is enough. Pairs with the ISO 27001 control set
via the iso_mapping column. Regulators sampling Art.32 compliance
trace processing → risk → measures → appropriateness justification.

## When to use it

You're producing the register required by **GDPR Article 32**.
Annual refresh minimum (freshness 365d). One row per RoPA
processing activity (cross-references the Art.30 register).

## Prerequisites

<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

**8-16 hours** for v1 (per-activity risk scoring + measures mapping); **2-4 hours** for annual refresh.

---

<!-- TABLE-COLUMNS leaf:req:Art.32:risk_appropriate_measures_register -->
<!-- column: item:Art.32:reg_activity_id -->
<!-- column: item:Art.32:reg_risk_assessment -->
<!-- column: item:Art.32:reg_measures -->
<!-- column: item:Art.32:reg_appropriateness -->
<!-- column: item:Art.32:reg_owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per processing activity (cross-referenced to your Art.30
RoPA row IDs). Each column maps to a MUST item — empty columns count
as unsatisfied. The hardest column to write is **Appropriateness** —
but it's the one regulators read first.

<!-- EDIT-ZONE-START leaf:req:Art.32:risk_appropriate_measures_register -->
| RoPA Activity ID | Risk (L × S to subject) | T&O Measures Applied | Appropriateness Justification | Owner |
|---|---|---|---|---|
|                  |                         |                      |                               |       |
|                  |                         |                      |                               |       |
|                  |                         |                      |                               |       |
<!-- EDIT-ZONE-END leaf:req:Art.32:risk_appropriate_measures_register -->

## Column guidance — what to fill in

### RoPA Activity ID

<<MUST item:Art.32:reg_activity_id>>

> _Standard text:_ Per-row processing activity (Art.30 RoPA
> cross-reference)

Same activity-ID convention you use in the Art.30 RoPA register.
Every Art.32 row resolves 1:1 to a RoPA row.

**✓ Good**: `ACT-001` (customer-account mgmt — see Art.30 row),
`ACT-002` (service-content processor role), `ACT-006`
(account-security monitoring)

**✗ Avoid**: Inventing new IDs not in the RoPA — the auditor
cross-checks both registers and any mismatch is a finding.

<<GUIDANCE>>

### Risk (L × S to subject)

<<MUST item:Art.32:reg_risk_assessment>>

> _Standard text:_ Per-row risk-to-rights-and-freedoms assessment
> (likelihood + severity)

Score risk per Art.32 lens: **likelihood × severity of harm to data subjects** (distinct from generic ISO risk-to-org). Recital 75 lists
the harm categories: identity theft, financial loss, reputation,
loss of confidentiality, restriction of rights, etc.

**✓ Good**: `L=3 / S=3 → 9 (yellow). Severity reasoning: identifiers
+ account info; harm category per R.75 = restriction of rights /
reputation damage.`

**✗ Avoid**: Just a number without the dimension breakdown — the
appropriateness justification depends on which harm type drives the
score.

<<GUIDANCE>>

### T&O Measures Applied

<<MUST item:Art.32:reg_measures>>

> _Standard text:_ Per-row T&O measures applied (pseudonymisation /
> encryption / CIA / resilience / restoration)

The specific Art.32.1(a-d) measures: **(a)** pseudonymisation / encryption, **(b)** ongoing CIA + resilience, **(c)** restore availability after incident, **(d)** regular testing.

**✓ Good**: `(a) TLS 1.2+, AES-256, pseudonymous user-ID in event
logs; (b) RBAC + MFA per A.5.15-18, audit log per A.8.15; (c)
multi-AZ + PIT recovery 35d per A.5.30; (d) IR exercises quarterly
+ pentest annual per A.5.24.`

**✗ Avoid**: "Appropriate measures in place" — too vague to audit.

<<GUIDANCE>>

### Appropriateness Justification

<<MUST item:Art.32:reg_appropriateness>>

> _Standard text:_ Per-row appropriateness justification (state of
> art / cost / nature of processing weighted against risk)

The **hardest column to write** but the one regulators sample. Art.32.1 requires you to weigh: **state of the art**, **cost of implementation**, **nature/scope/context/purposes**, **risk to subjects**. Cover all four.

**✓ Good**: "Score 12 (yellow) within accepted tier. Measures
appropriate because: (a) state of art — TLS 1.3 deployed; AES-256
contemporary baseline; KMS auto-rotate. (b) Cost — measures are
commodity at our scale, included in cloud SLAs. (c) Nature/scope —
processor role; instruction-bound. (d) Risk — controls reduce
residual to 6 (green). Reviewed annually + on threat-landscape
change."

**✗ Avoid**: Generic statements like "measures are appropriate to the
risk" — no auditor will accept that.

<<GUIDANCE>>

### Owner

<<MUST item:Art.32:reg_owner>>

> _Standard text:_ Per-row owner

Per-activity owner. Operational owner (system / product) + DPO
co-sign. Annual review: owner attests the measures are still
appropriate given current risk + current state of the art.

**✓ Good**: `Customer Success Director + <<DPO_NAME>> (co-sign)`

**✗ Avoid**: "Security team" — un-actionable.

---

<<GUIDANCE>>

## Recommended additional columns

_These strengthen the register but aren't strictly required for the
MUST checks. Add them as extra columns in the table if they apply._

### ISO Mapping

<<SHOULD item:Art.32:reg_iso_mapping>>

> _Standard text:_ ISO control mapping per row (ISO ↔ GDPR
> cross-reference — Art.32 measures map to ISO 27001 Annex A
> controls)

Lets the ISO certification work double for GDPR Art.32 evidence.

**Example**: `Encryption → A.8.24; Access control → A.5.15-18; Audit
logging → A.8.15; Backup → A.8.13; Resilience + restoration → A.5.30;
IR → A.5.24-28; Pseudonymisation → A.8.11.`

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
