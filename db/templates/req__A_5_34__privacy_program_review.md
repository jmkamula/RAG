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
table_shape: true
---

# Periodic Privacy and PII Protection Program Review

> Periodic verification that the policy still matches applicable law, the register reflects current processing reality, DSARs are being responded to within SLA, breaches were handled per Art.33/34, transfers still have valid legal mechanisms, and DPIAs are completed where required. ISO 27002:2022 § 5.34 + GDPR's accountability principle (Art.5.2 + Art.24) expect the privacy program to be MAINTAINED — drift between policy and reality is the audit failure mode this leaf catches. Annual cadence (freshness=365) matches A.5.35 independent review + A.5.36 compliance review + A.5.33 records-family default

<!-- TABLE-COLUMNS leaf:req:A.5.34:privacy_program_review -->
<!-- column: item:A.5.34:rev_date -->
<!-- column: item:A.5.34:rev_reviewer -->
<!-- column: item:A.5.34:rev_register_check -->
<!-- column: item:A.5.34:rev_scope_check -->
<!-- column: item:A.5.34:rev_dsar_metrics -->
<!-- column: item:A.5.34:rev_breach_history -->
<!-- column: item:A.5.34:rev_transfer_validity -->
<!-- column: item:A.5.34:rev_dpia_review -->
<!-- column: item:A.5.34:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.34:privacy_program_review -->
| Rev Date | Rev Reviewer | Rev Register Check | Rev Scope Check | Rev Dsar Metrics | Rev Breach History | Rev Transfer Validity | Rev Dpia Review | Rev Register Update |
|---|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.34:privacy_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.34:rev_date>>
_Why: 27002:5.34 — maintained / GDPR Art.5.2_

> _Standard text:_ Review date within the planned interval (typically within 12 months of last review)

### Rev Reviewer

<<MUST item:A.5.34:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role recorded (DPO or Privacy Officer + InfoSec lead jointly; legal-counsel sign-off where law has shifted materially)

### Rev Register Check

<<MUST item:A.5.34:rev_register_check>>
_Why: 27002:5.34 — kept current_

> _Standard text:_ Per-activity outcome (verified / amended / retired / new added) with lawful-basis-still-valid and retention-still-adequate confirmation

### Rev Scope Check

<<MUST item:A.5.34:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the privacy applicability scope — any new jurisdiction, regulated activity, data subject category that should add register entries

### Rev Dsar Metrics

<<MUST item:A.5.34:rev_dsar_metrics>>
_Why: GDPR Art.12.3 + Art.15-22 compliance_

> _Standard text:_ DSAR metrics review (volumes, response times against SLA, refusal/extension rates, complaints to supervisory authority) — operational privacy health

### Rev Breach History

<<MUST item:A.5.34:rev_breach_history>>
_Why: GDPR Art.33-34_

> _Standard text:_ Breach history for the period (every personal-data breach in scope confirmed handled per Art.33 72h notification + Art.34 data-subject notification where required; lessons fed into A.5.27)

### Rev Transfer Validity

<<MUST item:A.5.34:rev_transfer_validity>>
_Why: GDPR Chap V_

> _Standard text:_ Transfer-mechanism validity check (SCCs current edition, adequacy decisions still standing — e.g. Schrems shifts, BCRs unchanged) — flag stale mechanisms for remediation

### Rev Dpia Review

<<MUST item:A.5.34:rev_dpia_review>>
_Why: GDPR Art.35_

> _Standard text:_ DPIA completion status reviewed (any high-risk processing without a completed DPIA flagged; DPIAs older than 24 months refreshed where processing material to lifecycle changed)

### Rev Register Update

<<MUST item:A.5.34:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated back to the live register with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.5.34:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (Schrems-style adequacy shift, new regulator enforcement action in scope sector, M&A, large-scale breach in industry)

### Rev Next Date

<<SHOULD item:A.5.34:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
