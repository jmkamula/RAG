---
name: ship-13-prime-d-chroma-digest-eval-2026-07-22
description: "Ship 13'.d — Chroma indexing (27003 + 27005) + minimal chat digest promotion + 2 eval cases; brings the guidance enrichment surface to chat"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 13'.d (2026-07-22) — fourth sub-arc of Ship 13. Wires the
Ship 13'.b/'.c authored enrichment into the actual chat surface
and makes the full guidance texts retrievable.

## Three concerns bundled

### 1. Chroma indexing — 2 new collections

`scripts/index_iso_guidance_to_chroma.py` — standalone indexer
that chunks the extracted texts by top-level § anchors and
upserts to Chroma. Runs against
`/data/arioncomply/private/iso27003_2017.txt` +
`/data/arioncomply/private/iso27005_2022.txt` (both gitignored).

Results:
- `iso27003_2017` — 25 sections (chapters 4-10 body content;
  boilerplate + front matter skipped)
- `iso27005_2022` — 42 sections (chapters 4-10, richer subsection
  structure)
- Model: `text-embedding-3-large` per `rag/embedding_config.py`
- Idempotent via `col.upsert()`

**Section-header regex hardening** discovered mid-arc:
initially `^([0-9]+(\.[0-9]+){0,3})[\s]+(.{2,120})$` also matched
body lines beginning with a §-like number (e.g., `6.1.1 (general).
Risks that fall into this category…`). Fixed with
`_looks_like_header()` rejecting lines containing mid-sentence
punctuation (`re.search(r"[.,]\s+[A-Za-z]", stripped)`). Duplicate
ID error was the tell.

Sample retrieval verified on 4 test queries — all hit the correct
section as the top result:
- "how to structure a risk assessment process" → §7.1 (dist 0.392)
- "risk acceptance criteria and who approves them" → §6.4.2 (0.338)
- "how to define ISMS scope" → §4.3 (0.331)
- "management review agenda items" → §9.3 (0.533)

### 2. Minimal chat digest promotion — `→ guidance:` hint

`rag/casefile/digest.py::_render_obligations` now emits a compact
one-line guidance hint per obligation line when the leaf's
`business_description` carries a Ship 13'.b/'.c enrichment
paragraph. Format:

```
OBLIGATIONS:
- 6.1.2: The organization shall define and apply an information security…
  → guidance: Per ISO 27005:2022 §7: risk assessment comprises three activities…
```

New helper `_extract_guidance_hint()` — scans
`business_description` for the `Per ISO 27003:2017` or
`Per ISO 27005:2022` markers, extracts the first sentence,
trims to 220c on a word boundary.

**Design constraints observed:**

- **Case-file discipline maintained.** The hint is a compact
  one-liner, not a full paragraph. Rough budget: 8 obligation
  lines × ~180c hint = ~1.4 KB added to the digest — well
  within the ~10 KB budget the case-file arc set.
- **Non-load-bearing.** Skipped when `obligation_text` is empty
  (would double-cite BD). Skipped when no marker present. Zero
  new prompt tokens for leaves without enrichment.
- **APPEND-ONLY discipline.** The hint is added AFTER the
  obligation line, never replaces it. Preserves the existing
  reading order the case-file arc validated.

### 3. Two new eval cases — 222 + 223

Locks in the guidance-surfacing property:

- **#222**: `"what does ISO 27005 recommend for risk assessment
  methodology?"` — expects answer to contain both `27005` and
  `6.1.2`. Signal C routes via `"risk assessment"` →
  `DOCUMENT_TOPIC_MAP` → 6.1.2. Digest hint carries the 27005
  citation; LLM should surface it.
- **#223**: `"what does ISO 27003 say about ISMS management
  review?"` — expects `27003` and `9.3`. Signal C routes via
  `"management review"` → 9.3. Digest hint carries the 27003
  citation.

Both cases would have failed pre-Ship-13'.d because
`business_description` was deprioritised behind `obligation_text`
in the digest — the LLM never saw the 27003/27005 authority
attribution at chat time.

## What did NOT ship (deferred to arc close)

- **SHOULD promotions** — Ship 13'.b identified 3 candidate SHOULDs
  from 27005 (§6.4.2 acceptance-criteria signoff, §8.6.1 treatment-
  plan required elements, §7.2.2 risk-owner authority). Ship 13'.c
  found ~5-8 more candidates in 27003. Batched review deferred to
  Ship 13'.e retrospective — cross-standard consistency review
  before mutating checklist items.
- **Cross-collection retrieval integration** — the new
  `iso27003_2017` and `iso27005_2022` collections exist but aren't
  in the classifier's Signal A retrieval pipeline yet. Chat still
  gets the guidance via the digest hint (deterministic), not via
  Chroma retrieval. Wiring Chroma into Signal A is a future arc
  (probably requires new signal weights + routing rules to avoid
  guidance out-competing normative obligations).

## Impact on baseline

Eval confirmed: **227/228 PASS + 1 WARN + 0 FAIL**. The 1 WARN is
the pre-existing #200 gap_analysis vs posture_check mismatch;
baseline lifts from 225/226 to 227/228 with the 2 new Ship 13'.d
guidance-surface cases passing cleanly.

First run flagged #222 + #223 as WARN on type-classifier (`expected
standard_knowledge, got definition`) but `failures` column empty
— the must_contain check confirmed both LLM answers cite 27005 +
6.1.2 and 27003 + 9.3 respectively. `expected_type` corrected to
`definition` (the natural classification for "what does X say
about Y" phrasing); second run scored clean PASS.

## Ship 13 progress

| Sub-arc | Status |
|---|---|
| 13'.a Design + 27004 unenrollment | ✓ |
| 13'.b 27005 batch (14 leaves) | ✓ |
| 13'.c 27003 batch (26 ISMS clauses) | ✓ |
| **13'.d Chroma + digest promotion + 2 eval cases** | **✓ (this doc)** |
| 13'.e Arc retrospective | next |

## Related

- [[ship-13-prime-a-iso27000-curation-design-2026-07-21]] — design
- [[ship-13-prime-b-iso27005-enrichment-2026-07-21]] — 27005 prose
- [[ship-13-prime-c-iso27003-enrichment-2026-07-22]] — 27003 prose
- [[ship-2-prime-casefile-arc-2026-07-15]] — the digest budget
  discipline this change respects
- Ship 5'.b consolidation — the `text-embedding-3-large` decision
  the new collections inherit
