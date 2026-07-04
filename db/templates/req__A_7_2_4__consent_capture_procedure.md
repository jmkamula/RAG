---
leaf_id: req:A.7.2.4:consent_capture_procedure
control_ref: A.7.2.4
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Consent Capture + Recording Procedure

> §7.2.4 requires per-consent-event capture with sufficient detail to demonstrate the consent on later request. Covers the record fields (who / when / what / how / version) and the demonstration pathway (subject request → consent-event lookup within X business days).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-consent record fields (subject identifier + timestamp + purposes consented to + artifact version consented to + collection mechanism)

<<MUST item:A.7.2.4:proc_record_fields>>
_Why: §7.2.4 implementation — details of consent provided_

<<TEXT>>

## 2. Demonstration pathway — subject requests proof of consent, org retrieves record within stated SLA

<<MUST item:A.7.2.4:proc_demonstration_pathway>>
_Why: §7.2.4 — provide on request_

<<TEXT>>

## 3. Pre-consent information delivery per §7.3.3 (linked to A.7.3.3)

<<MUST item:A.7.2.4:proc_pre_consent_information>>
_Why: §7.2.4 — information delivered before consent process should follow guidance in 7.3.3_

<<TEXT>>

## 4. Freely-given test — no detriment for refusal, no bundled coercion

<<MUST item:A.7.2.4:proc_freely_given_test>>
_Why: §7.2.4 — freely given_

<<TEXT>>

## 5. Specific test — one consent per purpose (or granular per-purpose selection)

<<MUST item:A.7.2.4:proc_specific_test>>
_Why: §7.2.4 — specific_

<<TEXT>>

## 6. Unambiguous test — clear affirmative action, no pre-ticked boxes, no consent by silence

<<MUST item:A.7.2.4:proc_unambiguous_test>>
_Why: §7.2.4 — unambiguous + explicit_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Withdrawal pathway link (per §7.3.4 modify/withdraw consent)

<<SHOULD item:A.7.2.4:proc_withdrawal_link>>
_Why: §7.3.4 cross-link_

<<TEXT>>
