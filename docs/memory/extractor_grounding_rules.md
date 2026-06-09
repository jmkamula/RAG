---
name: extractor-grounding-rules
description: "SHIPPED 2026-06-09 (f5a4f95 + 64cdcc8): _evidence_grounded checks LLM citations against both full_text AND markdown, with punctuation normalised. Today's BCP doc went 0 findings → 3 findings."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The verbatim-quote check protects against LLM hallucination (made-
up citations) but historically had two false-negative modes that
silently dropped real evidence. Today's Business Continuity and
Disruption Response Plan upload hit both before they were fixed:

  - 1st upload: 0 findings (the entire grounding model was broken
    for list-item content)
  - 2nd upload: 1 finding (source-coverage fix landed; 2 still
    dropped on punctuation drift)
  - 3rd upload: 3 findings (punctuation-tolerant grounding landed)

## Two false-negative modes the fix closes

**1. Source-coverage gap (commit f5a4f95).** The check used
`doc.full_text` only — paragraph-walk output. For docx, mammoth
captures more than the paragraph walker (lists, table cells,
appendix entries). The LLM is fed `doc.markdown` (full content),
but the grounding check looked in `doc.full_text` (partial). Any
citation from list/table content was rejected as hallucinated even
though it was real doc content.

  Fix: check both sources — `doc.full_text` AND `doc.markdown`.
  Citation grounds if either contains the (normalised) needle.

**2. Punctuation drift (commit 64cdcc8).** The LLM routinely cites
bullet lists with semicolons inserted between items, but the
source text (paragraph walk OR mammoth markdown) renders bullets
with dashes / hyphens / commas / no separator. The first-50-char
substring check failed on these tokens.

  Example from the BCP doc:
    LLM:    `"Revoke affected credentials via Azure AD; Initiate scan..."`
    Doc:    `"revoke affected credentials via azure ad - initiate scan..."`

  Fix: strip non-word/non-space characters from BOTH needle and
  haystack before substring match. `_ground_normalize` lowercases,
  removes `[^\w\s]`, collapses whitespace. Word content + order
  decide grounding; punctuation is noise that varies with
  rendering.

## How to extend

If a new false-negative mode emerges (e.g. LLM citing across
non-adjacent lines with a `…` ellipsis it inserted), extend
`_ground_normalize` rather than weakening the substring check.
Levenshtein / word-overlap is the next-tier fix if/when needed —
the current substring approach is cheap and explainable.

If a false-POSITIVE emerges (LLM paraphrases with the same words
but different meaning passes the check), tighten by requiring
adjacency or a longer needle window. The 50-char window post-
normalisation is the lever.

## Why we don't trust the LLM's own "verbatim" promise

The system prompt instructs `Quote must be a real, verbatim
substring of the document. Hallucinated quotes are auto-rejected.`
Models reliably IGNORE the verbatim instruction when the
information they want to cite spans multiple lines or contains
formatting. They preserve the WORDS but invent punctuation /
separators. Both fixes work around that observed behaviour.

## Diagnostic signal

`intake_trace_log.dropped_hallucinated > 0` is the canonical
signal that grounding is rejecting LLM output. Read the dropped
quotes (instrument `_evidence_grounded` to log the rejected
needle) before assuming the LLM is genuinely hallucinating —
today's BCP proved most "hallucinations" were punctuation drift.

## Related

- [[table-heavy-docx-rescue]] — same paragraph-vs-markdown gap on
  the *extraction* side; this is the analog on the *grounding*
  side.
- [[intake-quality-telemetry]] — the signal that catches grounding
  false-negatives via `dropped_hallucinated` counter.
- [[feedback-telemetry-before-trouble]] — today's grounding fix is
  the first real-world telemetry-caught bug.
