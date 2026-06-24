---
leaf_id: req:A.7.11:supporting_utilities_procedure
control_ref: A.7.11
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Supporting Utilities Continuity Procedure

> A.7.11 requires information processing facilities to be protected from power failures and other supporting-utility disruptions. The procedure documents critical utilities, redundancy, monitoring, maintenance, testing. The utility register, applicable-sites scope and periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Critical utilities identified (power, cooling, water, communications, gas where relevant)

<<MUST item:A.7.11:critical_utilities>>
_Why: 27002:7.11 — supporting utilities_

<<TEXT>>

## 2. Redundancy / backup arrangements per utility (UPS, generator, dual-feed, redundant cooling, dual ISP)

<<MUST item:A.7.11:redundancy>>
_Why: 27002:7.11 — protected_

<<TEXT>>

## 3. Monitoring with alerting for utility status (BMS / power quality / temperature)

<<MUST item:A.7.11:monitoring>>
_Why: 27002:7.11 — protected_

<<TEXT>>

## 4. Maintenance contracts with provider SLAs (UPS battery replacement, generator service)

<<MUST item:A.7.11:maintenance>>
_Why: 27002:7.11 — protected_

<<TEXT>>

## 5. Periodic testing arrangements (UPS run-time tests, generator load tests, ATS transfer tests)

<<MUST item:A.7.11:testing>>
_Why: Continuity validation_

<<TEXT>>

## 6. BCP integration (utility-failure scenarios feed A.5.29/A.5.30 BCP plans)

<<MUST item:A.7.11:bcp_integration>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Alternate-site considerations where redundancy unachievable on-site

<<SHOULD item:A.7.11:alternate_site>>
_Why: Higher-resilience option_

<<TEXT>>
