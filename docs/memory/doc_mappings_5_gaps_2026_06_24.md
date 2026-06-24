---
name: doc-mappings-5-gaps-2026-06-24
description: "AUTHORED 2026-06-24: 3 new doc_mapping umbrellas close the gaps surfaced by the unconditional unbound drop. vendor_security_assessment_report (A.5.21+22), pii_data_handling_process (A.5.34+12+8.10), external_audit_report (9.2+9.3+10.1). 2 of the 5 listed gaps (HR Security + Compliance Requirements) already had adequate mappings — they only needed the unbound drop. Discover smoke confirms top-match at 0.90 for all 4 docx files."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

The 2026-06-24 unconditional unbound drop (commit b4bf331)
surfaced 5 docs in Arion's corpus producing 0 findings. Diagnosis
per doc:

| Doc | Existing mapping | Resolution |
|---|---|---|
| Vendor Security Assessment Report.docx | None (supplier_security_policy.yaml targets POLICY shape, not assessment-report shape) | NEW: `vendor_security_assessment_report.yaml` |
| Lead Sales and Client Data Handling.docx | None | NEW: `pii_data_handling_process.yaml` |
| 214427_Client Report 27001_DG3D87.pdf (Czech audit) | None (`iso27001_2022_9_2_internal_audit_programme.yaml` is for internal programme docs) | NEW: `external_audit_report.yaml` |
| Compliance Requirements.docx | `compliance_requirements_register.yaml` exists + matches | No change — existing mapping covered it; unbound was LLM-stochasticity, now dropped |
| HR Security Policy.docx | `hr_security_policy.yaml` exists + matches (A.6.3 + A.6.6 included) | No change — existing mapping covered it; unbound was LLM-stochasticity, now dropped |

## The 3 new umbrellas

### `vendor_security_assessment_report.yaml` → A.5.21 + A.5.22

Targets the per-vendor *assessment report* shape — distinct from
the supplier_security_policy umbrella (which targets the *policy*
shape). 18 filename fingerprints cover vendor/supplier/third-party
× security/privacy/risk × assessment/evaluation/due-diligence
permutations. Body fingerprints capture the "third-party vendors",
"data processing agreement", "vendor classification" vocabulary.

Target leaves:
- req:A.5.22:supplier_review_record (the assessment IS this)
- req:A.5.22:review_schedule_register
- req:A.5.21:supply_chain_review

### `pii_data_handling_process.yaml` → A.5.34 + A.5.12 + A.8.10

Targets multi-step PII lifecycle process docs (Collect → Classify
→ Restrict → Process → Store → Delete). Anchored on A.5.34 PII
protection with adjacent classification (A.5.12) + deletion
(A.8.10) leaves. 15 filename fingerprints, 10 body fingerprints
covering "personally identifiable information", "data subject
rights", "data minimization", "anonymize data" vocabulary.

Target leaves:
- req:A.5.34:pii_processing_register
- req:A.5.34:privacy_and_pii_protection_policy
- req:A.5.34:privacy_applicability_scope
- req:A.5.12:information_classification_scheme
- req:A.8.10:information_deletion_procedure
- req:A.8.10:applicable_deletion_scope

### `external_audit_report.yaml` → 9.2 + 9.3 + 10.1

Targets third-party certification body audit reports (Stage 1,
Stage 2, surveillance, recertification). These are EXTERNAL
audit evidence, distinct from the existing
`iso27001_2022_9_2_internal_audit_programme.yaml` per-leaf
scaffold for internal audit programme docs. 17 filename
fingerprints; 9 body fingerprints covering "nonconformity
finding", "opportunity for improvement", "audit conclusion",
"certification decision".

Numeric tokens (1, 2, 27001) **must be quoted** in YAML
fingerprints — `_normalise_fingerprint` calls `.lower()` and
errors on int. Caught during validation.

Target leaves:
- req:9.2:audit_execution_record
- req:9.2:audit_program_review
- req:9.3:management_review
- req:10.1:improvement_action_register
- req:10.1:applicable_triggers_scope

Note: filename heuristics work on English titles. The Czech
audit report ("214427_Client Report 27001_DG3D87.pdf") matches
on the `[client, report, "27001"]` fingerprint. Non-English
docs more broadly will rely on the enricher's translated topic
tokens — a future i18n workstream.

## Discover smoke test

Direct `discover_doc()` test on each docx + the new mappings:

| Doc | Top match | Confidence |
|---|---|---|
| Vendor Security Assessment Report.docx | supplier_security_assessment_report | **0.90** |
| Lead Sales and Client Data Handling.docx | pii_data_handling_process | **0.90** |
| Compliance Requirements.docx | compliance_requirements_register | **0.90** (existing) |
| HR Security Policy.docx | hr_security_policy | **0.90** (existing) |

All 4 reach `filename_score=1.0` + `body_score=1.0` = 0.90 total.

The Czech PDF was not tested with this script (PDF reader path
differs) but will exercise the real pipeline on re-extract.

## Re-extract results

All 5 docs went from 0 → non-zero bound findings:

| Doc | Pre | Post | Mapping |
|---|---|---|---|
| HR Security Policy.docx | 0 | **15 bound** | hr_security_policy.yaml (existing) |
| 214427_Client Report 27001_DG3D87.pdf (Czech) | 0 | **11 bound** | external_audit_report.yaml (NEW) |
| Vendor Security Assessment Report.docx | 0 | **5 bound** | vendor_security_assessment_report.yaml (NEW) |
| Lead Sales and Client Data Handling.docx | 0 | **5 bound** | pii_data_handling_process.yaml (NEW) |
| Compliance Requirements.docx | 0 | **3 bound** | compliance_requirements_register.yaml (existing) |

Total: **39 new bound findings** across the 5 docs.

Tenant-wide: extracted bound 329 → 348 (+19 net — some of the 39
superseded prior bound findings from related controls via the
writer-supersede mechanism). 0 unbound across all
engine-actionable sources. xfw_bridge 95 → 72 (some by-design
bridges got superseded during the re-extracts).

The Czech audit report match validates the
`[client, report, "27001"]` filename fingerprint — non-English
docs CAN match doc_mappings via numeric/identifier tokens that
are language-invariant.

## Related

- [[extractor-unbound-drop-2026-06-24]] — the prior commit that
  surfaced these gaps by dropping unbound findings instead of
  emitting inert control-level matches
- [[doc-mapping-training-awareness-2026-06-24]] — same-day
  precedent for vocabulary-widening umbrellas
- [[doc-curation-engine-v1]] — Direction C extractor (per-MUST
  binding); these doc_mappings are the curated narrowing layer
