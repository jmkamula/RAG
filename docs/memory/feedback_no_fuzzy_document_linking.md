---
name: feedback-no-fuzzy-document-linking
description: "Deterministic linking only between uploads and registered documents — drop fuzzy word-overlap heuristics. Two unrelated docs sharing generic tokens like {ISMS, process, policy} silently conflate; resulting evidence_type swap breaks engine posture verdicts. Use explicit external_ref / exact filename / fresh row — never guess by word overlap."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

When matching an upload to an existing `client_documents` row,
**use only deterministic rules**: explicit reference (DOC-prefix
external_ref), exact filename, or accept a fresh row. Do not
fall back to word-bag overlap on filenames or titles.

**Why:** word-overlap is unprincipled. Two genuinely different
documents in the same domain share generic tokens (`ISMS`,
`process`, `policy`, `document`, `register`). Tweaking the
overlap threshold doesn't fix it; the signal is just too weak.
Bad linking has compound consequences: the upload's enricher
tag overwrites the existing row's `evidence_type`, which then
breaks engine Phase-1 fallback for any control that depends
on the old type. The bug surfaces downstream as posture
regression, far from where the conflation actually happened.

**How to apply:** in any matcher between uploads and a
registered-document table, ladder is:
  1. Explicit ref (DOC-prefix in filename → external_ref)
  2. Exact filename match
  3. (Optional) content-hash equality on file bytes
  4. Otherwise: fresh row

No fuzzy-similarity step. Tenants who want consolidation across
renames register an `external_ref` once and reuse it. No
guessing.

**Scar:** 2026-06-12 — fuzzy word-overlap at
`posture_writer.py:171-196` (≥ 2 shared significant words)
linked `"ISMS Policy and Process Documents Acknowledgment.xlsx"`
to the registered `"ISMS Change Management Process.docx"` row.
Shared tokens: {isms, process}. The upload's tag `'policy'`
overwrote the row's `'procedure'`. Engine then proposed
control 6.3 OFI → NC because no leaf evidence_type is 'policy'.
Removed the fuzzy step in [[posture-writer-drop-fuzzy-match-2026-06-12]];
the principle generalises to any future linking work.

**Generalised principle:** if a matching rule can produce a
wrong answer that's *invisible* to the operator (silent
overwrite, silent merge), the rule needs to be either
explicit-deterministic or removed. Fuzzy heuristics are fine for
producing CANDIDATES that a human or a follow-up validator
confirms (e.g. [[sample-row-anchor-confirmation-2026-06-12]] uses
sample-data anchors to validate fingerprint matches). They are
NOT fine as terminal decisions.

## Related

- [[posture-writer-drop-fuzzy-match-2026-06-12]] — where this
  principle was first crystallised.
- [[feedback-intake-label-unreliability]] — sibling rule about
  intake-side labels being unreliable; same family of design
  consequence (deterministic-then-validate, not heuristic-then-
  trust).
- [[doc-mappings-no-tenant-specific]] — earlier sibling: the
  YAML matching layer should also avoid tenant-specific
  abbreviations (different mechanism, same principle —
  deterministic shared vocabulary, not tenant-specific guessing).
