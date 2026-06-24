---
leaf_id: req:7.5:document_control_policy
control_ref: 7.5
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 2
must_count: 6
should_count: 2
---

# Documented Information Control Policy

## What this template gives you

The **meta-policy** that governs how every other ISMS policy,
procedure, and record is identified, approved, distributed, retained,
and disposed of. Auditors check that the documents in your ISMS
actually follow this policy (versioning, ownership, review cadence).
A weak document-control policy makes other audit findings
multiply — old versions in circulation, no approval evidence,
inconsistent metadata.

## When to use it

You're producing the policy required by **ISO/IEC 27001:2022 Clause
7.5**. It covers both ISO-required documented information (Clauses
4.3 scope, 5.2 policy, 6.1.2 risk methodology, 6.1.3 SoA + RTP,
6.2 objectives, 9.1 monitoring, 9.2 audit, 9.3 review, 10.1
corrective) AND any organisation-determined necessary information
(typically your A.5 topic-specific policies).

## Before you start

- [ ] **4.3 ISMS Scope** stable (documents apply within scope)
- [ ] Inventory of existing ISMS documents on hand (you'll need to
      reference the **7.5 ISMS Document Register** sibling leaf)

## Cross-references

- **7.5 ISMS Document Register** (sibling) — the live list of all
  documents under this policy's control
- **A.5.33 Records protection** — for record retention discipline
- **A.5.34 PII protection** — for personal-data-containing documents
- **5.2 InfoSec Policy** — itself controlled under this policy

## Estimated effort

**2-4 hours** for v1; **30 min** for refresh.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. List the ISO 27001-required documented information

<<MUST item:7.5:iso_required_docs>>
_Clause 7.5.1(a) — required by ISO 27001._

Enumerate the documents that the standard itself mandates. This is
the ISMS-required minimum.

**✓ Good**: "ISO 27001-required documented information held by
<<TENANT_NAME>>: (a) ISMS Scope (Clause 4.3); (b) Information
Security Policy (Clause 5.2); (c) Risk Assessment Procedure
(Clause 6.1.2); (d) Risk Treatment Plan + Statement of Applicability
(Clause 6.1.3); (e) Information Security Objectives (Clause 6.2);
(f) Monitoring + Measurement results (Clause 9.1); (g) Internal
Audit Programme + results (Clause 9.2); (h) Management Review
results (Clause 9.3); (i) Corrective Action records (Clause 10.1).
Storage location + owner for each: see the ISMS Document Register
(req:7.5:isms_document_register)."

<<TEXT>>

## 2. Identify org-determined necessary information

<<MUST item:7.5:org_defined>>
_Clause 7.5.1(b) — determined necessary by the organisation._

Beyond the ISO-required minimum, what additional documents YOU
decide your ISMS needs. Typically your A.5 topic-specific policies +
procedures + records.

**✓ Good**: "Organisation-determined documented information:
(a) Annex A topic-specific policies (A.5.1, A.5.10 AUP, A.5.12
classification, A.5.15 access control, A.5.19 supplier security,
A.5.34 privacy, A.6 HR security, A.7 physical, A.8 technological).
(b) Operational procedures (A.5.18 access provisioning, A.5.24
incident response, A.5.30 ICT readiness, A.8.32 change management).
(c) Records (A.5.5 contacts, A.5.6 SIGs, A.5.9 asset inventory,
A.5.11 returns, A.5.16 identity revocation, ...). Full inventory:
ISMS Document Register."

<<TEXT>>

## 3. Define the creation + update process

<<MUST item:7.5:creation_update>>
_Clause 7.5.2 — creation, update, identification, review, approval._

How a new document is created and approved; how an existing document
is updated. Cover: identification (naming + ID convention), format
+ media standards, review cadence, approval authority by document
type.

**✓ Good**: "Creation + update process: (1) Author proposes new doc
via the ISMS workflow tool, selects type (policy / procedure /
record / scope / register / etc.). (2) Doc ID auto-assigned per
naming convention (TENANT-<TYPE>-<###>). (3) Draft circulated for
review per the review matrix (policies → ISMS Manager + DPO if PII;
procedures → operational owner). (4) Approval per the authority
matrix (policies → ISMS Owner; procedures → ISMS Manager).
(5) Approved doc published, prior version archived per retention
schedule. (6) Document Register updated by ISMS Manager same day."

<<TEXT>>

## 4. Control distribution, access, retrieval, retention, disposition

<<MUST item:7.5:control>>
_Clause 7.5.3 — control of documented information._

The five operational verbs. Cover each.

**✓ Good** (table excerpt):

| Verb | <<TENANT_NAME>> implementation |
|---|---|
| Distribution | All ISMS documents on the controlled SharePoint site; auto-notified to relevant role-holders on approval |
| Access | Read by all employees by default; edit limited to authors + ISMS Manager; sensitive docs (incident records) restricted per A.5.15 RBAC |
| Retrieval | Searchable by ID, control ref, and free text; full audit log of access for sensitive records |
| Retention | Per the retention schedule in A.5.33; ISMS records 6 years minimum; superseded versions retained read-only |
| Disposition | Secure delete per A.8.10 after retention period; deletion logged in disposal register |

<<TEXT>>

## 5. Protect against loss of legibility, integrity, unauthorised use

<<MUST item:7.5:legibility>>
_Clause 7.5.3 — protection requirements._

Three sub-protections: legibility (will it still be readable?),
integrity (will it still be unaltered?), unauthorised use (will only
the right people use it?).

**✓ Good**: "Protection mechanisms: (a) Legibility — file format
standards (PDF/A for long-term, .docx/.xlsx with sunset review every
3 years), no proprietary formats without sunset plan. (b) Integrity
— version-controlled storage, immutable audit log of changes,
SHA-256 checksums on approved versions, write-locked superseded
versions. (c) Unauthorised use — A.5.15 access control applies;
RBAC enforced via Okta; sensitive documents (incident records,
audit results) restricted to need-to-know roles."

<<TEXT>>

## 6. Control externally-originated documents

<<MUST item:7.5:external_docs>>
_Clause 7.5.3 — control external documents determined necessary._

Documents you didn't author but rely on (ISO standards copies,
vendor SOC2 reports, regulator guidance, customer DPAs, code-of-
practice publications). Same control discipline as internal docs.

**✓ Good**: "External documents under control: (a) The ISO/IEC
27001:2022 + 27002:2022 standards (licensed copies). (b) Vendor
SOC2 / ISO 27001 reports (refreshed annually per A.5.22). (c)
Customer signed DPAs + MSAs (refreshed at renewal). (d) Regulator
guidance documents (ICO, EDPB, NCSC). External docs tracked in the
Document Register with source, version-as-of, owner."

<<TEXT>>

---

## Recommended additions

### State document-format standards

<<SHOULD item:7.5:format_standards>>
_Format consistency reduces friction in retrieval and audit._

State preferred formats per document type (PDF for approved policies,
markdown for procedures, .xlsx for registers, etc.).

<<TEXT>>

### Address accessibility

<<SHOULD item:7.5:accessibility>>
_Documents need to be reachable when needed (consider on-call,
incident response, disaster recovery)._

State how the document store is reachable during disruption: e.g.
cached copies for incident responders, offline kit for major outage.

<<TEXT>>
