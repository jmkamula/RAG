---
name: ship-13-prime-arc-retrospective-2026-07-22
description: "Ship 13' arc retrospective — ISO 27000-family MUST-level curation; 5 sub-arcs across 2 days; all 3 guidance families curated + Chroma-indexed + surfacing at chat"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 13' arc — ISO 27000-family curation. Followed directly from
Ship 12' (audit + enrollment stub) once source texts became
available. Delivered the deferred MUST-level curation across
ISO 27003:2017, 27004:2016, and 27005:2022 — all three now
curated, indexed, and surfacing to auditor + chat surfaces.

**Arc window:** 2026-07-21 → 2026-07-22. 5 delivery sub-arcs +
this closer over ~1.5 days.

## Sub-arc inventory

| Sub-arc | Delivery | Commit |
|---|---|---|
| 13'.a | Design memo + 27004 unenrollment (edition mismatch) | `673f8b9` |
| 13'.b | 27005 enrichment on 14 risk-adjacent leaves | `32013b4` |
| 13'.c | 27003 enrichment on 26 ISMS clauses (2 renumbering traps fixed) | `3ceeee7` |
| 13'.d | Chroma indexing + digest promotion + 2 eval cases | `8bfabad` |
| 13'.e | 27004:2016 re-enrollment (unplanned, texts arrived mid-arc) | `b5c971a` |
| **13'.f Arc retrospective** | **This doc** | (next commit) |

## What ships from Ship 13'

**Curation output (47 leaves total across all sub-arcs):**
- 14 leaves × 27005:2022 paragraphs (~7.6 KB)
- 26 leaves × 27003:2017 paragraphs (~14 KB)
- 7 leaves × 27004:2016 paragraphs (~4.2 KB)
- Total: ~25.8 KB of authority-cited prose across 40 unique
  leaves (with 8 leaves stacking two families 27003+27005 or
  27003+27004)

**Schema:**
- `schema_v85` unenrolls `ISO27004:2016` (Ship 13'.a)
- `schema_v86` re-INSERTs it (Ship 13'.e — symmetric reversal)

**Chroma collections (3 new):**
- `iso27003_2017` — 25 sections, chapters 4-10
- `iso27004_2016` — 23 sections, chapters 4-8
- `iso27005_2022` — 42 sections, chapters 4-10
- All on `text-embedding-3-large`

**Scripts (5 new):**
- `scripts/scrub_iso27004_citations.py` (Ship 13'.a)
- `scripts/enrich_iso27005_leaves.py` (Ship 13'.b)
- `scripts/enrich_iso27003_leaves.py` (Ship 13'.c)
- `scripts/index_iso_guidance_to_chroma.py` (Ship 13'.d → 13'.e)
- `scripts/enrich_iso27004_leaves.py` (Ship 13'.e)

**Code paths modified:**
- `rag/casefile/digest.py::_render_obligations` — `→ guidance:`
  hint per obligation line when leaf carries `Per ISO 2700X`
  marker (Ship 13'.d + widened in 13'.e)
- `rag/casefile/digest.py::_extract_guidance_hint` — new helper;
  sentence-boundary regex fixed in 13'.e
- `rag/classifier.py` — 3 new DOCUMENT_TOPIC_MAP entries for
  monitoring/measurement queries (Ship 13'.e)

**Vocab (3 new / 1 restored):**
- `rag/output/vocab/iso27003_2017.json` (Ship 12'.b)
- `rag/output/vocab/iso27004_2016.json` (Ship 12'.b → 13'.a
  deleted → 13'.e restored)
- `rag/output/vocab/iso27005_2022.json` (Ship 12'.b)

**Eval cases (3 new):**
- #222 27005 risk methodology surfaces
- #223 27003 management review surfaces
- #224 27004 monitoring + measurement surfaces

**Baseline lift:** 225/226 → **228/229 PASS + 1 WARN + 0 FAIL**
across the arc. Only WARN remains the pre-existing #200
gap_analysis vs posture_check mismatch. Zero regressions.

## Codified lessons

### 1. Enrollment-stub pattern validated by round-trip

Ship 12'.b enrolled 3 guidance standards without curation
content. Ship 13'.a discovered 27004:2016 was the wrong edition
(2009 first-ed PDF) and cleanly unenrolled it. Ship 13'.e then
re-enrolled 27004:2016 (correct 2016 second-ed PDF) with the
same registry shape.

**The round-trip cost was ~2 SQL migrations + 1 vocab file
delete/restore + 1 citation scrub/restore.** Zero
architectural change. The registry infrastructure absorbed the
edition mismatch without touching downstream code.

**Generalisation**: when downstream code needs to recognise a
new entity but the entity's content isn't ready OR is in the
wrong shape, stub the registry entry first. The scrub/restore
scripts complementary to `enrich_X.py` scripts remain in the
repo as documentation of the reversible discipline.

### 2. Cross-version renumbering trap (27001:2013 → :2022)

Ship 13'.c uncovered TWO renumbering traps that dry-run pre-
write caught:

- **§10.1 ↔ §10.2 swap** — 27003:2017 (indexed to 27001:2013)
  has §10.1=Nonconformity, §10.2=Continual improvement.
  27001:2022 swapped them. First-draft enrichment matched by
  number and would have published nonconformity content under
  a continual-improvement leaf.
- **§6.3 (Planning of changes) is new in 27001:2022** —
  27003:2017 has no §6.3, so first-draft citation was a phantom.

**Lesson**: curating from an older guidance edition against a
newer normative edition requires cross-version mapping.
**Cross-check Neo4j `title` field against enrichment content in
dry-run BEFORE live write.** Both traps surfaced this way and
were fixed with 3 lines each (explicit renumbering notes).

Retroactively confirms Ship 3'.l (2026-07-17) which fixed the
same 2013→2022 renumbering in source JSONs. Same shape of
trap, different context, same fix pattern.

### 3. Guidance-not-normative discipline held throughout

Across 47 leaves × 3 families, **zero new MUSTs were added
from guidance content**. All enrichment lives in
`business_description` prose. Auditor-facing surfaces get the
authority attribution + implementation guidance; engine
verdicts stay untouched.

3 candidate SHOULDs identified in Ship 13'.b (27005 §6.4.2 j)
signoff, §8.6.1 treatment-plan elements, §7.2.2 risk-owner
authority); more candidates surfaced in 13'.c + 13'.e but were
NOT harvested. Deferred to a future review batch (see below).

Rationale: any SHOULD promotion can flip existing tenant
postures. Batching them into a cross-standard review pass —
where a curator can judge consistency across 27003 + 27004 +
27005 together — is safer than piecewise addition per sub-arc.

### 4. Minimal digest promotion pattern

Ship 13'.d's `→ guidance:` hint injection is the minimal
integration that closes the loop between authored enrichment
and chat surface. Design constraints observed:

- **Non-load-bearing.** Skipped when `obligation_text` empty;
  APPEND-ONLY; never rewrites LLM prose.
- **Case-file discipline respected.** ~180c/leaf × 8 obligation
  lines = ~1.4 KB — well within the ~10 KB digest budget the
  Ship 2' arc set.
- **Vocabulary-driven.** New markers (27004:2016 in 13'.e)
  extend the recognised set without touching digest rendering
  logic.

This pattern generalises: when a curation arc adds authored
prose to `business_description`, promotion into chat can be a
compact one-liner extracted from the paragraph rather than
digest-priority-swap.

### 5. Empirical text verification before scaling

Ship 13'.a's 27004 edition-mismatch discovery came from
looking at the extracted text 60 seconds after receiving the
PDF — spotting `First edition 2009-12-15` vs the enrolled
`ISO27004:2016` was the difference between a wasted sub-arc
and a clean skip.

The user's original data-driven-hypothesis lesson (Ship 8'
retrospective, 2026-07-20) applied here: **verify what's
actually there before building against the assumption of what
should be there**. Cost: ~2 minutes of extract-and-grep. Value:
one avoided sub-arc that would have published wrong content.

## Deferred to Ship 14+

**SHOULD-promotion review batch** across all 3 guidance
families. Candidate list:
- 27005 §6.4.2 j) risk-acceptance-criteria signoff → 6.1.2
- 27005 §8.6.1 treatment-plan required elements → 6.1.3
- 27005 §7.2.2 risk-owner authority check → 6.1.2
- 27004 §6.5 measurement roles enumeration → 9.1
- 27003 §5.1 (a)-(h) top management commitment checklist → 5.1
- (more candidates in 27003 §6.2, §7.3, §9.2, §9.3)

**Cross-collection Chroma retrieval into Signal A**. The 3 new
Chroma collections exist but aren't yet part of the
classifier's retrieval pipeline. Chat gets guidance via the
deterministic digest hint. Wiring Chroma into Signal A
requires signal-weight decisions (guidance should not
out-compete normative obligations) and a new query-routing
rule for "how do I implement X" phrasings.

**Stacked-paragraph ordering discipline**. Leaves with both
27003 and 27005 enrichment currently show the 27005 paragraph
first (via 13'.b sequencing) then 27003 (via 13'.c). Citation
footer lists them alphabetically. A cross-standard reading
order pass could re-order to match footer if desired — low
priority.

**27004 SHOULD-candidate collection**. Ship 13'.e's rushed
build skipped explicit SHOULD-candidate identification. A
retrospective read of the 27004 authoring notes should
surface at least 2-3 more candidates for the batched review.

## Baseline throughout

| Sub-arc | PASS | WARN | FAIL |
|---|---|---|---|
| Start (Ship 12'.d close) | 225/226 | 1 | 0 |
| After 13'.b (27005) | 225/226 | 1 | 0 |
| After 13'.c (27003) | 225/226 | 1 | 0 |
| After 13'.d (digest + 2 cases) | 227/228 | 1 | 0 |
| **After 13'.e (27004 + 1 case)** | **228/229** | **1** | **0** |

Zero regressions across the arc despite 47 leaves of Neo4j
mutation, 3 new Chroma collections, 1 digest-code change with a
mid-arc sentence-boundary regex fix, and 3 new eval cases.

## Ship 13' close

| Sub-arc | Status |
|---|---|
| 13'.a Design + 27004 unenrollment | ✓ |
| 13'.b 27005 batch (14 leaves) | ✓ |
| 13'.c 27003 batch (26 ISMS clauses) | ✓ |
| 13'.d Chroma + digest + 2 eval cases | ✓ |
| 13'.e 27004:2016 re-enrollment | ✓ |
| **13'.f Arc retrospective** | **✓ (this doc)** |

Total: 5 delivery sub-arcs + closer. Second-largest Ship arc
count after Ship 11' (5 + closer) and Ship 4' (7 + closer).

## Related

- [[ship-12-prime-arc-retrospective-2026-07-21]] — the audit +
  enrollment-stub arc this one built on
- [[ship-13-prime-a-iso27000-curation-design-2026-07-21]] —
  design memo (also captures 27004 skip decision)
- [[ship-13-prime-b-iso27005-enrichment-2026-07-21]] — 27005 batch
- [[ship-13-prime-c-iso27003-enrichment-2026-07-22]] — 27003 batch
  + renumbering-trap lesson
- [[ship-13-prime-d-chroma-digest-eval-2026-07-22]] — digest hint
  mechanism
- [[ship-13-prime-e-iso27004-reenrollment-2026-07-22]] — 27004
  re-enrollment
- [[ship-2-prime-casefile-arc-2026-07-15]] — the digest budget
  discipline this arc respected
- [[ship-8-prime-arc-retrospective-2026-07-20]] — "verify
  hypotheses against data BEFORE building" — applied by 13'.a
  when spotting the 27004 edition mismatch
- Ship 14+ candidate: SHOULD-promotion review batch (see
  Deferred section above)
