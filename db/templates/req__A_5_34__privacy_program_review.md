---
leaf_id: req:A.5.34:privacy_program_review
control_ref: A.5.34
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 9
should_count: 2
---

# Periodic Privacy and PII Protection Program Review

> Periodic verification that the policy still matches applicable law, the register reflects current processing reality, DSARs are being responded to within SLA, breaches were handled per Art.33/34, transfers still have valid legal mechanisms, and DPIAs are completed where required. ISO 27002:2022 § 5.34 + GDPR's accountability principle (Art.5.2 + Art.24) expect the privacy program to be MAINTAINED — drift between policy and reality is the audit failure mode this leaf catches. Annual cadence (freshness=365) matches A.5.35 independent review + A.5.36 compliance review + A.5.33 records-family default

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (typically within 12 months of last review)

<<MUST item:A.5.34:rev_date>>
_Why: 27002:5.34 — maintained / GDPR Art.5.2_

<<TEXT>>

## 2. Reviewer identity and role recorded (DPO or Privacy Officer + InfoSec lead jointly; legal-counsel sign-off where law has shifted materially)

<<MUST item:A.5.34:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-activity outcome (verified / amended / retired / new added) with lawful-basis-still-valid and retention-still-adequate confirmation

<<MUST item:A.5.34:rev_register_check>>
_Why: 27002:5.34 — kept current_

<<TEXT>>

## 4. Cross-check against the privacy applicability scope — any new jurisdiction, regulated activity, data subject category that should add register entries

<<MUST item:A.5.34:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. DSAR metrics review (volumes, response times against SLA, refusal/extension rates, complaints to supervisory authority) — operational privacy health

<<MUST item:A.5.34:rev_dsar_metrics>>
_Why: GDPR Art.12.3 + Art.15-22 compliance_

<<TEXT>>

## 6. Breach history for the period (every personal-data breach in scope confirmed handled per Art.33 72h notification + Art.34 data-subject notification where required; lessons fed into A.5.27)

<<MUST item:A.5.34:rev_breach_history>>
_Why: GDPR Art.33-34_

<<TEXT>>

## 7. Transfer-mechanism validity check (SCCs current edition, adequacy decisions still standing — e.g. Schrems shifts, BCRs unchanged) — flag stale mechanisms for remediation

<<MUST item:A.5.34:rev_transfer_validity>>
_Why: GDPR Chap V_

<<TEXT>>

## 8. DPIA completion status reviewed (any high-risk processing without a completed DPIA flagged; DPIAs older than 24 months refreshed where processing material to lifecycle changed)

<<MUST item:A.5.34:rev_dpia_review>>
_Why: GDPR Art.35_

<<TEXT>>

## 9. Changes propagated back to the live register with reference to this review

<<MUST item:A.5.34:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers listed (Schrems-style adequacy shift, new regulator enforcement action in scope sector, M&A, large-scale breach in industry)

<<SHOULD item:A.5.34:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.34:rev_next_date>>
_Why: Planning_

<<TEXT>>
