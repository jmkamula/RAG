---
leaf_id: req:A.5.35:finding_response_register
control_ref: A.5.35
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Independent Review Finding Response Register

> A.5.35 requires management response to findings — but the response promise is theoretical without a per-finding lifecycle tracker. The register catalogues every finding from every independent review: severity, owner, agreed treatment, target date, closure status. This is the audit-defensibility artefact: 'show me what you did with the findings from the 2024 review' has a one-table answer

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-finding unique identifier traceable back to the source review report

<<MUST item:A.5.35:fr_finding_id>>
_Why: 27002:5.35 — review_

<<TEXT>>

## 2. Severity recorded per finding (matches the report's severity classification)

<<MUST item:A.5.35:fr_severity>>
_Why: 27002:5.35 — review_

<<TEXT>>

## 3. Named owner per finding (named individual, not generic team) with target closure date

<<MUST item:A.5.35:fr_owner>>
_Why: Accountability_

<<TEXT>>

## 4. Agreed treatment per finding (accept / remediate / transfer with rationale; mirrors the management response committed in the report)

<<MUST item:A.5.35:fr_treatment>>
_Why: Closes the loop_

<<TEXT>>

## 5. Current status per finding (open / in-progress / closed / aged-overdue) with last-updated date

<<MUST item:A.5.35:fr_status>>
_Why: Operational discipline_

<<TEXT>>

## 6. Closure evidence reference per closed finding (link to the artefact that proves the finding was addressed — control change, policy update, training delivered)

<<MUST item:A.5.35:fr_closure_evidence>>
_Why: Audit defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Aged-overdue alerting (notification when target date passes without closure)

<<SHOULD item:A.5.35:fr_aging_alerts>>
_Why: Operational discipline_

<<TEXT>>

### 2. Cross-link to A.5.36 compliance-review nonconformity register where the two are kept as one artefact (common in mature programs)

<<SHOULD item:A.5.35:fr_cross_review_link>>
_Why: Cross-control coherence_

<<TEXT>>
