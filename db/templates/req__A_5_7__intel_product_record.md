---
leaf_id: req:A.5.7:intel_product_record
control_ref: A.5.7
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Per-Product Intelligence Records

> A.5.7 expects intelligence to actually reach consumers and inform defensive action — not just be produced and filed. The per-product record evidences each delivered artefact: product id, layer, source feeds aggregated, named consumer(s), distribution date, action taken downstream (firewall rule pushed / IDS signature added / risk register entry / exec briefing). One record per published product, traceable back to the feed register and forward to the consumer's control

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Product identifier per record (unique, sequenced)

<<MUST item:A.5.7:prod_id>>
_Why: 27002:5.7 — produce threat intelligence_

<<TEXT>>

## 2. Intelligence layer per record (strategic / tactical / operational)

<<MUST item:A.5.7:prod_layer>>
_Why: 27002:5.7 — three layers_

<<TEXT>>

## 3. Source feeds aggregated per record (links to feed register entries)

<<MUST item:A.5.7:prod_sources>>
_Why: 27002:5.7 — sources traceability_

<<TEXT>>

## 4. Named consumer(s) per record (sec ops, IT/network, risk owners, exec briefing)

<<MUST item:A.5.7:prod_consumer>>
_Why: 27002:5.7 — communication_

<<TEXT>>

## 5. Distribution date and channel per record (email, ticket, briefing)

<<MUST item:A.5.7:prod_distribution>>
_Why: 27002:5.7 — delivered_

<<TEXT>>

## 6. Action taken downstream per record (firewall rule / IDS signature / risk register entry / control update / no-op)

<<MUST item:A.5.7:prod_action_taken>>
_Why: 27002:5.7 — informed defensive action_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Effectiveness check planned or recorded (post-distribution validation that the product drove the intended action)

<<SHOULD item:A.5.7:prod_effectiveness>>
_Why: Continual improvement_

<<TEXT>>

### 2. Retention end-date noted (IOC libraries age fast — old products marked for archive/disposal)

<<SHOULD item:A.5.7:prod_retention_end>>
_Why: Operational discipline_

<<TEXT>>
