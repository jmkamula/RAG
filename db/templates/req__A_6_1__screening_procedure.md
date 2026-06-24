---
leaf_id: req:A.6.1:screening_procedure
control_ref: A.6.1
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Personnel Screening Procedure

> A.6.1 requires background verification checks on candidates and ongoing checks proportional to role risk. The procedure documents the check types, timing, proportionality, legal considerations, decision authority, retention rules, and re-screening triggers. The screening record register, applicable-roles scope and periodic program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Types of checks defined (identity, employment history, education, criminal record where lawful, financial where role-relevant, sanctions/PEP for finance-sector roles)

<<MUST item:A.6.1:check_types>>
_Why: 27002:6.1a — background verification checks_

<<TEXT>>

## 2. Timing — pre-joining checks plus ongoing checks where applicable (recurring re-check cadence for high-trust roles)

<<MUST item:A.6.1:timing>>
_Why: 27002:6.1a — prior to joining + ongoing_

<<TEXT>>

## 3. Proportionality stated by role, information classification accessed, and perceived risk (junior office role vs admin vs CISO — different check depth)

<<MUST item:A.6.1:proportionality>>
_Why: 27002:6.1a — proportional_

<<TEXT>>

## 4. Legal, regulatory, and ethical constraints applied per jurisdiction (some checks unlawful or restricted in EU/UK; consent + transparency obligations under GDPR)

<<MUST item:A.6.1:legal_consideration>>
_Why: 27002:6.1 — applicable laws, regulations and ethics_

<<TEXT>>

## 5. Decision authority named (who accepts or rejects screening outcomes — typically Hiring Manager + HR + InfoSec for sensitive roles)

<<MUST item:A.6.1:decision_authority>>
_Why: Accountability_

<<TEXT>>

## 6. Retention rules for screening results (often short retention for negative results to comply with GDPR; longer where law mandates — financial roles)

<<MUST item:A.6.1:retention>>
_Why: 27002:6.1 — applicable laws_

<<TEXT>>

## 7. Named owner of the screening procedure (HR + InfoSec jointly; HR runs operationally, InfoSec sets risk-tier criteria)

<<MUST item:A.6.1:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Re-screening triggers (significant role change, escalated access from A.5.18, security incident involving the individual)

<<SHOULD item:A.6.1:rescreen_triggers>>
_Why: Ongoing relevance_

<<TEXT>>

### 2. Third-party screening provider contracts and oversight (where used — supplier-management linkage to A.5.19)

<<SHOULD item:A.6.1:third_party_use>>
_Why: Common pattern_

<<TEXT>>
