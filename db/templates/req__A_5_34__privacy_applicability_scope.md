---
leaf_id: req:A.5.34:privacy_applicability_scope
control_ref: A.5.34
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Privacy Applicability Scope

<<DOC_CONTROL>>

> The upstream that drives the policy and the register. Documents the privacy laws applicable to the organisation, the jurisdictions where data subjects live and where processing happens, the data subject categories the org touches, and the regulated activities that pull in sectoral privacy regimes. ISO 27002:2022 § 5.34 expects organisations to know which privacy regimes apply before claiming compliance — drift between scope and register is the audit failure mode this leaf catches

## What this template gives you

This template helps you clearly identify which privacy laws and regulations apply to your organization, where your data subjects are located, and what types of personal data and activities are covered. It's useful for understanding your compliance obligations and avoiding gaps in your privacy program.

## When to use it

Use this document whenever you need to define or update the privacy laws and jurisdictions relevant to your organization. It should be reviewed and refreshed whenever there are changes to your business operations, data processing activities, or applicable regulations.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on how easily you can gather information about your data subjects, processing locations, and applicable privacy laws.

## 1. Applicable privacy laws enumerated per jurisdiction (GDPR for EU/EEA, UK GDPR for UK, CCPA for California residents, LGPD for Brazil, PIPEDA for Canada, sectoral laws — HIPAA, GLBA, FERPA where relevant)

<<MUST item:A.5.34:scope_privacy_laws>>
_Why: 27002:5.34 — applicable laws + relevance_

<<GUIDANCE>>

<<TEXT>>

## 2. Jurisdictions covered (HQ + places of business + data subject residency + processing locations + transfer destinations — each may impose distinct privacy obligations)

<<MUST item:A.5.34:scope_jurisdictions>>
_Why: 27002:5.34 — relevance_

<<GUIDANCE>>

<<TEXT>>

## 3. Data subject categories the organisation touches (customers, employees, prospects, suppliers' staff, minors, healthcare patients, financial-services clients — drives extra-safeguard rules)

<<MUST item:A.5.34:scope_data_subjects>>
_Why: 27002:5.34 — protection of PII_

<<GUIDANCE>>

<<TEXT>>

## 4. Regulated activities pulling in sectoral privacy regimes (healthcare → HIPAA, financial → GLBA/PSD2/DORA-privacy overlap, telco → ePrivacy, public sector → FERPA/government-records laws, advertising/profiling → ePrivacy)

<<MUST item:A.5.34:scope_regulated_activities>>
_Why: 27002:5.34 — applicable laws_

<<GUIDANCE>>

<<TEXT>>

## 5. Controller vs Processor vs Joint Controller status per processing context (drives different obligation sets — Art.24-31 for controllers, Art.28 for processors, Art.26 for joint controllers)

<<MUST item:A.5.34:scope_controller_role>>
_Why: GDPR Art.24-28_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-link to A.5.31 applicable-obligations scope — privacy laws are a subset; the two should share drivers and stay aligned

<<SHOULD item:A.5.34:scope_obligations_link>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

### 2. Trigger list for re-scoping (new geography, new service line entering a regulated sector, M&A bringing new data subject categories, new transfer destinations)

<<SHOULD item:A.5.34:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
