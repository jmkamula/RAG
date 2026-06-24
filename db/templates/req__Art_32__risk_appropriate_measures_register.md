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
---

# Art.32 Risk-Appropriate T&O Measures Register

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

## Before you start

- [ ] **Art.30 RoPA** populated — drives the activity-row list
- [ ] **6.1.2 Risk Assessment** + register — risk scores per
      processing activity
- [ ] **6.1.3 SoA** — ISO 27001 controls per activity to
      cross-reference
- [ ] **A.5.7 Threat Intelligence** — informs risk scoring

## Cross-references

- **Art.30 RoPA** — activity-row source
- **Art.5.1.f** — security-of-processing principle (derives_from
  Art.32)
- **6.1.2 / 6.1.3** — risk methodology + treatment
- **A.5.15-18** — access controls referenced
- **A.5.24 + A.5.27 + A.5.28** — IR + lessons + evidence
- **A.5.30 ICT Readiness** — restoration capability
- **A.8.13 Backup** — backup discipline
- **A.8.24 Cryptography** — encryption discipline

## Estimated effort

**8-16 hours** for v1 (per-activity risk scoring + measures
mapping); **2-4 hours** for annual refresh.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Cross-reference each row to a RoPA activity

<<MUST item:Art.32:reg_activity_id>>
_RoPA linkage — every Art.32 row maps to an Art.30 activity._

State the activity-ID column convention + the source-of-truth
cross-reference.

**✓ Good** (sample rows):

| Activity ID | RoPA activity name |
|---|---|
| ACT-001 | Customer-account management |
| ACT-002 | Customer service-content processing (processor role) |
| ACT-003 | Marketing prospect engagement |
| ACT-004 | HR / payroll |
| ACT-005 | Customer support |
| ACT-006 | Account-security monitoring |

Each row's Activity-ID resolves to the row of the same ID in the
Art.30 RoPA register.

<<TEXT>>

## 2. Score risk to rights and freedoms per activity

<<MUST item:Art.32:reg_risk_assessment>>
_Per-activity risk — Art.32 requires measures **appropriate to
the risk**; the risk scoring is the input._

Score risk per Art.32 lens: likelihood × severity of harm to data
subjects. Distinct from generic ISO risk scoring (which is to the
org). Recital 75 lists the harm categories.

**✓ Good** (sample row):

| Activity | Likelihood | Severity (to subject) | Score | Notes |
|---|---|---|---|---|
| ACT-001 customer-account mgmt | Medium (3) | Medium (3) — identifiers + account |
| ACT-002 service-content (processor) | Medium (3) | High (4) — sensitive customer content possible | 12 |
| ACT-006 account-security monitoring | Low-medium (2) | Medium (3) — behavioural / IP | 6 |

Severity reasoning: harm types per Recital 75 — discrimination,
identity theft / fraud, financial loss, damage to reputation, loss
of confidentiality, unauthorised reversal of pseudonymisation,
restriction of rights.

<<TEXT>>

## 3. List per-row T&O measures applied

<<MUST item:Art.32:reg_measures>>
_The specific measures per activity — pseudonymisation /
encryption / CIA / resilience / restoration / regular testing
(Art.32.1.a-d)._

For each activity, name the specific measures.

**✓ Good** (sample row): "ACT-001 customer-account mgmt:
(a) **Pseudonymisation** — account identifiers separated from
session activity (user-ID hashed in event logs). (b)
**Encryption** — TLS 1.2+ in transit; AES-256 at rest in
RDS + S3 + EBS. (c) **CIA** — RBAC + MFA (A.5.15-18 + A.5.17);
audit logging (A.8.15); immutable backup (A.8.13). (d)
**Resilience** — multi-AZ deployment; auto-failover. (e)
**Restoration** — point-in-time recovery up to 35 days; tested
quarterly per A.5.30. (f) **Testing** — A.5.24 IR exercises
quarterly; pen-test annually + on major change."

<<TEXT>>

## 4. Justify appropriateness per row

<<MUST item:Art.32:reg_appropriateness>>
_"Appropriate to the risk" — Art.32.1 requires the org to weigh
state of the art, cost of implementation, nature/scope/context/
purposes, and risk._

For each row, state the appropriateness reasoning. This is the
hardest column to write — but it's the one regulators reach for
when sampling.

**✓ Good** (sample row): "ACT-002 service-content (score 12):
The measures applied are appropriate because: (a) **State of the
art** — TLS 1.3 deployed where possible; AES-256-GCM is
contemporary baseline; KMS envelope encryption + automatic key
rotation. (b) **Cost** — measures are commodity at our scale
(included in cloud-provider SLAs); incremental cost of higher
intensity (e.g. client-side encryption per-customer) judged
disproportionate to incremental risk reduction. (c) **Nature /
scope / purposes** — processor role with customer-provided
content; instruction-bound; data-minimisation is the customer's
responsibility per DPA. (d) **Risk to subjects** — score 12
(yellow) within accepted tier; controls reduce residual to 6
(green). The state-of-the-art evaluation is reviewed annually +
on threat-landscape change (A.5.7)."

**✗ Avoid**: "Appropriate measures are in place" (says nothing about
*why*).

<<TEXT>>

## 5. Name per-row owner

<<MUST item:Art.32:reg_owner>>
_Accountability per activity — the role that owns the
measures-design + sign-off._

State owner per row. Typically the product / system owner is
operational; DPO co-signs.

**✓ Good**: "Per-activity owners: ACT-001 customer-account —
Customer Success Director + DPO co-sign. ACT-002 service-content
— CTO + DPO. ACT-006 account-security monitoring — SecOps
Manager + DPO. Annual review: owner attests the measures are
still appropriate given current risk + current state of the art."

<<TEXT>>

---

## Recommended additions

### ISO control mapping per row

<<SHOULD item:Art.32:reg_iso_mapping>>
_ISO ↔ GDPR cross-reference — Art.32 measures map to ISO 27001
Annex A controls._

For each measure, name the implementing ISO control. Lets the
ISO certification work double for GDPR Art.32 evidence.

**✓ Good** (sample): "ACT-001 ISO mapping: encryption →
A.8.24; access control → A.5.15-18; audit logging → A.8.15;
backup → A.8.13; resilience + restoration → A.5.30; IR →
A.5.24-28; pseudonymisation → A.8.11."

<<TEXT>>
