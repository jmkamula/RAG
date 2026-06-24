---
leaf_id: req:A.7.12:cabling_register
control_ref: A.7.12
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Cabling Run Register

> The catalogue of cabling runs (or aggregations) — site, run id, carried traffic class, routing class, last inspection

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row run identifier

<<MUST item:A.7.12:reg_run_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-row site

<<MUST item:A.7.12:reg_site>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 3. Per-row carried traffic class (drives encryption + tamper-evidence requirements)

<<MUST item:A.7.12:reg_traffic_class>>
_Why: 27002:7.12 — proportional_

<<TEXT>>

## 4. Per-row routing description (conduit / overhead-tray / under-floor / via-shared-corridor)

<<MUST item:A.7.12:reg_routing>>
_Why: 27002:7.12 — protected_

<<TEXT>>

## 5. Per-row last-inspected date

<<MUST item:A.7.12:reg_last_inspected>>
_Why: Drift prevention_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row remediation log where protection falls short

<<SHOULD item:A.7.12:reg_remediation>>
_Why: Operational discipline_

<<TEXT>>
