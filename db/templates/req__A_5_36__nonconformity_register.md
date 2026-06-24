---
leaf_id: req:A.5.36:nonconformity_register
control_ref: A.5.36
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Compliance Nonconformity Register

> A.5.36 requires corrective actions tracked to closure — but the corrective-action promise is theoretical without a per-NC lifecycle tracker. The nonconformity register catalogues every NC raised: severity, owner, agreed corrective action, target date, closure status, root cause. This is the audit-defensibility artefact paired with the review records

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-NC unique identifier traceable back to the source review record

<<MUST item:A.5.36:nc_id>>
_Why: 27002:5.36 — review_

<<TEXT>>

## 2. Severity recorded per NC (matches the review record's severity classification)

<<MUST item:A.5.36:nc_severity>>
_Why: 27002:5.36 — review_

<<TEXT>>

## 3. Named owner per NC (named individual, not generic team) with target closure date

<<MUST item:A.5.36:nc_owner>>
_Why: Accountability_

<<TEXT>>

## 4. Corrective action stated per NC (the specific change committed — policy update, control implementation, training delivery)

<<MUST item:A.5.36:nc_corrective_action>>
_Why: Closes the loop_

<<TEXT>>

## 5. Current status per NC (open / in-progress / closed / aged-overdue / risk-accepted-with-exception) with last-updated date

<<MUST item:A.5.36:nc_status>>
_Why: Operational discipline_

<<TEXT>>

## 6. Closure evidence reference per closed NC (link to the artefact that proves the NC was addressed)

<<MUST item:A.5.36:nc_closure_evidence>>
_Why: Audit defensibility_

<<TEXT>>

## 7. Root cause noted per NC where determined (drives systemic improvements vs point fixes)

<<MUST item:A.5.36:nc_root_cause>>
_Why: Continual improvement_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exception register integration — risk-accepted NCs with expiry date (so 'we accept this' doesn't drift into 'we forgot this')

<<SHOULD item:A.5.36:nc_exception_register>>
_Why: Realistic operations_

<<TEXT>>

### 2. Aged-overdue alerting (notification when target date passes without closure)

<<SHOULD item:A.5.36:nc_aging_alerts>>
_Why: Operational discipline_

<<TEXT>>

### 3. Cross-link to A.5.35 independent-review finding register where the two are kept as one artefact

<<SHOULD item:A.5.36:nc_cross_review_link>>
_Why: Cross-control coherence_

<<TEXT>>
