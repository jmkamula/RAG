---
leaf_id: req:A.5.33:records_protection_policy
control_ref: A.5.33
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 6
should_count: 3
---

# Records Retention and Protection Policy

<<DOC_CONTROL>>

> A.5.33 requires records to be protected from loss, destruction, falsification, unauthorized access, and unauthorized release. The policy/procedure documents how records are classified, what protection is applied per class, how disposal is carried out at end of retention, and how legal-hold overrides operate. The records schedule (per-class register), records-categories scope (upstream that determines what counts as a 'record') and periodic review are sibling leaves

## What this template gives you

This template helps you create a clear policy for protecting your important records from loss, unauthorized access, or destruction. It guides you in classifying records, applying the right protections, and managing disposal and legal holds.

## When to use it

Use this template whenever you need to document how your organization handles and safeguards records, as this policy should always be in place and updated whenever your processes or legal requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours drafting this policy from scratch, depending on how many types of records you manage and how detailed your classification and disposal processes are.

## 1. Protection requirements per record class (access control, encryption at rest, immutability where needed, integrity verification — protects against loss, destruction, falsification, unauthorized access and release)

<<MUST item:A.5.33:protection_requirements>>
_Why: 27002:5.33 — protect from loss, destruction, falsification, unauthorized access and release_

<<GUIDANCE>>

<<TEXT>>

## 2. Records classification scheme stated (record classes and the protection class assigned to each — cross-link to A.5.12 classification of information)

<<MUST item:A.5.33:classification_scheme>>
_Why: 27002:5.33 — classification_

<<GUIDANCE>>

<<TEXT>>

## 3. Disposal procedure at end of retention (secure destruction method per media type, certificate of destruction, witness for high-sensitivity classes — cross-link to A.8.10 information deletion)

<<MUST item:A.5.33:disposal>>
_Why: 27002:5.33 — secure disposal_

<<GUIDANCE>>

<<TEXT>>

## 4. Format-specific protection guidance (paper vs digital vs hybrid records; storage media handled — cloud objects, immutable WORM stores, optical media, physical archives)

<<MUST item:A.5.33:format_guidance>>
_Why: 27002:5.33 — storage media_

<<GUIDANCE>>

<<TEXT>>

## 5. Legal-hold provisions overriding normal retention (litigation hold, regulatory investigation hold, who can invoke, how it's released)

<<MUST item:A.5.33:legal_hold>>
_Why: 27002:5.33 — litigation readiness_

<<GUIDANCE>>

<<TEXT>>

## 6. Named owner of the procedure (typically records manager / legal counsel / InfoSec lead jointly)

<<MUST item:A.5.33:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. PII overlay — records containing PII inherit additional GDPR Art.5.1.e storage-limitation constraints (cross-link to A.5.34 + Art.5.1.e)

<<SHOULD item:A.5.33:proc_pii_overlay>>
_Why: ISO × GDPR integration_

<<GUIDANCE>>

<<TEXT>>

### 2. Cross-link to A.5.9 asset register — records are information assets; protection class must reconcile

<<SHOULD item:A.5.33:proc_asset_link>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

### 3. Change-log requirement for policy edits (audit trail for retention-period or protection changes)

<<SHOULD item:A.5.33:proc_change_log>>
_Why: Auditability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
