---
leaf_id: req:Art.32:resilience_test
control_ref: Art.32
standard_id: GDPR:2016/679
evidence_type: test_log
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 3
should_count: 1
---

# Periodic resilience and restoration test record

> Art.32.1.d requires a process for regularly testing, assessing and evaluating the effectiveness of technical and organisational measures for ensuring the security of processing.

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Test scope covers confidentiality, integrity, availability and resilience

<<MUST item:Art.32:resilience_test_scope>>
_Why: Art.32.1.d_

<<TEXT>>

## 2. Test executed within the freshness window (last 12 months)

<<MUST item:Art.32:resilience_test_recent>>
_Why: Art.32.1.d — 'regularly'_

<<TEXT>>

## 3. Findings recorded and remediated or accepted

<<MUST item:Art.32:resilience_test_findings>>
_Why: Art.32.1.d evaluation requirement_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Test conducted or reviewed by an independent party

<<SHOULD item:Art.32:resilience_test_independent>>
_Why: Best practice for credibility_

<<TEXT>>
