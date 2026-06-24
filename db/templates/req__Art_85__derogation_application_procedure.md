---
leaf_id: req:Art.85:derogation_application_procedure
control_ref: Art.85
standard_id: GDPR:2016/679
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 2
---

# Art.85 Derogation Application Procedure

> How the organisation identifies which processing activities fall under Art.85 (journalism / academic / artistic / literary expression), how it looks up the applicable Member-State national-law derogations per jurisdiction of operation, and how it applies derogations consistently while documenting the legal basis per activity. The procedure is the canonical artefact. Sibling leaves: per-jurisdiction derogation register, applicable activities scope, program review

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Named owner of the procedure (typically DPO + legal counsel + editorial/academic lead)

<<MUST item:Art.85:proc_owner>>
_Why: Accountability_

<<TEXT>>

## 2. Classification rules for journalism / academic / artistic / literary expression activities (distinguishes from general processing)

<<MUST item:Art.85:proc_activity_classification>>
_Why: Art.85.1 — scope of expression purposes_

<<TEXT>>

## 3. National-law lookup process per Member State of operation (each MS implements Art.85 differently per Art.85.2)

<<MUST item:Art.85:proc_jurisdiction_lookup>>
_Why: Art.85.2 — Member State law_

<<TEXT>>

## 4. Decision rules for which GDPR provisions are derogated for which activities (Chapter II/III/IV/V/VI/VII/IX scope of permissible derogations)

<<MUST item:Art.85:proc_derogation_decision>>
_Why: Art.85.2 — necessary derogations_

<<TEXT>>

## 5. Per-derogation legal-basis documentation requirement (which national-law provision authorises which derogation for which activity)

<<MUST item:Art.85:proc_legal_basis_docs>>
_Why: Demonstrability under Art.5.2_

<<TEXT>>

## 6. Cross-activity consistency check (same activity type → same derogations applied; document divergences)

<<MUST item:Art.85:proc_consistency_check>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Guidance on residual data-subject rights when derogations apply (rights may be limited but rarely fully extinguished)

<<SHOULD item:Art.85:proc_subject_rights_interaction>>
_Why: Recital 153 — reconcile both rights_

<<TEXT>>

### 2. External legal review trigger (new jurisdiction / novel activity / national-law change)

<<SHOULD item:Art.85:proc_external_legal_review>>
_Why: Risk discipline_

<<TEXT>>
