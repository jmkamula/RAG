---
name: normalizer-annex-a-isms-collision
description: "SHIPPED 2026-06-09 (19ab68c + 0365e3e): two ISO 27001 normalizers both auto-added 'A.' prefix to [5-8].N refs, corrupting ISMS clauses (5.x/6.x/7.x/8.x Leadership/Planning/Support/Operation) by filing them under Annex A storage."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

ISO 27001:2022 has a structural ambiguity: ISMS body clauses 4-10
and Annex A categories A.5-A.8 share the leading digit. At the
2-dot level they collide:

  - ISMS clause 8.2  = Information security risk assessment
  - Annex A.8.2      = Privileged access rights

Format alone can't disambiguate. The codebase carried two
normalizers that BOTH used the same wrong heuristic — "if it starts
with [5-8].N, add A. prefix" — corrupting any ISMS-clause ref into
an Annex A control_ref.

## The two normalizers

1. `rag/intake/ref_normalizer.py:normalize_iso27001` — called from
   the LLM-output parser (`extractor._parse_llm_response:440`),
   workbook header detection (`readers.py:336`), structured row
   extraction (`extractor.py:106`), and ref-scan-in-text
   (`ref_normalizer.py:176`).

2. `rag/framework_refs.py:normalize_control_ref` — called only from
   the writer (`posture_writer.py:490`) when looking up the
   `posture_controls` row to update.

Both had the same bug. Fixing only the extractor-side meant the
writer re-corrupted the (correct) bare ref at write time. **If you
fix one, fix the other** — and check before assuming there's only
one.

## What ships in both normalizers

- 3-dot pattern (e.g. `6.1.1`, `A.6.1.1`): ALWAYS ISMS clause —
  Annex A doesn't have sub-sub-clauses. Strip any `A.` prefix.
- 2-dot pattern (e.g. `8.2`, `5.1`): **never auto-prefix**. Pass
  through unchanged. Callers must supply canonical form.
- `A5.18`/`A 5.18` (no dot after A): canonicalise spacing → `A.5.18`.
- Anything starting `A.` and matching the canonical shape: untouched.

## The companion strict-match in the extractor

`_parse_llm_response` now matches the LLM's returned ref against
the candidate list (`valid_refs` built from `controls[].ref`) BEFORE
falling back to normalize. The LLM is given canonical refs from
doc_mappings; it should echo them back. If it does, accept as-is.
If it doesn't, try normalize; if still unmatched, drop with
`dropped_unknown_ref` counter. Eliminates LLM hallucinations that
slip past the heuristic.

## Trigger case

A Risk Management Policy upload on 2026-06-09 produced 5 findings:
6.1.1, 6.1.2, 6.1.3, 8.2, 8.3. Pre-fix all five landed as A.6.1.1
(doesn't exist in Annex A), A.6.1.2 (doesn't exist), A.6.1.3 (doesn't
exist), A.8.2 (Privileged access — wrong control), A.8.3 (Information
access restriction — wrong control). Three bogus posture_controls
rows created; two collisions overwrote unrelated Annex A controls
with risk-register evidence.

Cleanup steps used: delete bogus 3-dot A-prefixed posture_controls
rows + posture_history (FK cascade); delete the 5 document_findings;
re-upload after restart. The 3-dot rows were uniquely identifiable
via `control_ref ~ '^A\.\d+\.\d+\.\d+$'`.

## How to apply

- When adding a new normalizer caller, prefer the **strict-match-
  against-candidate-list** pattern over normalize_ref. Candidates
  come in canonical form; round-tripping through normalize is risky.
- When debugging a posture row that looks "off" — check if it's a
  3-dot A-prefixed ref (smoke gun for normalizer corruption) or a
  2-dot ref where ISMS clause vs Annex A is ambiguous (look at
  evidence text).
- The dual-normalizer surface is a known scar. Search for both
  `normalize_iso27001` and `normalize_control_ref` when touching
  ref-handling code.

## Related

- [[posture-controls-ref-format]] — the canonical-form convention
  this normalizer was supposed to enforce, not violate.
- [[extractor-section-fallback]] — same extractor pipeline,
  different layer of the over-narrowing pattern.
