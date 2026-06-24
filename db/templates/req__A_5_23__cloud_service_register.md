---
leaf_id: req:A.5.23:cloud_service_register
control_ref: A.5.23
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 7
should_count: 3
---

# Cloud Service Register

> A.5.23 expects the org to know which cloud services are in use, where they store and process data, what classification of data they hold, what the shared-responsibility split looks like in practice, and what the agreement says. The register is the live source of truth — feeding the periodic posture review and exit-migration leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each cloud service identified per row (provider, service name, deployment model)

<<MUST item:A.5.23:reg_service>>
_Why: 27002:5.23a — scope_

<<TEXT>>

## 2. Data classification per service (which org-classification levels are processed)

<<MUST item:A.5.23:reg_classification>>
_Why: 27002:5.23 — sensitive info_

<<TEXT>>

## 3. Geographic location of data per service (region, sub-region)

<<MUST item:A.5.23:reg_geo>>
_Why: 27002:5.23 — geo_

<<TEXT>>

## 4. Shared-responsibility split recorded per service (what is CSP-managed, what is org-managed)

<<MUST item:A.5.23:reg_responsibility>>
_Why: 27002:5.23d_

<<TEXT>>

## 5. Named internal owner accountable per service (typically platform / SRE / business owner)

<<MUST item:A.5.23:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 6. Reference to the agreement / contract in force per service (link to A.5.20 coverage register)

<<MUST item:A.5.23:reg_agreement>>
_Why: Cross-control consistency_

<<TEXT>>

## 7. Exit-plan readiness flag per service (Yes / No / Stale)

<<MUST item:A.5.23:reg_exit_readiness>>
_Why: 27002:5.23 — exit_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Disclosed sub-processors per service tracked

<<SHOULD item:A.5.23:reg_subprocessors>>
_Why: 27002:5.23 — sub-processing_

<<TEXT>>

### 2. Most recent CSP attestation / certification reference per service (with date)

<<SHOULD item:A.5.23:reg_attestation>>
_Why: 27002:5.23 — CSP assurance_

<<TEXT>>

### 3. Business-process dependency map (which processes depend on which service)

<<SHOULD item:A.5.23:reg_dependency_map>>
_Why: Continuity awareness_

<<TEXT>>
