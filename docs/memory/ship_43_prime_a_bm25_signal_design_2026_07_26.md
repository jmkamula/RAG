---
name: ship-43-prime-a-bm25-signal-design-2026-07-26
description: "Ship 43'.a design memo — BM25 lexical scoring as new consensus_extraction signal. Companion to must_semantic_topk (embedding-based). Uses rank_bm25 (BM25Okapi, MIT, pure Python, ~200 LOC dep). Per-doc index over doc sections; query each MUST's text; top-K MUSTs by BM25 score emit candidates. Weight 0.25 (between fingerprint 0.50 and must_semantic 0.30 — lexical fuzzy is stronger than semantic-only but weaker than exact fingerprint token match). Discovery mode: emits new candidates outside scoped_leaf_ids like must_semantic does."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 43'.a — design memo for BM25 lexical signal in
consensus_extraction.

## Motivation

Ship 40'.b unlocked cross-framework extraction; Ship 42'.b fixed
multi-attribution via dedup. Current 8 signals cover:

- **Discovery** (broaden candidates): explicit_ref, doc_mappings_target,
  fingerprint_keyword, must_semantic_topk, per_protocol_scope
- **Filter** (narrow / penalize): semantic_fit_gate,
  content_shape_penalty, evidence_uniqueness

The discovery layer has two token-based signals
(fingerprint_keyword, must_semantic_topk) with distinct
matching semantics:

- **fingerprint_keyword** — exact-token-set match against curated
  keyword catalog. Binary: matches or doesn't.
- **must_semantic_topk** — Chroma embedding similarity between
  doc text and MUST text. Semantic (paraphrase-tolerant).

Gap: **lexical fuzzy matching**. A doc might use different words
than the fingerprint catalog AND semantically-different phrasing
(rare edge cases). BM25 is the industry-standard lexical
relevance score — it catches lexical variants that fingerprints
miss without requiring embedding similarity.

## Why BM25 over TF-IDF or exact keyword

- **BM25 vs TF-IDF**: BM25 has saturating term frequency (log-like
  curve) + doc length normalization. Better ranking on short vs
  long docs. Industry default.
- **BM25 vs exact keyword** (fingerprint_keyword): BM25 gives
  graded score (0.0-N.0 typical range). Binary-firing false
  positives get muted; near-matches boost.
- **BM25 vs semantic embeddings** (must_semantic_topk): BM25 is
  lexical (word-based) — catches "revocation record" vs
  "revocation log" as similar (share "revocation"); embeddings
  might catch "credential retirement audit" via semantic
  paraphrase but miss because tokens don't overlap.

Complementary — hence a new signal, not a replacement.

## Library choice — rank_bm25

`rank_bm25` on PyPI:
- MIT license, pure Python, ~200 LOC, no C extensions
- Standard BM25Okapi implementation
- Zero deploy risk on the Azure VM
- Standard interface: `BM25Okapi([tokens_per_doc])` → `.get_scores(query_tokens)`

Alternative rejected:
- **whoosh** — full-text search engine, overkill (~5k LOC)
- **Elasticsearch** — deployable but adds JVM + separate service
- **PyLucene** — heavy JNI dep

Add to requirements: `rank-bm25>=0.2.2`.

## Architecture — where BM25 lives

New signal file: `rag/intake/consensus_extraction/signals/bm25_topk.py`.

Registered in `rag/intake/consensus_extraction/signals/__init__.py`.

Wired into `orchestrator.py` in round 1 (parallel with other
discovery signals). Runs on `widened_leaf_ids` (post-must_semantic
widening).

## Signal semantics

**Input**: `doc` (ParsedDocument with markdown text or sections),
`scoped_leaf_ids` (post-widening), `cfg`.

**Output**: `ExtractionSignalOutput` with candidates dict —
`(leaf_id, must_id) → cfg.bm25_weight` for each top-K MUST above
score floor.

**Processing**:

1. Fetch all MUST texts + their (leaf_id, must_id) from
   `_fetch_leaf_musts(scoped_leaf_ids)`. Tokenize each MUST.
2. Tokenize doc text (or doc sections concatenated). Simple
   lowercasing + `re.findall(r"\b\w+\b", ...)`. No stemming for
   v1 — keep dependencies minimal.
3. Build `BM25Okapi([must_tokens_1, must_tokens_2, ...])`
   over MUSTs (2595 × ~10 tokens; sub-second on this scale).
4. Query with doc tokens → scores per MUST.
5. Take top-K MUSTs (K = `cfg.bm25_topk`, default 30). Filter
   below score floor (`cfg.bm25_score_floor`, default 1.0 —
   avoids weak lexical matches spamming candidates).
6. Emit each surviving (leaf_id, must_id) with
   `cfg.bm25_weight`.

Alternative considered: BM25 over doc sections queried with MUST
text (inverse indexing direction). Ruled out because MUST texts
are consistent + persistent — indexing them once per doc has
symmetric cost + reveals which MUSTs the doc "sounds like".

Actually — MUST-centric indexing means one BM25 index per doc
(rebuild each extraction). Fast but not persisted. Alternative:
persist a global MUST BM25 index in Chroma-adjacent shape.
V1 rebuilds per-doc; V2 could persist if latency matters.

## Weight and thresholds

Proposed initial:
- `bm25_weight: float = 0.25`
- `bm25_topk: int = 30`
- `bm25_score_floor: float = 1.0` (BM25Okapi scores typically
  0.0-10.0; 1.0 rules out weak matches)

Rationale for 0.25:
- Below fingerprint_keyword (0.50) — fingerprints are curated
  exact-token-set match; BM25 is fuzzy
- Similar to must_semantic (0.30) — both are discovery signals
- Above per_protocol (0.10) — BM25 attests to the specific doc,
  per_protocol is broad framework hint

**Discovery-mode**: like must_semantic_topk (post Ship 39'.b),
BM25 emits candidates OUTSIDE scoped_leaf_ids (any MUST from the
2595 catalog can surface). The orchestrator widens using union of
must_semantic + BM25 candidates.

## Orchestrator changes

`orchestrator.py` — one insertion:

```python
# Ship 43'.b — BM25 as second discovery-mode signal
sig_bm25 = bm25_topk.compute(doc, scoped_leaf_ids, cfg)

widened_leaf_ids = list({
    *scoped_leaf_ids,
    *(lid for (lid, _mid) in sig_must_semantic.candidates.keys() if lid),
    *(lid for (lid, _mid) in sig_bm25.candidates.keys() if lid),
})
```

The union widening pattern from Ship 39 extends naturally.

Signals list grows from 8 → 9.

## Expected impact — hypothesis

BM25 will:

1. **Add candidates on lexical-drift MUSTs** — where the doc uses
   the MUST's vocabulary but not the exact fingerprint tokens.
2. **Not add many candidates on well-fingerprinted MUSTs** —
   fingerprint_keyword already catches these; BM25 provides
   corroboration (same candidate, additional weight) not new
   candidates.
3. **Corroborate cross-framework findings** — Art.35 MUSTs on
   DPIA doc likely score high on BM25 (doc explicitly discusses
   DPIA topics with GDPR-adjacent vocabulary).

**Prediction**: +5-15% new candidates surfaced, mostly
corroborating existing accepts. Modest recall improvement
(possibly 5-10 more accepts across 5 Ship 10 docs).

**Not expected**: massive discovery blowout — BM25's graded scoring
+ score floor + evidence_uniqueness downstream all constrain
runaway multi-attribution.

## Ship 43'.c re-measurement plan

Compare Ship 42'.b baseline (74 accepts, 33 unique groups on 5
Ship 10 docs) vs Ship 43'.b:
- Total accepts (should hold or grow)
- Unique groups (should hold — dedup is orthogonal to BM25)
- Latency per doc (should stay < 60s)
- Eval baseline (must hold at 231/232+)

HITL: sample any new accepts BM25 introduces (expect ~5-10).
Verify they're genuinely lexical-drift catches, not noise.

## Framework role + case-file alignment

**Role model**: BM25 is a discovery-layer signal. Runs on ALL
enrolled standards' MUSTs (widening pattern). Phase 3 filter
bypass under consensus (Ship 40) already ensures cross-framework
MUSTs are in scope.

**Case-file model**: Chat pipeline reads posture, not raw
findings. BM25 affects extraction only. No case-file changes.

## What Ship 43 does NOT do

- **Global persistent BM25 index** — v1 rebuilds per-doc; v2
  candidate if latency matters
- **Stemming / stopword lists** — simple tokenization suffices
  for v1; language-specific preprocessing is future work
- **Score-based normalization** — top-K + score floor is
  sufficient; explicit normalization deferred
- **BM25F (fielded BM25)** — MUST text is one field; single-field
  BM25Okapi suffices
- **Retire other signals** — BM25 is additive, not replacement

## Ship 43'.d retro topics

- Did BM25 add discovery breadth? How much?
- Did the weight settle correctly? Any tuning needed?
- HITL surprises — any noise BM25 introduced?
- Latency impact — acceptable?

## Ship 44 preview

OpenTelemetry + Jaeger instrumentation arc. Instrument every data
point for community-backed tracing. Independent arc; opens after
Ship 43 closes.

## Related

- [[ship-42-prime-arc-retrospective-2026-07-26]] — the dedup that
  makes BM25's discovery additions safe
- [[ship-39-prime-arc-retrospective-2026-07-25]] — the widening
  pattern BM25 extends
- `rag/intake/consensus_extraction/signals/must_semantic_topk.py`
  — the closest signal shape BM25 mirrors
- `rag/intake/consensus_extraction/config.py:39-49` — where
  new BM25 weight lives
- `rag/intake/consensus_extraction/orchestrator.py:65-68` —
  where widened_leaf_ids union expands
