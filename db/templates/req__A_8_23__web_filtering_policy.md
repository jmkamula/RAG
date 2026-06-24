---
leaf_id: req:A.8.23:web_filtering_policy
control_ref: A.8.23
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Web Filtering Policy

> A.8.23 requires access to external websites managed to reduce exposure to malicious content. Policy states filtering scope, blocked categories, override workflow, monitoring expectation. Per-event register, applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Category-based blocking minimum set (malware / phishing / illegal content / anonymisers / known-malicious)

<<MUST item:A.8.23:categories>>
_Why: 27002:8.23 — reduce exposure to malicious content_

<<TEXT>>

## 2. Override / business-justification workflow (block-page UX with audit trail)

<<MUST item:A.8.23:override_workflow>>
_Why: 27002:8.23 — managed_

<<TEXT>>

## 3. Monitoring requirement for attempted access to blocked sites (cross-link to A.8.16)

<<MUST item:A.8.23:monitoring_req>>
_Why: 27002:8.23 — managed_

<<TEXT>>

## 4. TLS-inspection stance documented (where applied / where bypassed for privacy / legal-categorisation excluded)

<<MUST item:A.8.23:tls_inspection>>
_Why: Operational trade-off_

<<TEXT>>

## 5. Named policy authority (InfoSec lead with Legal/HR partner for category boundaries)

<<MUST item:A.8.23:authority>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. BYOD coverage strategy (proxy enforcement / off-network behaviour)

<<SHOULD item:A.8.23:byod_strategy>>
_Why: Realistic scope_

<<TEXT>>
