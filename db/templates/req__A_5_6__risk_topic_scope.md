---
leaf_id: req:A.5.6:risk_topic_scope
control_ref: A.5.6
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# SIG Engagement Risk-Topic Scope

> The upstream that drives the register. Documents the threat categories, technology stack components, sectoral concerns and skill domains that justify each SIG membership. ISO 27002:2022 § 5.6 expects engagement to be relevant — random or legacy memberships fail the test

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Threat categories prioritised (ransomware, supply-chain, insider, sector-specific) that justify SIG choices

<<MUST item:A.5.6:scope_threat_categories>>
_Why: 27002:5.6 — relevant_

<<TEXT>>

## 2. Technology-stack components for which vendor/community SIGs are valuable (cloud, OS, network, OT/IoT)

<<MUST item:A.5.6:scope_tech_stack>>
_Why: 27002:5.6b_

<<TEXT>>

## 3. Sectoral concerns (finance ISAC, health ISAC, critical infra forum) driving sector-specific memberships

<<MUST item:A.5.6:scope_sectoral>>
_Why: 27002:5.6 — relevant_

<<TEXT>>

## 4. Professional development / skill domains (CISO peer groups, secure-coding communities) driving professional memberships

<<MUST item:A.5.6:scope_skill_domains>>
_Why: 27002:5.6_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-link to threat-intelligence procedure (A.5.7) — the two scopes should share drivers

<<SHOULD item:A.5.6:scope_threat_intel_link>>
_Why: Cross-control coherence_

<<TEXT>>

### 2. Trigger for re-scoping (new tech adoption, new sector entry, emerging threat class)

<<SHOULD item:A.5.6:scope_change_trigger>>
_Why: Currency_

<<TEXT>>
