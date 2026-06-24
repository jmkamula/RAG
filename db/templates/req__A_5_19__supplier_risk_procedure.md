---
leaf_id: req:A.5.19:supplier_risk_procedure
control_ref: A.5.19
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 2
must_count: 8
should_count: 3
---

# Supplier Information Security Risk Management Procedure

## What this template gives you

The **procedure** that governs how you take on, monitor, and exit
suppliers (cloud providers, SaaS vendors, contractors, outsourcers).
Auditors check this exists, that it's actually run on new engagements,
and that ongoing monitoring isn't all-passive. Supplier compromise
is one of the most common breach vectors — a documented procedure
is half the defence.

## When to use it

You're producing the procedure required by **ISO/IEC 27001:2022
A.5.19**. Sits at the top of the supplier control family
(A.5.20-23). Pairs with the supplier register sibling leaf.

## Before you start

- [ ] **6.1.2 Risk Assessment Procedure** in place (supplier risk is
      a category of org risk)
- [ ] **A.5.31 Compliance Register** — supplier obligations + DPA
      requirements live there
- [ ] **A.5.34 PII Protection Policy** — drives DPA + Art.28
      processor agreements

## Cross-references

- **A.5.20 Supplier Agreements** — agreement content
- **A.5.21 ICT Supply Chain** — sub-supplier (4th-party) discipline
- **A.5.22 Supplier Reviews** — ongoing monitoring outputs
- **A.5.23 Cloud Services** — cloud-specific overlay
- **Art.28 GDPR** — processor agreement requirements
- **Art.44-49 GDPR** — cross-border transfer mechanisms

## Estimated effort

**6-10 hours** for v1; **1-2 hours** per supplier added.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Identify and document supplier types

<<MUST item:A.5.19:supplier_types>>
_Type-driven risk — different supplier types carry different risk
profiles + need different controls._

State the supplier categories you have. Each category gets its own
overlay later. Common: ICT services (SaaS, IaaS, PaaS), ICT
infrastructure (hardware, network), professional services
(contractors, consultants), business services (payroll, legal,
audit), logistics, utilities, financial.

**✓ Good**: "Supplier categories: (a) Cloud IaaS (AWS, GCP) — A.5.23
overlay. (b) Cloud SaaS (Okta, Atlassian, Stripe, etc.) — A.5.23
overlay + processor agreement if PII. (c) Contracted personnel
(individual contractors, agency staff). (d) Professional services
(legal, audit, consulting). (e) Business services (payroll
provider). Sub-supplier risk (A.5.21) tracked per primary supplier
where in-scope data flows through chain."

<<TEXT>>

## 2. Define selection + evaluation criteria

<<MUST item:A.5.19:selection_criteria>>
_Risk-proportional intake — high-risk suppliers get more scrutiny
than low-risk._

State the criteria: data sensitivity processed, business
criticality, regulatory implications. Each combination drives the
intake assessment depth.

**✓ Good**: "Selection criteria: (a) Data sensitivity score (Public
1 — Restricted 4). (b) PII handled (none / pseudonymous / direct).
(c) Business criticality (RTO impact). (d) Regulatory implications
(GDPR Art.28 processor, sector-specific). (e) Cross-border transfer
implications. Combined score drives intake tier (Tier 1 light —
Tier 3 deep). Tier 3 requires SOC2 + ISO 27001 + DPA review;
Tier 1 acceptable on questionnaire + standard terms."

<<TEXT>>

## 3. State infosec rules per supplier type / access type

<<MUST item:A.5.19:risk_rules>>
_The minimum bar — what every supplier in a given type must satisfy._

State minimum requirements per category. Auditor checks the matrix
+ samples actual suppliers against it.

**✓ Good** (table):

| Supplier type | Min requirements |
|---|---|
| Cloud IaaS/SaaS holding restricted data | SOC2 Type II + ISO 27001 + DPA + EU/UK data residency or SCC + breach notification < 24h |
| Cloud SaaS holding confidential (non-PII) | SOC2 Type II or ISO 27001 + standard DPA + breach < 72h |
| Contracted personnel | Background check (A.6.1) + NDA (A.6.6) + onboarding security training + access via own identity system |
| Professional services (legal, audit) | NDA + scoped engagement letter + secure data exchange channel |
| Business services (payroll) | DPA (PII) + SOC2 or equivalent + breach < 24h |

<<TEXT>>

## 4. State due-diligence steps before engagement

<<MUST item:A.5.19:due_diligence>>
_Pre-engagement work — what you do BEFORE the contract is signed._

The intake gates. State who does each step + what evidence is
produced.

**✓ Good**: "Due diligence steps: (1) Procurement raises engagement
request with proposed supplier + scope. (2) Security questionnaire
sent (ISMS Manager owns content). (3) Tier scoring (see MUST 2)
performed by ISMS Manager + DPO if PII. (4) Tier-appropriate
evidence reviewed: SOC2 report, ISO certificate, penetration test
summary, public breach history, financial stability check (for
high-criticality). (5) Draft DPA exchange (legal + DPO). (6) Risk
register row created if open items. (7) Sign-off: Tier 3 needs
ISMS Owner + DPO; Tier 1-2 needs ISMS Manager. Engagement contract
cannot be signed before all steps complete."

<<TEXT>>

## 5. Define ongoing monitoring

<<MUST item:A.5.19:ongoing_monitoring>>
_Post-engagement — selection is not enough; the supplier must be
re-evaluated over time._

State: periodic reassessment cadence per tier, event-driven
triggers, third-party reports relied upon. The A.5.22 sibling
captures the review records.

**✓ Good**: "Monitoring approach: (a) Periodic reassessment: Tier 3
annually, Tier 2 every 2 years, Tier 1 every 3 years.
Reassessment refreshes the questionnaire, evidence + tier score.
(b) Continuous: vendor incident notifications, breach disclosures,
SOC2 report renewal review (annual), regulatory enforcement actions
against the supplier. (c) Event triggers: vendor security
incident, M&A, sub-processor change, regulator action against
vendor — each triggers immediate reassessment. (d) A.5.22 review
records sibling leaf captures the outputs."

<<TEXT>>

## 6. Define handoff to supplier agreements (A.5.20)

<<MUST item:A.5.19:agreement_handoff>>
_Conditions when security clauses must enter the contract._

State which findings from the intake assessment must end up in the
contract.

**✓ Good**: "Agreement handoff: All Tier 2 and Tier 3 suppliers
require A.5.20-compliant clauses: (a) DPA (if PII handled — Art.28
compliant); (b) confidentiality + IP terms; (c) breach
notification SLAs (24h Tier 3 / 72h Tier 2); (d) audit
right + on-demand attestation refresh; (e) sub-processor disclosure
+ approval. Tier 1 uses the standard terms baseline. Open items
from intake (e.g. 'vendor doesn't yet have SOC2 — committed by
date X') become contract conditions with milestones."

<<TEXT>>

## 7. Train own personnel on supplier engagement

<<MUST item:A.5.19:training_personnel>>
_People-side control — your staff need to know how to engage
suppliers correctly + handle the data exchange._

State the training programme cross-link.

**✓ Good**: "Personnel training: (a) Engagement-side: procurement,
product, engineering managers receive supplier-engagement training
in onboarding + annual refresh (per A.6.3). Content covers: when
to use this procedure, how to score data sensitivity, the intake
tier table, common pitfalls. (b) Operational-side: anyone handling
data exchange with suppliers (sales engineers, support engineers,
data ops) receives data-exchange-security training: classification
+ encryption + secure channels + retention. (c) Renewal: annual
refresh + immediate on procedure update."

<<TEXT>>

## 8. State incident + contingency handling with the supplier

<<MUST item:A.5.19:incident_joint_mgmt>>
_Incident coordination — what happens when something goes wrong
on either side._

State the bi-directional incident flow + the contingency triggers.

**✓ Good**: "Joint incident handling: (a) Supplier-side breach
affecting our data: vendor notifies per SLA (24h/72h per tier);
we trigger our A.5.24 incident response with vendor as the source;
joint forensic + remediation track; vendor evidence captured per
A.5.28. (b) Our-side incident affecting supplier integration: we
notify the vendor per the agreement's reverse-notification clause
(typically 48h); we coordinate remediation. (c) Contingency: if a
supplier fails (insolvency, sustained outage, security incident
requiring suspension), the A.5.30 ICT-readiness plan covers
service continuity; supplier exit per the A.5.20 termination clauses."

<<TEXT>>

---

## Recommended additions

### Supplier tiering model documented separately

<<SHOULD item:A.5.19:tiering_model>>
_Model rigor — make the tier rubric a separately-maintained
artefact so it can evolve._

The scoring rubric is its own document; this procedure references it.

<<TEXT>>

### Standard questionnaire referenced

<<SHOULD item:A.5.19:questionnaire_ref>>
_Reuse the industry baseline (SIG, CAIQ, or your own)._

State which questionnaire format you use and where it lives.

<<TEXT>>

### Resilience / disengagement plan

<<SHOULD item:A.5.19:resilience_plan>>
_Exit-readiness — what's the plan when the supplier exits or you exit?_

State the disengagement plan reference (typically per-supplier in
A.5.20 / A.5.23 cloud-exit clauses).

<<TEXT>>
