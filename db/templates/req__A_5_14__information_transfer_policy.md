---
leaf_id: req:A.5.14:information_transfer_policy
control_ref: A.5.14
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Information Transfer Policy

> A.5.14 requires rules, procedures or agreements covering all transfer facilities within the organisation and to/from external parties. The policy documents electronic/physical/verbal transfer rules, authorisation thresholds, classification-aware protections, jurisdictional considerations and approved-channel lists. Approval, communication and periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Rules for electronic transfers (email, file transfer, cloud sharing, APIs) with encryption requirements per classification level

<<MUST item:A.5.14:electronic_transfer>>
_Why: 27002:5.14 — transfer facilities_

<<TEXT>>

## 2. Rules for physical media transfers (removable storage, paper documents, post/courier — tamper-evident packaging where appropriate)

<<MUST item:A.5.14:physical_media>>
_Why: 27002:5.14 — all transfer facility types_

<<TEXT>>

## 3. Rules for verbal and visual transfers (calls, screen-shares, in-person discussions in public spaces, conference talks where sensitive info may appear)

<<MUST item:A.5.14:verbal_visual>>
_Why: 27002:5.14 — all transfer facility types_

<<TEXT>>

## 4. Distinction between internal and external transfer requirements (within-org transfers may have lighter controls than out-bound to third parties)

<<MUST item:A.5.14:internal_vs_external>>
_Why: 27002:5.14 — within the organisation and between_

<<TEXT>>

## 5. Authorisation requirements for transfers above defined classification levels (who approves, for which level, for which counterparty)

<<MUST item:A.5.14:authorisation>>
_Why: 27002:5.14 — rules_

<<TEXT>>

## 6. Legal and jurisdictional considerations (cross-border transfers, data sovereignty, GDPR Art.44-49 international-transfer mechanisms)

<<MUST item:A.5.14:legal_jurisdiction>>
_Why: 27002:5.14 + GDPR Chap V_

<<TEXT>>

## 7. Alignment with the A.5.12 classification scheme stated explicitly (transfer protections per level — cascade from parent scheme)

<<MUST item:A.5.14:scheme_alignment>>
_Why: 27002:5.14 + cross-link to [[A.5.12]]_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Standard transfer agreements with frequent counterparties referenced (cross-link to A.5.20 supplier agreements path where the counterparty is also a supplier)

<<SHOULD item:A.5.14:transfer_agreements>>
_Why: Efficiency + cross-link to [[A.5.20]]_

<<TEXT>>

### 2. Approved channel list (e.g. encrypted email, sanctioned file-sharing platforms, MFT solutions) per classification level

<<SHOULD item:A.5.14:approved_channels>>
_Why: User clarity_

<<TEXT>>

### 3. Emergency / out-of-band transfer path (when standard channels are unavailable — break-glass procedure with post-hoc authorisation)

<<SHOULD item:A.5.14:emergency_path>>
_Why: Real-world coverage_

<<TEXT>>
