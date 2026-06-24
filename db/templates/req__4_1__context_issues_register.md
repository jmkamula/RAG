---
leaf_id: req:4.1:context_issues_register
control_ref: 4.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Internal and External Issues Register

> Clause 4.1 requires the organization to determine external and internal issues relevant to its ISMS purpose and outcomes. The register is the canonical artefact — issue rows with internal/external classification, relevance to ISMS outcomes, owner, last assessment date. Sibling leaves: identification framework, applicable-domains scope, program review

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Internal issues documented per row (organizational culture, governance, contracts, capabilities, technologies)

<<MUST item:4.1:internal_issues>>
_Why: Clause 4.1 — internal issues_

<<TEXT>>

## 2. External issues documented per row (regulatory, market, threat landscape, social, technology trends)

<<MUST item:4.1:external_issues>>
_Why: Clause 4.1 — external issues_

<<TEXT>>

## 3. Relevance to ISMS intended outcomes stated per issue

<<MUST item:4.1:relevance_to_ismsm>>
_Why: Clause 4.1 — affect ability to achieve outcomes_

<<TEXT>>

## 4. Named owner of the register (typically ISMS Manager)

<<MUST item:4.1:owner>>
_Why: Accountability_

<<TEXT>>

## 5. Last assessment date per issue row (drives staleness detection)

<<MUST item:4.1:reg_last_assessed>>
_Why: Currency_

<<TEXT>>

## 6. Per-issue handoff to the risk assessment (6.1.2) where relevance warrants it

<<MUST item:4.1:reg_risk_handoff>>
_Why: Cross-clause coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Time-horizon column per issue (near-term vs long-term)

<<SHOULD item:4.1:reg_horizon>>
_Why: Planning visibility_

<<TEXT>>
