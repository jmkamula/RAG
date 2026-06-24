---
name: doc-mapping-training-awareness-2026-06-24
description: "Authored 2026-06-24: db/doc_mappings/training_awareness_policy.yaml — umbrella A.6.3 mapping. Closes the three zero-finding docs from the re-extract workstream: Training & Awareness 0→17 bound; TOC 0 is correct (filename-heuristic skip); Access_Control_Policy.docx (underscored) marked failed (storage_path missing, superseded by canonical)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

Three docs in Arion's corpus produced 0 findings after the
2026-06-23 doc re-extraction workstream. Diagnosis:

| Doc | Cause | Resolution |
|---|---|---|
| Training and Awareness Policy.docx | doc_mappings vocabulary gap — A.6.3 per-leaf scaffolds required "education" + "training" / "education" + "awareness"; Arion uses "Training and Awareness Policy" with no "education" | New umbrella YAML `training_awareness_policy.yaml` widens vocabulary; matches at 0.9 |
| TOC Information Security Documents.docx | extractor TOC-skip heuristic (filename token 'toc') | **Correct behavior** — doc is a literal table of contents, no extractable evidence; verified by reading content |
| Access_Control_Policy.docx (underscored) | storage_path missing on disk (orphan upload row from pre-current-storage scheme) | Marked `extraction_status='failed'` with `error_message`; canonical "Access Control Policy.docx" (with space) supersedes |

## Training & Awareness — root cause + fix

A.6.3 has two auto-generated per-leaf scaffolds:
- `iso27001_2022_a_6_3_audience_curriculum_scope.yaml`:
  fingerprints `[audience, curriculum]` — too literal
- `iso27001_2022_a_6_3_security_awareness_programme.yaml`:
  fingerprints `[education, training, programme]` /
  `[awareness, education, training]` / `[awareness, education]`
  — ALL require "education"

Arion's filename "Training and Awareness Policy" tokenises to
`[training, and, awareness, policy]` — no "education", so all
A.6.3 fingerprints fail. The LLM then falls through to broader
matches via topic-token leakage from the enricher:

- `supplier_security_policy(0.9)` matches because the Arion doc
  mentions "third-party vendors" in scope, and the enricher emits
  topic tokens like `[supplier, vendor, third, party]`. These
  union with filename tokens, so the supplier mapping's
  `[supplier, security, policy]` fingerprint matches (filename
  contributes "policy"; topics contribute "supplier" + "security").
- `Art.25 DPbD` + `Art.35 DPIA` match similarly via privacy topics
  ("data subject rights", "DPIA" mentioned in scope text).

The LLM then correctly returns 0 findings — the doc isn't actually
about suppliers or DPIA, and Direction-C grounding rejects
fabricated quotes.

Fix: hand-authored `training_awareness_policy.yaml` umbrella
covering the full A.6.3 family (security_awareness_programme +
audience_curriculum_scope + training_completion_register +
awareness_programme_review). 16 filename fingerprints + 10 body
fingerprints capture the common security/privacy-training shape.

Result: Training and Awareness Policy.docx 0 → 17 bound findings
(16 on A.6.3 + 1 cross-control on A.5.34 PII protection).
Supplier mapping STILL matches at 0.9, but now the LLM has A.6.3
leaves with appropriate evidence requirements and binds against
those.

## TOC doc — correct skip

Inspected actual content: pure table of contents listing
A.5.x/A.6.x/A.7.x/A.8.x policy and process documents with
one-line purposes. No evidence of compliance — just metadata
about other docs. Extractor's filename-token TOC skip is the
right behavior. Future tenants who upload similar index docs will
get the same correct skip.

## Access_Control_Policy.docx — orphan

Upload row exists (id `a99aba3e-84a8-48f7-abe2-8f8caaf35add`)
but `storage_path` points to a file that doesn't exist on disk.
`sha256` is NULL. This is a pre-current-storage-scheme stub that
was never properly seeded with bytes. The canonical version
"Access Control Policy.docx" (with space, id `3d09a52b`, sha
`0c8aaa914c89`) supersedes it semantically — has 22 active
bound findings.

Marked `extraction_status='failed'` with `error_message`
explaining the orphan + the canonical's upload_id. This prevents
the orphan from being re-extracted unnecessarily and surfaces
the situation if someone investigates.

## Pattern: filename vocabulary gaps

The auto-generated per-leaf doc_mapping scaffolds use literal leaf
titles as token bags. When tenants use vocabulary variations
("Training and Awareness" vs "Education and Training Programme"),
the scaffolds miss and topic-token leakage causes incorrect
fallback matches.

The mitigation pattern (hand-authored umbrella YAMLs covering a
family of leaves with broader vocabulary) is documented in
existing examples: `access_control_policy.yaml`,
`supplier_security_policy.yaml`,
`business_continuity_policy.yaml`. Adding
`training_awareness_policy.yaml` continues the pattern.

Future tenants with vocabulary-divergent doc names: add a
hand-authored umbrella YAML for that family.

## Related

- [[doc-reextraction-workstream-2026-06-23]] — the workstream
  that surfaced these 3 zero-finding docs
- [[doc-curation-engine-v1]] — Direction C extractor with
  per-MUST binding + grounding
- [[intake-quality-telemetry]] — admin-quality dashboard where
  zero-finding docs would surface for review
- [[doc-discovery-vocabulary-gap-fix]] — earlier fix for
  filename↔leaf-title vocabulary gaps at the tokenize/enricher
  level; this fix is the YAML-side complement
