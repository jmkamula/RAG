---
leaf_id: req:A.5.7:threat_intel_feed_register
control_ref: A.5.7
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Threat Intelligence Feed Register

> A.5.7 requires a curated set of sources, not an ad-hoc list. The feed register catalogues every active intelligence source with metadata that allows the program review to assess which feeds deliver value: source name, layer, owner inside the org, last received signal, cost, signal/noise rating. Decommissioned feeds are retained with end-date for traceability

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each active source captured with a unique identifier

<<MUST item:A.5.7:reg_source_id>>
_Why: 27002:5.7 — sources_

<<TEXT>>

## 2. Intelligence layer per row (strategic / tactical / operational)

<<MUST item:A.5.7:reg_layer>>
_Why: 27002:5.7 — three layers_

<<TEXT>>

## 3. Internal owner per row accountable for the source (renewal, escalation, value assessment)

<<MUST item:A.5.7:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 4. Last-received timestamp per row (stale-feed detection)

<<MUST item:A.5.7:reg_last_received>>
_Why: 27002:5.7 — collection cadence verified_

<<TEXT>>

## 5. Cost per row (paid feeds vs free) — required for value review

<<MUST item:A.5.7:reg_cost>>
_Why: Program economics_

<<TEXT>>

## 6. Signal/noise rating per row (high/medium/low) updated at each program review

<<MUST item:A.5.7:reg_signal_rating>>
_Why: 27002:5.7 — relevance_

<<TEXT>>

## 7. Internal sources captured alongside external (e.g. A.5.6 SIG-membership outputs, internal IR observations)

<<MUST item:A.5.7:reg_internal_input>>
_Why: 27002:5.7 — internal/external balance_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Decommissioned sources retained with end-date and reason (audit trail)

<<SHOULD item:A.5.7:reg_decommissioned>>
_Why: Operational discipline_

<<TEXT>>

### 2. Contact per row (vendor support, ISAC liaison)

<<SHOULD item:A.5.7:reg_contact>>
_Why: Operational continuity_

<<TEXT>>
