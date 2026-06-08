---
name: doc-curation-engine-v1
description: "SHIPPED 2026-06-07/08: doc-side analog of workbook intake — db/doc_mappings/*.yaml + doc_discovery + extractor integration + prompt/post-process tightenings + CLI parity. Arion's 3 policy docs went from 173 over-attributed findings to 9 grounded ones (94.8% reduction)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The LLM doc-extractor used to over-attribute aggressively — Arion's
Supplier Vendor Security Policy got bound to 42 controls, Access Control
Policy to 29, Business Continuity Policy to 33. Single uploaded policy
files routinely triggered the leaf evaluator's Phase-1 coarse-match path
to satisfy unrelated controls' policy leaves (e.g. Supplier Vendor
Security Policy satisfying A.5.34 PII protection's policy leaf via
`cd.evidence_type='policy'` alone, regardless of topic relevance).

## Architecture (mirror of workbook intake)

**`db/doc_mappings/*.yaml`** — canonical doc-shape pattern files. Each
YAML declares filename_fingerprints + optional body_fingerprints +
explicit target_leaves. Replaces the broad `DOC_TYPE_CLAUSE_MAP`
("policy" → all of A.5-A.8) with per-shape leaf targeting.

```yaml
schema_version: 1
mapping_id: doc.iso.A_5_23.cloud_services_policy
filename_fingerprints:
  - tokens: [cloud, service, policy]
  - tokens: [csp, security]
body_fingerprints:
  - tokens: [cloud, service, provider]
target_leaves:
  - leaf_id: req:A.5.23:cloud_services_policy
    control_ref: A.5.23
    role: policy
```

**`rag/intake/doc_discovery.py`** — fingerprint matcher (filename + body
sample). Same tokenizer as workbook discovery. Returns DocProposal list
ranked by confidence; caller unions target_controls.

**`rag/intake/extractor.py:_scope_controls_via_doc_mappings`** — replaces
the broad pre-filter. When a mapping matches above confidence_floor=0.5,
the LLM candidate set scopes to matched leaves' parent controls only.
Soft fallback to legacy `DOC_TYPE_CLAUSE_MAP` when no mapping matches —
older docs continue working.

**Extractor prompt + post-process tightenings** (orthogonal but landed
the same session):
- Prompt: "The bar is HIGH. Bind ONLY when (a) substantive coverage,
  (b) verbatim ≥40-char quote." Top-15 controls per chunk cap.
- Parser: drop confidence='low'; drop evidence quotes < 40 chars; drop
  quotes that don't appear verbatim in doc text (hallucination check);
  enforce 15-finding cap per chunk.

**`scripts/generate_doc_mappings.py`** — bulk-generates per-leaf scaffolds
for every doc-shaped curated leaf (policy/procedure/plan/scope_note/etc.).
Same tokenizer + abbreviation logic as `generate_register_yamls.py`. The
fingerprint generator deliberately blacklists 2-token fallbacks composed
only of generic words (information/security/data/isms/info/sec) — without
that, leaves titled "Information Security X" emit cross-matching `[info,
sec]` fingerprints that pollute every "Information Security ..." filename.

**`scripts/validate_doc_mappings.py`** — checks every target_leaves[].
leaf_id resolves to a curated `EvidenceRequirement` (top-level or
`DerivedSpec.direct_evidence`).

**`rag/intake/doc_pipeline.py --original-name`** + auto-resolve from
`document_uploads.storage_path`. Closes the CLI-side UX gap where
re-extracting an existing upload used the UUID-named on-disk basename
as `doc.original_name`, which doesn't match any filename fingerprint.

## Corpus state (2026-06-08)

291 doc mappings total:
- 4 hand-authored canonical YAMLs (umbrella shapes, multi-leaf targets):
  - access_control_policy.yaml → A.5.15 + A.5.16 + A.5.17 + A.5.18
  - supplier_security_policy.yaml → A.5.19 + A.5.20 + A.5.21 + A.5.23
  - business_continuity_policy.yaml → A.5.29 + A.5.30
  - information_security_policy.yaml → 5.2 + A.5.1
- 287 generator scaffolds (per-leaf) for the remaining policy / procedure
  / plan / scope_note / privacy_notice / etc. leaves
- Coexistence: umbrella mappings and per-leaf scaffolds can both match
  one upload; discovery unions target_controls cleanly.

## Over-attribution cleanup on Arion (2026-06-08)

Re-extracted the 3 historically over-attributed policy docs against the
tightened path:

| Doc                                | Before | After |
|------------------------------------|-------:|------:|
| Access Control Policy.docx         | 94 findings | **4** (A.5.15-18) |
| Supplier Vendor Security Policy.docx | 46 findings | **3** (A.5.19/20/23) |
| Business Continuity Policy.docx    | 33 findings | **2** (A.5.29/30) |
| Total                              | 173    | **9 (-94.8%)** |

Procedure (`/tmp/reextract_policies.py`):
1. Soft-delete (`is_active=FALSE`) the 173 existing findings on these
   3 docs — kept for audit, removed from engine view.
2. Re-run reader → enricher → extractor → INSERT new findings at
   `review_status='pending'`, keyed to existing client_document_ids.
3. Bypass the pipeline's markdown dedup that would otherwise block a
   normal re-run.

Tenant approved Stage-1 for all 9 new findings. Engine sweep produced
3 Stage-2 NC-downgrade proposals (A.5.1 + A.5.23 + A.5.34) — all
genuine cases where the previous Comply/OFI was a false positive from
the over-attribution. Tenant approved all 3 downgrades. Final live
posture: 14 Comply / 6 OFI / 171 NC.

A.5.34 worth noting specifically: previously Comply via "✓ Privacy and
PII Protection Policy" — the curated leaf TITLE that surfaced was the
SPEC'S expected artefact name, not the doc filename. The actual
evidence was the Supplier Vendor Security Policy LLM-misattributed via
Phase-1 coarse-match. Tenant never uploaded a real Privacy/PII policy
doc; the Comply was fake; NC is the honest state.

## How to apply

- **Authoring a new doc_mapping**: copy the closest existing YAML
  (umbrella for multi-leaf, scaffold for per-leaf). Validate with
  `scripts/validate_doc_mappings.py`. Verify match via
  `rag/intake/doc_discovery.discover_doc()` against the expected
  filename.
- **Regenerating Tier scaffolds**: `python3 scripts/generate_doc_mappings.py`
  is idempotent; won't overwrite existing files.
- **Tenant vocabulary mismatch** (e.g. "Cryptographic Controls Policy"
  tenant filename vs "Use of Cryptography Policy" curated title):
  hand-tune the relevant YAML's `filename_fingerprints` with the tenant's
  abbreviation, same workflow as workbook intake.
- **Re-extracting an existing upload** through the new path: use
  `scripts/discover_workbook.py` analog OR `rag/intake/doc_pipeline.py
  --file <storage_path> --original-name "Foo.docx" --tenant-id <uuid>
  --dry-run` to preview. For non-dry-run, bypass markdown dedup either
  by reusing the original `--upload-id` or by direct script (see
  `/tmp/reextract_policies.py` pattern).

## Related

- [[workbook-intake-corpus-v1-complete]] — the architectural sibling
  this mirrors (workbook intake YAMLs).
- [[a523_policy_attribution_2026_06_07]] — the original incident report
  surfaced via A.5.23 verdict-tree investigation (referenced from
  in-code comments).
- [[compose-posture-any-progress-ofi]] — verdict rule that interprets
  the cleaned-up findings.
