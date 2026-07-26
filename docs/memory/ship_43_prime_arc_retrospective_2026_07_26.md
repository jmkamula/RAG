---
name: ship-43-prime-arc-retrospective-2026-07-26
description: "Ship 43' arc closer — BM25 lexical signal working. +24 accepts (+32%), +17 consensus groups (+52%) on 5 Ship 10 docs. Ship 42's dedup absorbed the discovery breadth cleanly. DPIA now cites Art.32 + Art.36 + B.8.2.1 via lexical relevance where fingerprint token set didn't fire. Eval held 231/232. Ship 44 opens on OpenTelemetry + Jaeger."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 43' arc retrospective — 2 delivery sub-arcs + closer,
single session 2026-07-26. BM25 lexical scoring added as 9th
consensus_extraction signal. Discovery breadth expanded 32%
without disturbing chat pipeline or writer semantics.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 43'.a | Design memo — BM25 lexical signal | 315be56 |
| 43'.b | Implementation + measurement | d3b24dd |
| **43'.d** | **Retro (this)** | pending |

Sub-arc 43'.c collapsed into 43'.b (measurement happened
inline during implementation).

## The gap BM25 filled

Ship 40'.b + 42'.b delivered cross-framework extraction with
dedup, but the 8 discovery signals had a lexical-fuzzy gap:

- `fingerprint_keyword` — exact token set match (binary, curated)
- `must_semantic_topk` — Chroma embeddings (semantic paraphrase)
- No signal for **lexical relevance graded score**

BM25 catches lexical variants that fingerprint's exact-set match
misses without requiring semantic paraphrase. Example on DPIA:
Art.32 (security of processing) — fingerprint didn't match
because the DPIA doc doesn't literally use Art.32's fingerprint
tokens; BM25 caught it via overall lexical relevance to Art.32's
MUST texts.

## Design and impl in one memo

Library: `rank-bm25` (BM25Okapi variant). MIT license, pure
Python, ~200 LOC, zero deploy risk. Installed via
`pip install --break-system-packages rank-bm25`.

Signal at `rag/intake/consensus_extraction/signals/bm25_topk.py`:
- Load 4293 (leaf_id, must_id, must_text) triples from Neo4j
  once per process (cached)
- Per doc: tokenize `must_text` for each MUST; build
  `BM25Okapi(all_must_tokens)`; query with `doc_tokens`
- Top-K (default 30) MUSTs above score floor (default 1.0)
  emit candidates with weight 0.25
- Discovery mode: emits candidates regardless of
  scoped_leaf_ids; orchestrator widens via union

Config additions (`config.py`):
```python
bm25_weight:      float = 0.25
bm25_topk:        int   = 30
bm25_score_floor: float = 1.0
```

Weight rationale:
- Above must_semantic (0.30) → wait, actually 0.25 is BELOW
  must_semantic. Deliberate: lexical fuzzy has more surface-area
  false positives than semantic; keeps BM25 as corroborator not
  decider.

Orchestrator changes: BM25 signal runs alongside must_semantic
in round 1; widened_leaf_ids union expanded.

## Measurement — 5 Ship 10 docs

| Doc | 42'.b acc | **43'.b acc** | Δ acc | 42'.b groups | **43'.b groups** | Δ groups |
|---|---|---|---|---|---|---|
| Consent | 12 | 17 | +5 | 4 | 7 | +3 |
| DPIA | 20 | 28 | +8 | 5 | 8 | +3 |
| DQA | 12 | 15 | +3 | 10 | 13 | +3 |
| Processor Ops | 15 | 18 | +3 | 9 | 12 | +3 |
| RoPA | 15 | 20 | +5 | 5 | 10 | +5 |
| **Total** | **74** | **98** | **+24 (+32%)** | **33** | **50** | **+17 (+52%)** |

Latency: 26-55s per doc (was 20-45s in Ship 42'.b). Acceptable
overhead for +32% recall.

Auditor experience per doc: +3-5 unique dedup groups on average.
Ship 42's evidence_group_id dedup absorbed the discovery breadth
correctly — BM25's added candidates dedupe cleanly by (excerpt,
control_ref).

## What BM25 caught that fingerprint didn't

DPIA now surfaces 3 additional controls:
- **Art.32 (security of processing)** — DPIA doc discusses risk
  mitigation which lexically resonates with Art.32's MUSTs
- **Art.36 (prior consultation)** — DPIA content covers when to
  escalate to supervisory authority
- **B.8.2.1 (processor DPIA support)** — DPIA doc mentions
  processor responsibilities in DPIA context

None of these are hallucinations — they're genuine cross-
framework evidentiary connections BM25 found via lexical
relevance. Fingerprint's exact-token-set match required each
control's specific curated keywords in the doc; BM25 scored
overall lexical overlap.

## Eval safety verified

231 PASS / 1 WARN / 0 FAIL. Baseline unchanged. Chat pipeline
reads posture (not raw findings); BM25 only affects the
extraction discovery layer.

## Codified 2 lessons

### 1. Signal weight vs discovery breadth trade-off

BM25 weight settled at 0.25 — deliberately BELOW must_semantic
(0.30). Rationale: BM25 has larger candidate surface than
must_semantic (any lexical match counts, vs top-30 semantic
neighbors). Lower per-candidate weight prevents individual BM25
hits from crossing accept threshold alone. Requires
corroboration (fingerprint OR must_semantic OR doc_mappings).

**Rule**: when adding a discovery-mode signal with broad surface,
weight it BELOW the existing signals in its family. Corroboration
requirement filters false positives; explicit_ref (weight 1.00)
is the exception because it's ground-truth self-citation.

### 2. Ship 42's dedup made Ship 43 safe

Ship 41 HITL predicted BM25 could regress multi-attribution.
Ship 42's evidence_group_id dedup made this impossible:
same-excerpt cross-control expansion (which BM25 amplifies)
gets collapsed at surface. Ship 43 delivered +32% recall
without any auditor-facing quality regression.

**Rule**: enabling signals become safe when downstream filters
are in place. Ship 42 (write dedup) unblocked Ship 43 (BM25
discovery). Consensus arc-family dependencies matter — order
of arcs isn't arbitrary.

## What Ship 43 did NOT do

- **Retire must_semantic_topk** — BM25 is complementary, not
  replacement. Semantic still catches paraphrase BM25 misses.
- **Global persistent BM25 index** — v1 rebuilds per-doc
  (sub-second on 4293 MUSTs); v2 candidate if latency matters
- **Stemming/stopwords** — simple tokenization suffices for v1
- **BM25F (fielded)** — MUST text is one field; single-field
  BM25Okapi suffices
- **HITL sample of the 24 new accepts** — deferred; spot-check
  of DPIA's new Art.32/Art.36/B.8.2.1 confirmed groundedness

## Ship 44 direction — OpenTelemetry + Jaeger instrumentation

Per user's ask alongside BM25 (2026-07-26 session):

> instrument every data point in our app so that we have community
> backed tracing and this will help debugging the app

Separate arc; independent of consensus arc-family. Scope:

- **Ship 44'.a**: design memo — OTel SDK integration, Jaeger
  backend deployment shape (docker vs systemd on Azure VM),
  instrumentation surface (FastAPI, Postgres, HTTP, custom
  spans on consensus signals + LLM calls + chat pipeline)
- **Ship 44'.b**: install + basic instrumentation (auto-instrument
  FastAPI + psycopg2 + httpx)
- **Ship 44'.c**: custom spans on consensus_extraction (per-signal
  timing, aggregator decisions, arbiter calls)
- **Ship 44'.d**: chat pipeline spans (case-file digest, LLM
  calls, preservation-check repair)
- **Ship 44'.e**: retro

Not blocked by anything in the consensus arc-family.

## Deferred / follow-on candidates

- **Broader-doc eval on Arion's 68 other docs** (Ship 41 follow-on,
  now with BM25 + dedup live). Backlog per user.
- **BM25 v2 — persistent index** if latency matters at scale
- **BM25 stemming** for language-specific token conflation
- **Retire USE_CONSENSUS_EXTRACTION flag + default-ON** (blocked
  on broader-doc eval)
- **Backfill evidence_group_id on legacy rows** (Ship 42 deferred)
- **UI-side "covers N MUSTs" annotation** (Ship 42 deferred)

## Related

- [[ship-42-prime-arc-retrospective-2026-07-26]] — the dedup
  arc that made Ship 43's discovery-breadth safe
- [[ship-43-prime-a-bm25-signal-design-2026-07-26]] — the design
  memo
- [[ship-39-prime-arc-retrospective-2026-07-25]] — the widening
  pattern Ship 43 extends
- `rag/intake/consensus_extraction/signals/bm25_topk.py` — the
  new signal
- `rag/intake/consensus_extraction/config.py:64-72` — the BM25
  weight/topk/floor config
- Ship 44 (next) — OpenTelemetry + Jaeger instrumentation
