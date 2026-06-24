---
leaf_id: req:A.5.34:pii_processing_register
control_ref: A.5.34
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
---

# PII Processing Register

> The operational catalog of every processing activity involving PII — what categories, whose, on what legal basis, retained how long, owned by whom, protected how, transferred where. Often shared with (or extended from) the GDPR Art.30 Records of Processing (RoPA) — same operational artefact serves both ISO A.5.34 and GDPR Art.30. Without this register, the privacy policy is theoretical; with it, A.5.34 / Art.30 / Art.25 / Art.5 can all be evidenced from a single source

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. PII categories enumerated per processing activity (basic identifiers, contact data, financial, health, biometric, special-category — GDPR Art.9 / sectoral equivalents); links to GDPR Art.30 RoPA

<<MUST item:A.5.34:pii_inventory>>
_Why: 27002:5.34 — protection of PII / GDPR Art.30.1.c_

<<TEXT>>

## 2. Data subject categories per processing activity (customers, employees, prospects, minors, vulnerable groups — drives extra-safeguard decisions)

<<MUST item:A.5.34:reg_data_subjects>>
_Why: 27002:5.34 — relevant / GDPR Art.30.1.c_

<<TEXT>>

## 3. Processing purposes stated per activity (specific, explicit, legitimate — not 'business operations'; cross-link to GDPR Art.5.1.b purpose limitation)

<<MUST item:A.5.34:reg_purposes>>
_Why: GDPR Art.30.1.b + Art.5.1.b_

<<TEXT>>

## 4. Lawful basis recorded per activity (matches the policy's discipline — consent / contract / legal obligation / vital interests / public task / legitimate interests, with special-category Art.9 basis where applicable)

<<MUST item:A.5.34:reg_lawful_basis>>
_Why: GDPR Art.6 + Art.9_

<<TEXT>>

## 5. Retention period per activity (concrete duration with start/end triggers; cross-link to A.5.33 records schedule — no arbitrary numbers)

<<MUST item:A.5.34:reg_retention>>
_Why: GDPR Art.30.1.f + A.5.33 coherence_

<<TEXT>>

## 6. Owner per processing activity (named role responsible for the activity — HR for employee processing, Sales for prospect processing, etc.)

<<MUST item:A.5.34:reg_owner_per_activity>>
_Why: Accountability_

<<TEXT>>

## 7. Security controls applied per activity (encryption at rest/in transit, access control class, pseudonymisation where used — cross-link to A.8.x and GDPR Art.32)

<<MUST item:A.5.34:reg_controls_applied>>
_Why: GDPR Art.30.1.g + Art.32_

<<TEXT>>

## 8. Cross-border transfers per activity (destination jurisdictions + legal mechanism — SCCs / adequacy / BCRs / derogations; explicit 'none' where applicable)

<<MUST item:A.5.34:reg_transfers>>
_Why: GDPR Art.30.1.e + Chap V_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Direct link to GDPR Art.30 RoPA register where the two are kept as one artefact — saves duplication, prevents drift

<<SHOULD item:A.5.34:reg_ropa_link>>
_Why: Cross-control coherence_

<<TEXT>>

### 2. DPIA status per activity (required / completed / not required with rationale) — drives high-risk processing reviews

<<SHOULD item:A.5.34:reg_dpia_status>>
_Why: GDPR Art.35_

<<TEXT>>

### 3. Last-verified date per activity (proves the entry is current; missing dates surface stale activities at review)

<<SHOULD item:A.5.34:reg_last_verified>>
_Why: 27002:5.34 — maintained_

<<TEXT>>
