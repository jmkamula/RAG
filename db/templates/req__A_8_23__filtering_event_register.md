---
leaf_id: req:A.8.23:filtering_event_register
control_ref: A.8.23
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Web Filtering Event Register

> Aggregate event view — blocked-access trending, override events, malware-category hits. Drives 'does the filter actually work' visibility

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Aggregate blocked-event volume per category (rolling window)

<<MUST item:A.8.23:reg_volume>>
_Why: 27002:8.23 — managed_

<<TEXT>>

## 2. Top-blocked-sites view (signal for category-tuning opportunity)

<<MUST item:A.8.23:reg_top_blockers>>
_Why: Operational visibility_

<<TEXT>>

## 3. Override events captured (user / site / justification / approval)

<<MUST item:A.8.23:reg_overrides>>
_Why: Auditability_

<<TEXT>>

## 4. Malware-category hits (signal for incident handoff)

<<MUST item:A.8.23:reg_malware_hits>>
_Why: 27002:8.23 — malicious content_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Dashboard linked (coverage % / block rate / override volume)

<<SHOULD item:A.8.23:reg_dashboard>>
_Why: Operational visibility_

<<TEXT>>
