---
leaf_id: req:A.5.7:threat_intelligence_procedure
control_ref: A.5.7
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
---

# Threat Intelligence Programme Procedure

> A.5.7 requires information about information security threats to be collected and analysed to produce threat intelligence across strategic, tactical and operational layers. The procedure documents sources, collection cadence, analysis approach, the three intelligence layers, distribution to named consumers, and the feedback loop into risk and operational controls. The feed register, periodic program review and per-product intelligence records are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Threat intelligence sources enumerated (open-source feeds, vendor feeds, ISACs, government advisories, paid intel services)

<<MUST item:A.5.7:sources>>
_Why: 27002:5.7 — sources establishment_

<<TEXT>>

## 2. Three intelligence layers covered: strategic (sector/long-term), tactical (attacker methodologies/TTPs), operational (specific attack details/IOCs)

<<MUST item:A.5.7:layers>>
_Why: 27002:5.7 — three layers_

<<TEXT>>

## 3. Collection cadence stated per source (continuous, daily, weekly)

<<MUST item:A.5.7:collection_cadence>>
_Why: 27002:5.7 — collection_

<<TEXT>>

## 4. Analysis approach defined (relevance to org assets, integrity verification, completeness, correlation, prioritisation)

<<MUST item:A.5.7:analysis_approach>>
_Why: 27002:5.7 — analysis_

<<TEXT>>

## 5. Intelligence products defined per layer (IOC lists, TTP signatures, threat briefings, sector advisories)

<<MUST item:A.5.7:products>>
_Why: 27002:5.7 — produce threat intelligence_

<<TEXT>>

## 6. Distribution path to named consumers (security ops, IT/network, risk owners, exec briefing)

<<MUST item:A.5.7:distribution>>
_Why: 27002:5.7 — communication_

<<TEXT>>

## 7. Use into technical controls (firewall blocklists, IDS rules, EDR indicators, vulnerability prioritisation)

<<MUST item:A.5.7:control_use>>
_Why: 27002:5.7 — informed defensive action_

<<TEXT>>

## 8. Feedback loop into the risk register / risk assessment (intel that surfaces new exposures triggers reassessment)

<<MUST item:A.5.7:risk_feedback>>
_Why: 27002:5.7 — informed risk treatment_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Outbound intelligence sharing path (ISAC contributions, peer briefings)

<<SHOULD item:A.5.7:sharing>>
_Why: 27002:5.7 — sharing of analysed intel_

<<TEXT>>

### 2. Use into exercises / tabletop scenarios (intel informs realistic scenarios)

<<SHOULD item:A.5.7:exercise_input>>
_Why: 27002:5.7 — exercise planning_

<<TEXT>>

### 3. Retention period for intelligence products stated (often shorter than other compliance records — IOC libraries age fast)

<<SHOULD item:A.5.7:product_retention>>
_Why: Audit + lookback proportional to relevance_

<<TEXT>>
