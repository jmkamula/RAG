---
name: incident-type-classification-axes
description: Reference inventory of how each major compliance standard classifies incidents. Use to design classification dimensions + curated vocabularies.
metadata: 
  node_type: memory
  type: reference
  originSessionId: f7c33fad-b32e-4557-9944-b406bcbbd8ee
---

Incident classification axes from compliance standards. Each standard defines its OWN dimension; one real incident may carry classifications across many of these simultaneously.

| Standard | Clause | Dimension | Curated values |
|---|---|---|---|
| ISO/IEC 27035-1:2023 | §5.4 | category (mechanism) | natural disaster, social engineering, misuse of resources, malicious code, denial of service, unauthorized information gathering, technical failure, intrusion |
| ISO/IEC 27001:2022 Annex A | A.5.24–A.5.28 | lifecycle state (not "type") | security event, security weakness, security incident |
| GDPR (Reg. 2016/679) | Art. 4(12); EDPB Guidelines 9/2022 §I.B | breach CIA dimension | confidentiality breach, integrity breach, availability breach (combinable) |
| GDPR | Art. 33, 34 | notifiability | authority only, subjects only, both, neither |
| NIST SP 800-61 Rev. 2 | §2.1 | attack vector | external/removable media, attrition, web, email, impersonation, improper usage, loss/theft, other |
| NIS2 (Dir. 2022/2555) | Art. 23 | significance | significant incident, near miss, cyber threat |
| DORA (Reg. 2022/2554) | Art. 17–18 | ICT incident severity | major, significant |
| HIPAA | 45 CFR §164.402 | PHI breach presumption | breach, low-probability-of-compromise exception, good-faith exception |
| PCI DSS v4.0 | Req. 12.10 | cardholder data compromise | suspected, confirmed |
| SOC 2 (TSC 2017) | CC7.3 | (intentionally undefined — entity-chosen) | — |

**Implementation implication:** the `incident_classifications` table should be keyed `(incident_id, standard_id, dimension, value)` so a single incident can carry multiple values per standard (e.g., GDPR breach can be `confidentiality + availability`) and across standards.

Related: [[incident-obligations-model]]
