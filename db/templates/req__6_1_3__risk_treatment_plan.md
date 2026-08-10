---
leaf_id: req:6.1.3:risk_treatment_plan
control_ref: 6.1.3
standard_id: ISO27001:2022
evidence_type: risk_treatment_plan
trigger_type: universal
template_version: 3
must_count: 6
should_count: 1
---

# Risk Treatment Plan

<<DOC_CONTROL>>

## What this template gives you

The **action plan** that turns your risk register into a roadmap.
For every risk you decided to treat (not accept), the plan names the
treatment option (Modify / Avoid / Share / Retain), the controls
selected, who owns delivery, the target completion date, and the
residual risk after treatment. Auditors trace risks → plan → SoA →
implemented controls. Gaps anywhere in that chain are findings.

## When to use it

You're producing the Risk Treatment Plan required by **ISO/IEC 27001:2022 Clause 6.1.3**. This template covers the *plan itself*;
the **Statement of Applicability** (a sibling 6.1.3 leaf, mandatory
under 6.1.3(c-d)) is a separate template.

## Prerequisites

<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

**4-6 hours** for v1 (after the risk register is populated); **1-2 hours** for refresh on register updates.

---

## 1. Select a risk-treatment option per risk

<<MUST item:6.1.3:options>>

> _Standard text:_ Risk treatment options selected for each risk

_Clause 6.1.3(a) — treatment options selected._

For each risk **flagged for treatment** in the register, name the option: **Modify** (apply controls), **Avoid** (stop the activity),
**Share** (transfer to insurer / outsource), or **Retain** (formal
accept). Most rows are "Modify" — apply controls.

**✓ Good**: "Risk R-042 (cloud-provider data-region misconfiguration
causing GDPR transfer violation) — Option: Modify. Risk R-018
(legacy hosted-billing payment data) — Option: Avoid (migrate to
PCI-scoped processor + decommission legacy by Q3). Risk R-007
(supply-chain compromise via build-tooling) — Option: Share
(cyber insurance covers post-breach response costs) + Modify
(SBOM + signed builds reduce likelihood)."

**✗ Avoid**: Implicit treatment ("we'll deploy controls") with no
named option.

<<GUIDANCE>>

<<TEXT>>

## 2. Determine controls for each chosen option

<<MUST item:6.1.3:controls>>

> _Standard text:_ Controls determined to implement the chosen options

_Clause 6.1.3(b) — controls determined to implement the option._

For each "Modify" row, name **which controls** (Annex A or otherwise)
will be applied. This is the link to the SoA.

**✓ Good**: "R-042 controls: A.5.23 (cloud-services policy and
review), A.8.32 (change-management oversight on region configs),
Art.44 (transfer principle in DPA with cloud provider). R-007
controls: A.5.21 (ICT supply chain risk), A.8.27 (architecture
principles for build pipeline), A.8.28 (secure coding) + custom
'signed-build / SBOM' control listed in SoA as an additional
control beyond Annex A."

<<GUIDANCE>>

<<TEXT>>

## 3. Reference the Statement of Applicability

<<MUST item:6.1.3:soa_ref>>

> _Standard text:_ Reference to the live Statement of Applicability (the SoA leaf)

_Clause 6.1.3(c-d) — produce the SoA._

State that the SoA is the companion artefact and link to the sibling
leaf. Every treatment-plan row should resolve to a control marked
"Applicable / Implemented (or Planned)" in the SoA.

**✓ Good**: "This plan is paired with the Statement of Applicability
(req:6.1.3:statement_of_applicability) — the SoA enumerates all 93
Annex A controls + any additional controls. Each treatment row here
references the controls by their SoA identifier."

<<GUIDANCE>>

<<TEXT>>

## 4. Identify residual risk per treated risk

<<MUST item:6.1.3:residual>>

> _Standard text:_ Residual risk identified per treated risk

_Clause 6.1.3(e) — residual risk identified._

After the treatment is in place, what risk REMAINS? Score it with
the same matrix used in 6.1.2. A treatment can't reduce risk to
zero — name what's left so the residual is consciously accepted.

**✓ Good**: "R-042 residual: After A.5.23 review cadence and
A.8.32 oversight, residual likelihood reduced from 4 → 2; impact
unchanged at 4. New score 8 (yellow). R-007 residual: After signed
builds + SBOM, residual likelihood 2 (down from 3); impact 4. New
score 8 (yellow). Both residuals at-or-below acceptance criteria."

**✗ Avoid**: Treating "treatment selected" as if it equals "risk
eliminated."

<<GUIDANCE>>

<<TEXT>>

## 5. Identify treatment owners

<<MUST item:6.1.3:owners>>

> _Standard text:_ Risk treatment owners identified per treated risk

_Accountability — who delivers the treatment._

The **treatment owner** is the role responsible for *getting the
controls implemented*. Often different from the **risk owner** (who
accepts residual). Be explicit.

**✓ Good**: "R-042 treatment owner: Platform Engineering Lead
(implementation of A.5.23 review cadence + A.8.32 hooks). Risk
owner (residual acceptance): VP Engineering. R-018 treatment owner:
Billing Product Manager (migration). Risk owner: CFO."

<<GUIDANCE>>

<<TEXT>>

## 6. Capture risk-owner approval + residual acceptance

<<MUST item:6.1.3:approval>>

> _Standard text:_ Risk owners' approval of the plan AND acceptance of residual risks recorded

_Clause 6.1.3(f) — approval + acceptance of residual._

Each risk owner formally **approves the treatment plan** (says yes to the controls) AND **accepts the residual risk** (says yes to what's
left). Both signatures, both dated.

**✓ Good**: "Per-risk approval record: each row in the plan has
columns 'Treatment Approved by / on' and 'Residual Accepted by /
on'. Owners sign via the ISMS workflow tool; signatures retained as
the audit artefact."

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

### Target completion dates per treatment item

<<SHOULD item:6.1.3:timeline>>

> _Standard text:_ Target completion dates per treatment item

_Implementation tracking — turn the plan into a schedule._

Each treatment row gets a target date (when the control will be
"implemented" in the SoA). Slippage is visible in 9.1 metrics +
escalates to 10.1.

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
