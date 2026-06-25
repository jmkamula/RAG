---
leaf_id: req:6.1.2:risk_assessment
control_ref: 6.1.2
standard_id: ISO27001:2022
evidence_type: risk_assessment
trigger_type: universal
template_version: 3
must_count: 8
should_count: 2
---

# Information Security Risk Assessment Procedure

## What this template gives you

The **methodology document** that explains *how* you assess
information-security risk — criteria, identification, analysis,
evaluation. The risk *register* (a sibling leaf) is the running
output; this template is the recipe. Auditors check that the
methodology is repeatable (same input → same output) and that the
register actually follows it.

## When to use it

You're authoring the risk-assessment procedure required by **ISO/IEC
27001:2022 Clause 6.1.2**. A weak or absent procedure causes one of
the most common audit findings — "your risk register exists but how
did you decide what's on it?"

## Before you start

- [ ] **4.3 ISMS Scope** — risk assessment runs within scope
- [ ] **5.2 InfoSec Policy** — risk-acceptance criteria align with
      objectives stated there
- [ ] **5.3 Roles** — risk owners must be a defined role with
      authority to accept residual risk
- [ ] Have an **A.5.9 asset register** under way — risks attach to
      assets

## Cross-references

- **6.1.3 Risk Treatment Plan + SoA** — the procedure's output feeds
  treatment selection
- **6.1.1 Risks and opportunities** — sets the upstream framing
- **Art.32 + Art.35 (GDPR)** — personal-data processing requires
  risk-based T&O measures + DPIA for high-risk processing; the
  procedure must accommodate both ISO + GDPR contexts
- **9.1 monitoring + 9.3 management review** — the procedure's
  outputs are reviewed inputs

## Estimated effort

**4-8 hours** for v1; **1-2 hours** for refresh. Plan additional time
for the first full run of the procedure to build the live register.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Define risk acceptance criteria

<<MUST item:6.1.2:criteria>>

> _Standard text:_ Risk acceptance criteria defined

_Clause 6.1.2(a) — criteria for accepting risks._

State the thresholds for **what risk levels are acceptable** without
treatment. Common shape: a likelihood × impact matrix with explicit
"green / yellow / red" zones and authority levels per zone.

**✓ Good**: "Risk acceptance criteria: (a) Green (likelihood × impact
score 1-5): accepted at risk-owner level. (b) Yellow (6-15): accepted
at ISMS Manager + risk-owner. (c) Red (16-25): accepted only by ISMS
Owner with treatment-plan exception. No 'red' personal-data risk
accepted without DPO sign-off. Acceptance is recorded in the risk
register with the accepting role, date, and review date."

**✗ Avoid**: "Risks are accepted based on management judgement"
(non-repeatable; fails consistency MUST 2).

<<TEXT>>

## 2. Make results consistent and comparable

<<MUST item:6.1.2:consistency>>

> _Standard text:_ Consistent and comparable results produced

_Clause 6.1.2(b) — produces consistent, valid and comparable results._

The procedure must say *how* different assessors will reach similar
results on similar risks. Common: published rubrics for likelihood
levels + impact categories, calibrated examples, peer review.

**✓ Good**: "Consistency mechanisms: (a) Likelihood scale defined as
1=once-in-10-years … 5=monthly-or-more-frequent, with calibrating
examples. (b) Impact across CIA dimensions scored separately, then
combined per the impact-aggregation rule (highest, not sum).
(c) Every risk peer-reviewed by a second assessor before entering
the register. (d) Annual re-calibration exercise at management
review."

**✗ Avoid**: Numerical scales with no anchor descriptions (different
assessors will pick different numbers).

<<TEXT>>

## 3. Identify CIA risks

<<MUST item:6.1.2:identification>>

> _Standard text:_ Risks to confidentiality, integrity and availability identified

_Clause 6.1.2(c) — risks to confidentiality, integrity, availability._

State the **identification techniques** — asset-based, threat-based,
scenario-based — and how all three CIA dimensions are covered. Many
orgs over-weight confidentiality and under-weight integrity /
availability.

**✓ Good**: "Identification techniques: (a) Asset-driven — every
asset in the A.5.9 register has its CIA-risk pass annually. (b)
Threat-driven — annual review against MITRE ATT&CK + ENISA threat
landscape. (c) Scenario-driven — top-10 scenarios reviewed
quarterly (data breach, ransomware, vendor compromise, insider, etc.).
Confidentiality, Integrity and Availability are scored separately on
each risk."

<<TEXT>>

## 4. Identify risk owners

<<MUST item:6.1.2:owners>>

> _Standard text:_ Risk owners identified

_Clause 6.1.2(c) — risk owners identified._

Every risk in the register has **one named owner** with authority to
accept or treat. Ownership flows from asset / process ownership;
don't park risks centrally on the ISMS team.

**✓ Good**: "Each risk has exactly one risk owner — typically the
business or product owner of the affected asset or process.
Ownership rules: (a) Platform/infra risks → owned by VP Engineering.
(b) Product feature risks → owned by Product Manager. (c) Personal
data risks → owned by DPO (with business co-owner). Ownership is
not delegated to 'the security team' — security ADVISES and
TRACKS; owners DECIDE."

**✗ Avoid**: All risks owned by CISO / ISMS Manager (central
ownership defeats the point of distributed risk management).

<<TEXT>>

## 5. Analyse potential consequences

<<MUST item:6.1.2:consequences>>

> _Standard text:_ Potential consequences analysed

_Clause 6.1.2(d) — potential consequences analysed._

For each risk, the consequence dimensions you analyse and how you
score them. Beyond financial loss: regulatory penalty, customer
trust, operational disruption, personal-data harm to subjects.

**✓ Good**: "Consequence dimensions analysed per risk: (1) Direct
financial loss. (2) Regulatory exposure (GDPR fines up to 4% of
revenue or €20M for serious processor breaches; sector-specific
penalties). (3) Customer trust / contract default. (4) Operational
disruption (RTO/RPO breach). (5) Harm to data subjects (rights
infringement; potential to cause physical, material, or non-material
damage per GDPR Recital 75)."

<<TEXT>>

## 6. Assess realistic likelihood

<<MUST item:6.1.2:likelihood>>

> _Standard text:_ Realistic likelihood assessed

_Clause 6.1.2(d) — realistic likelihood assessed._

Likelihood is your most-cited audit weakness. State the data sources
that ground likelihood estimates (incident history, threat intel,
sector reports) so it isn't pure gut feel.

**✓ Good**: "Likelihood is informed by: (a) Our own incident history
(last 24 months). (b) A.5.7 threat-intel feeds. (c) Sector reports
(Verizon DBIR, ENISA Threat Landscape, ICO published cases). (d)
Peer comparison via the CISO-share programme. The likelihood score
rationale is recorded in the register cell."

<<TEXT>>

## 7. Evaluate risks against acceptance criteria

<<MUST item:6.1.2:evaluation>>

> _Standard text:_ Risks evaluated against acceptance criteria

_Clause 6.1.2(e) — evaluated against the criteria from MUST 1._

This MUST closes the loop: each assessed risk has a clear
accept-or-treat decision driven by MUST 1's criteria.

**✓ Good**: "Evaluation flow: each risk is scored (impact ×
likelihood), placed in green/yellow/red, the acceptance authority
runs the criteria check, and the outcome ('accept' or 'treat') is
recorded in the register with date + decider. Risks that move
between zones at re-assessment trigger a treatment-plan review."

<<TEXT>>

## 8. Address personal-data processing risks explicitly

<<MUST item:6.1.2:personal_data>>

> _Standard text:_ Personal data processing risks explicitly addressed

_GDPR alignment — Art.32 requires risk-based T&O measures, Art.35
requires DPIA for high-risk processing._

Personal-data risks need a distinct lane in the procedure: they
have different consequence dimensions (data-subject harm) and
different regulatory triggers (DPIA at high-risk threshold per
Art.35 + EDPB criteria).

**✓ Good**: "Personal-data risks follow the standard procedure with
two overlays: (a) Consequence scoring adds the 'harm to data
subjects' dimension per GDPR Recital 75. (b) Any risk scoring
yellow-or-red on PII + meeting the Art.35 high-risk criteria
(systematic monitoring, large-scale special category, etc.) triggers
a DPIA before treatment selection. DPO is the co-owner on all
personal-data risks."

<<TEXT>>

---

## Recommended additions

### Reference the methodology you base this on

<<SHOULD item:6.1.2:methodology>>

> _Standard text:_ Methodology documented (ISO 31000, NIST SP 800-30, or equivalent)

_Repeatability — readers should be able to trace your approach to a
recognised methodology._

Most orgs base their procedure on ISO 31000, NIST SP 800-30, OCTAVE,
or FAIR. Name yours + cite where your adaptations diverge.

<<TEXT>>

### State assessment date + next review date

<<SHOULD item:6.1.2:date>>

> _Standard text:_ Assessment date and next review date

_Document-control discipline — required by Clause 7.5._

Standard top-of-document metadata.

<<TEXT>>
