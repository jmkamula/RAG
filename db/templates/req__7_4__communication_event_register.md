---
leaf_id: req:7.4:communication_event_register
control_ref: 7.4
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
---

# ISMS Communication Event Register

> Per-communication record — what was communicated, when, to whom, via what channel, with what acknowledgement. The proof communications actually happened, not just planned. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique event identifier per row

<<MUST item:7.4:reg_event_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-row topic (matches procedure 'what' catalog)

<<MUST item:7.4:reg_topic>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 3. Per-row audience (which internal group / external party)

<<MUST item:7.4:reg_audience>>
_Why: Clause 7.4 c)_

<<TEXT>>

## 4. Per-row channel used

<<MUST item:7.4:reg_channel>>
_Why: Clause 7.4 d)_

<<TEXT>>

## 5. Per-row date / time of communication

<<MUST item:7.4:reg_date>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row acknowledgement evidence where required (read-receipt, attendance log, signed receipt)

<<SHOULD item:7.4:reg_ack>>
_Why: Closure proof_

<<TEXT>>

### 2. Per-row sender / responsible person

<<SHOULD item:7.4:reg_sender>>
_Why: Accountability — log-shape registers_

<<TEXT>>
