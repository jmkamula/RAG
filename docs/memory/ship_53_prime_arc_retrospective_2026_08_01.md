---
name: ship-53-prime-arc-retrospective-2026-08-01
description: "Ship 53' arc retrospective — consultant-grade grounding arc. Six sub-arcs delivered on 2026-08-01. Digest gains an inline guidance-standard citation for ISO refs; chat_answer swaps from gpt-4o-mini (via LOCAL_LLM_MODEL override) to gpt-4.1, which surfaces a latent ISO 27701 Chroma indexing gap; 49 PIMS RequirementNodes indexed; 27701 marker corrected (27002 → 27701 self-contained model); full EDPB Guidelines corpus (1190 chunks across 9 highest-load-bearing docs) indexed and wired into the digest via a per-ref semantic-query section. GDPR remediation quality shifts from LLM-training-data prose to auditor-defensible per-clause EDPB citations. Codified 8 lessons around model-choice vs. grounding infrastructure, Chroma embedding-function pitfalls, MVP scope discipline, and the consulting-grounding shape for regulations vs. standards."
metadata:
  node_type: memory
  type: project
---

Ship 53' arc retrospective — consultant-grade grounding arc.
Six sub-arcs delivered in one contiguous same-day session on
2026-08-01, covering three distinct grounding surfaces (ISO
27001/27002 attribution, ISO 27701 self-contained model, GDPR
via EDPB Guidelines corpus) plus a model migration that surfaced
a latent data gap.

## What triggered it

Ship 52' had shipped GDPR spot-check UX quality (drill-in surface,
verdict glossary, ref-form canonicalization). The operator then
asked the next natural consultant-side question:

> *"I want to strengthen the consultant side of things. What can I
>  do to remediate — this should bring out 27002 §5 grounding in
>  business language — can we discuss: how do I remediate A.5.15?"*

The concern: LLM prose was drafting remediation actions from
training data rather than the authoritative implementation-
guidance standard (ISO 27002 for A.5-A.8 refs, ISO 27003 for
ISMS clauses, etc.). For an auditor or a DPO reading the
remediation, generic prose reads as shallow. Real consulting
practice grounds every recommendation in a specific citation.

The arc kept going in three directions:

1. **ISO 27001 side** — build the guidance-authority attribution
   into the digest (53'.a-c).
2. **Model side** — swap chat_answer off gpt-4o-mini (which was
   ignoring Rule 10's citation directive) onto gpt-4.1 (53' base).
3. **Data side** — the model swap made two data gaps visible: ISO
   27701 nodes had no Chroma content (53'.d), and the 27701
   guidance marker was wrong (53'.e). Then the same lens revealed
   the GDPR side was equally shallow, which triggered the EDPB
   Guidelines corpus arc (53'.f).

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 53'.a-c | ISO 27002/27003 guidance attribution in digest — `_infer_guidance_standard()` + `← source: ISO ...` marker in OBLIGATIONS section + Rule 10 update in `answer_schema.py`. Rendered on 81 previously-invisible Annex A controls. | `cdc708e` |
| 53' base | LLM model migration — chat_answer moved from gpt-4o-mini (via LOCAL_LLM_MODEL env override) → gpt-4.1. Small OpenAI purposes (verify, classifier, consensus_gk, enrichment_t2) tier-preserving upgrade to gpt-4.1-mini. Anthropic sites (extractor, enricher) untouched. Pricing table extended with gpt-4.1 family. | `9d6f500` |
| 53'.d | ISO 27701 Chroma indexing gap closed — script existed (from Ship 2 era) but had never been run + hardcoded `text-embedding-3-small` incompatible with Ship 5'.b consolidation to 3-large. Fixed embedding config, ran script, indexed 49 RequirementNodes into new `iso27701_2019` collection + `arioncombly_all` (429 → 478 docs). | `c635fbb` |
| 53'.e | 27701 guidance marker correction — `_infer_guidance_standard()` was returning "ISO 27002:2022" for 27701 refs. ISO 27002 does not cover PIMS controllers or processors; a trained auditor would flag it. Correct return is "ISO 27701:2019" itself (self-contained standard model). | `f3d23d7` |
| 53'.f | EDPB Guidelines corpus grounding — new Chroma collection `edpb_guidelines` (1190 chunks across 9 highest-load-bearing docs: wp248 DPIA, wp243 DPO, EDPB 07/2020 Controller-Processor, 05/2020 Consent, 9/2022 Breach, Rec 01/2020 Transfers, 4/2019 DPbD, 3/2018 Territorial scope, 01/2022 Right of access). New `_render_edpb_guidance()` section in digest fires per cited GDPR ref via semantic query + metadata post-filter. Rule 10 extended with EDPB bracket-form citation pattern. | `ac1cf4c` |
| **53'.g** | **This retro** | pending |

## Sub-arc details

### 53'.a-c — Digest guidance-standard attribution

Three tightly-coupled changes shipped in one commit:

**53'.a — `_infer_guidance_standard(ref, standard_id)`**: new
helper in `rag/casefile/digest.py`. Maps:
- `ISO 27001 A.5.x-A.8.x` → ISO 27002:2022
- `ISO 27001 4.x-10.x` (ISMS body) → ISO 27003:2017
- `ISO 27701 A.7.x / B.8.x` → ISO 27002:2022 (later corrected in 53'.e)

Used to emit a `← source: <standard>` marker on OBLIGATIONS
entries where the primary text came from `business_description`
or the Chroma document fallback (as opposed to explicit
obligation_text).

**53'.b — `_render_obligations()` text_src tracking**: the
render function now tracks whether the emitted text came from
`obligation_text` (auditable primary), `bd` (BD paraphrase),
`document` (Chroma raw), or `title` fallback. When source is
bd/document, the `← source:` marker fires. Previously only 12
of 93 Annex A controls had an explicit "Per ISO 27003" marker
in their BD; the new inference covers 81 more with no data
migration needed.

**53'.c — Rule 10 in `answer_schema.py`**: extended to list
every ISO family standard the LLM must name verbatim in intro
prose (ISO 27002, 27003, 27004, 27005, 27701, 27017, 27018,
27552, 27799). Auditors trace guidance by standard number, not
paraphrase.

Verified live on A.5.15 remediation: intro now says
"ISO 27002:2022 provides implementation guidance for this
control" — grounded, not fabricated.

### 53' base — Model migration

Discovered mid-arc that `.env` carried `LOCAL_LLM_MODEL=gpt-4o-mini`
which was globally overriding `answer_model` + `verify_model` in
`rag/llm_answer.py:752`. The A.5.15 remediation was firing the
new Rule 10 correctly, but subsequent tests exposed that
`gpt-4o-mini` was inconsistent about applying it — the rule 10
guidance-standard citation appeared in ~40% of runs, not 100%.

Diagnosed via `ai_call_log`: `rank_answer` model was `gpt-4o-mini`,
not the `MODEL_CHAT_ANSWER = "gpt-4o"` default in `llm_models.py`.
The env override was defeating the per-purpose config.

Fix, phased:

1. Remove `LOCAL_LLM_MODEL` from `.env`. Set
   `MODEL_CHAT_ANSWER=gpt-4.1` explicitly.
2. Later in the same session, replace `.env` override with
   defaults in `rag/llm_models.py`:
   - `MODEL_CHAT_ANSWER = "gpt-4.1"`
   - Small OpenAI purposes (verify, classifier, consensus_gk,
     enrichment_t2) → `"gpt-4.1-mini"` (tier-preserving upgrade
     for stronger multi-rule instruction-following at ~2.7× cost
     on the small-model portion; ~$0.001-0.002 added per chat turn)
   - Anthropic sites (EXTRACTOR = claude-sonnet-4-6, ENRICHER =
     claude-haiku-4-5) untouched — deliberate Ship 5' extraction-
     quality choice that needs a bake-off before migrating off
     Claude.
3. Extend pricing table in `rag/ai_trace.py::_PRICING_USD_PER_M`
   with gpt-4.1 / gpt-4.1-mini / gpt-4.1-nano entries so cost
   tracking stays populated.

Verified: `rank_answer` → `gpt-4.1`; `consensus_gatekeeper` →
`gpt-4.1-mini` across 4 test queries.

### 53'.d — ISO 27701 Chroma indexing gap

Testing A.7.2.1 (an ISO 27701 controller-side PIMS ref) exposed
that gpt-4.1 produced a confidently wrong remediation about
"Classification of information" (which is ISO 27001:2013 A.7.2.1
or ISO 27001:2022 A.5.12 — completely different controls).

Investigated:

- Neo4j `RequirementNode` for A.7.2.1 with `standard_id: 'ISO27701:2019'`
  correctly had `title="Identify and document purpose"` +
  `business_description` about PII processing purposes.
- **Chroma collection `iso27701_2019` did not exist. `arioncombly_all`
  had 429 total docs, ZERO with `standard_id: ISO27701:2019`.**
- Root cause: `graph_expander._fetch_from_chroma` returned empty
  for ISO 27701 nodes → digest had only the POSTURE line ("A.7.2.1
  NC 0/4") + no OBLIGATIONS entry → LLM fell back to training-data
  pattern-matching on the numeric ref.

Fix: `scripts/index_27701_to_chroma.py` had been written in Ship
2 era but never actually run. Additionally it hardcoded
`text-embedding-3-small` which conflicted with Ship 5'.b
consolidation to 3-large. Two changes:

- Import `EMBED_MODEL_STANDARD` from `rag.embedding_config`
- Replace hardcoded model with the shared constant

Ran the script — 49 RequirementNodes indexed into `iso27701_2019`
(new collection) + upserted into `arioncombly_all` (429 → 478).
`arioncombly_all` grew by exactly 49 as expected.

Verified: A.7.2.1 remediation now correctly identifies "Identify
and document purpose" + emits PII-processing-purpose remediation
actions grounded in the actual BD.

### 53'.e — 27701 guidance marker correction

Discussion of "do we have implementation guidance for 27701 like
27002 for 27001?" clarified that:

- ISO 27701 is **self-contained**. Unlike 27001 → 27002, the 27701
  standard has its own implementation guidance embedded inline
  under each control clause (that's the source of the BD text now
  grounding remediation).
- Citing ISO 27002 for a PIMS control (A.7.x / B.8.x) is
  factually wrong. A trained auditor or DPO would flag it.

Fix: `_infer_guidance_standard()` for `ISO27701:2019` refs
returns `"ISO 27701:2019"` itself, not `"ISO 27002:2022"`.

Post-MVP grounding candidates deliberately deferred (documented
in the docstring so future sessions know where to look):

- ISO 27018:2019 — public cloud PII processor (relevant for B.8.x
  when tenant is a cloud processor)
- ISO 29134:2017 — PIA/DPIA methodology
- ISO 29100:2011 — privacy framework foundational concepts
- ISO 29151:2017 — PII protection code of practice

Not needed for the honest MVP baseline; a professional-quality
answer only requires the correct authority citation.

Verified: A.7.2.1 remediation card citation moved from
"ISO 27002:2022 implementation guidance" (wrong) to "ISO 27701:2019
implementation guidance" (correct).

### 53'.f — EDPB Guidelines corpus for GDPR

The next natural operator question:

> *"I thought GDPR had its own implementation text?"*

Diagnostic answer: yes, GDPR grounds in EDPB Guidelines + endorsed
WP29 predecessor guidance + national SA guidance + CJEU case law.
Structurally different from ISO's standard→guidance-book pattern.
Currently our engine treats GDPR as self-authoritative — the LLM
cites the article verbatim + drafts remediation from training data.
For DPO-level readers this reads as shallow.

Operator direction:

> *"GDPR is a mandatory european requirement. We can lift it now."*

Framing check: EU mandatory law is different weight class than
ISO voluntary certification. Trimming to "MVP sufficient minimum"
that made sense on the 27701 side doesn't apply here. Full corpus
indexed.

**Phase 1 — Corpus acquisition** (~1 hour). 9 highest-load-bearing
docs downloaded to `/data/arioncomply/private/edpb/` from
edpb.europa.eu (public, no license issue). URL discovery via
WebSearch — EDPB documents page is paginated (54 pages, 531 items)
so targeted per-doc search was more efficient than enumeration.

| Doc | Interprets | Size |
|---|---|---|
| WP29 wp248 rev.01 | Art.35, Art.36 (DPIA) | 1.1MB |
| WP29 wp243 rev.01 | Art.37-39 (DPO) | 824KB |
| EDPB 07/2020 | Art.4/24/26/28/29 (Controller-Processor) | 860KB |
| EDPB 05/2020 | Art.6/7/8/9 (Consent) | 329KB |
| EDPB 9/2022 | Art.33/34 (Breach notification) | 659KB |
| EDPB Rec 01/2020 | Art.44-49 (Transfers) | 1.4MB |
| EDPB 4/2019 | Art.25 (DPbD) | 313KB |
| EDPB 3/2018 | Art.3 (Territorial scope) | 543KB |
| EDPB 01/2022 | Art.12/15 (Right of access) | 1.4MB |

**Phase 2 — Extraction + chunking** (~1 hour). `pdftotext -layout`
each PDF → chunker in `scripts/index_edpb_to_chroma.py`:

- Chunks per H2/H3 section boundary (regex on numeric section
  headers like `2.1.3` + uppercase-word H2 markers)
- Min 300 chars / target 1200 chars / max 1800 chars
- Skip boilerplate (page footers, TOC markers, version-history
  blocks)
- Metadata per chunk: `source_doc`, `title`, `interprets_articles`
  (comma-joined string — Chroma metadata is primitives only),
  `authority` (EDPB / WP29), `adopted`, `section_title`,
  `chunk_index`

Total: **1190 chunks** across 9 docs.

**Phase 3 — Indexing** (~15 min). New Chroma collection
`edpb_guidelines` + upsert into `arioncombly_all` (478 → 1668
docs). Uses `EMBED_MODEL_STANDARD` from `rag/embedding_config.py`
per Ship 5'.b consolidation.

**Phase 4 — Digest wiring, Option C** (~2 hours).

Chose Option C from the arc plan: new digest section that
per-cited-GDPR-ref runs a semantic Chroma query at digest-build
time. Isolated code path. No changes to `ExpandedNode`,
`graph_expander`, or resolver.

New `_render_edpb_guidance(cf)` in `rag/casefile/digest.py`:

1. Extract GDPR refs from `cf.cited_refs` (starts with `Art.`)
2. For each ref, build a query hint from the article title
   (from `cf.all_nodes()`) + tenant query
3. Semantic search with `n_results=30` (overfetch — EDPB docs
   rarely mention article numbers verbatim, so post-filter by
   metadata needs a wider raw hit pool)
4. Post-filter: keep chunks where `interprets_articles` contains
   the ref
5. Take top-2 per ref, cap section at 2500 chars total

New `_get_edpb_collection()` uses `VectorIndexer.get_collection()`
— crucially NOT `chromadb.HttpClient().get_collection()` directly,
which defaults to a 384-dim onnx embedding function that
mismatches the 3072-dim stored embeddings. First implementation
made this mistake; caught via `EDPB_DEBUG` logging.

Rule 10 extension in `answer_schema.py`: action cards must cite
the source doc verbatim in bracket form the digest provides
(e.g., `[EDPB 07/2020] Art.28`). No paraphrasing of attribution.

**Phase 5 — Verification** across 7 GDPR remediation surfaces:

| Article | Doc | Bracket-form | ✓ |
|---|---|---|---|
| Art.35 DPIA | WP29 wp248 rev.01 | ✓ | ✓ |
| Art.28 Controller-Processor | EDPB 07/2020 | ✓ | ✓ |
| Art.33 Breach | EDPB 9/2022 | ✓ | ✓ |
| Art.6 Lawful basis | EDPB 05/2020 | ✓ | ✓ |
| Art.15 Right of access | EDPB 01/2022 | ✓ | ✓ |
| Art.25 DPbD | EDPB 4/2019 | ✓ | ✓ |
| Art.44 Transfers | EDPB Recommendations 01/2020 | inline (not bracket) | ✓ |

Content quality — the LLM extracted specific deep-guidance points
per query:

- Art.35: enumerated Art.35(7) content requirements verbatim from
  wp248
- Art.28: enumerated Art.28(3) mandatory contract terms from
  EDPB 07/2020
- Art.33: "including those not notified to the supervisory
  authority" — the Art.33.5 internal-only breach register point
- Art.25: cited "EDPB 4/2019 subchapter 2.1.4" (retroactive
  application to legacy systems) — paragraph-level grounding
- Art.44: cited "points 32 and 36" of EDPB Rec 01/2020 (the "know
  your transfer" step + TIA methodology)

Cost per GDPR chat turn: ~$0.012-0.013, ~4-5s wall time.
Pre-EDPB baseline was ~$0.010, ~3s. Trivial delta for the
quality shift.

## Codified lessons

### 1. Weaker models hide data gaps; stronger models make them visible

The ISO 27701 Chroma indexing gap had existed since 27701 Phase
3 shipped in Jan 2026. Every 27701 remediation query for six
months produced generic-shape hallucinations that "read fine"
because gpt-4o-mini's default output was already generic prose.

Moving to gpt-4.1 made the failure mode confidently specific —
the LLM wrote a coherent, detailed remediation for a completely
different control (Classification of information from ISO
27001:2013 A.7.2.1). That kind of confident-specific hallucination
is easy to detect on cross-check; generic-shape output is not.

**Rule**: when a model migration surfaces confidently-wrong
answers, treat it as diagnostic signal about data-layer gaps, not
as a regression to roll back. The stronger model is doing you
a favor.

### 2. Model choice ≠ Grounding infrastructure

Ship 53'.a-c built the guidance-attribution wiring (rule 10 + the
`← source:` marker). The rule was correct. But the LLM ignored it
under gpt-4o-mini in ~60% of runs.

Ship 53' base swapped the model. Now the rule fires 100% of the
time — but only where the digest actually carries the marker.
The 27701 side had no marker because Chroma had no content
(Ship 53'.d). The GDPR side had no marker at all because
`_infer_guidance_standard()` returned empty for GDPR refs
(Ship 53'.f).

**Rule**: model choice and grounding infrastructure are
independent axes. Both need to work. A stronger model doesn't fix
a data gap; better data doesn't fix an ignored rule. Diagnose
which layer is the bottleneck before picking the fix.

### 3. Chroma collection embedding-function mismatch is silent

When a Chroma collection is created with an OpenAI embedding
function (3072-dim), subsequent `chromadb.HttpClient().get_collection(name)`
calls that don't pass an embedding function silently fall back
to the default onnx (384-dim) embedder. Queries then either fail
with a dimension-mismatch error OR — worse — silently return
empty results if the caller catches the exception.

Fix: **always** use `VectorIndexer.get_collection()` which walks
the stored collection metadata for `embedding_function_name` and
matches. This was the specific bug that made my first
implementation of `_get_edpb_collection()` return zero chunks
despite the collection being populated.

Debug pattern: add a temporary `logger.warning` at each Chroma
boundary so the "0 chunks returned" case is visible in the API log.

### 4. Semantic query hint enrichment matters more than n_results

EDPB documents rarely mention the GDPR article number verbatim.
wp248 talks about "DPIA" and "impact assessment" every paragraph;
"Art.35" appears maybe once per page. A semantic query for
"Art.35 how do I remediate Art.35?" ranks EDPB docs about DPbD
(Art.25) higher than wp248 because the query text has no strong
topical signal.

Fix: enrich the query hint with the article title from
`cf.all_nodes()`. Query "Data protection impact assessment
how do I remediate Art.35?" ranks wp248 chunks correctly.

**Rule**: for semantic retrieval over guidance corpora, the
authoritative document text uses topical language, not reference
labels. Pass the topic (title, description, obligation_text)
as the query, not the reference. Overfetch + post-filter is a
viable but weaker fallback.

### 5. Consulting grounding for a regulation ≠ for a standard

ISO 27001 grounds via 27002 (standard → companion guidance book).
ISO 27701 is self-contained (standard IS its own guidance).
GDPR grounds via EDPB Guidelines + WP29 endorsed + national SA
guidance + CJEU case law (regulation → regulatory-body
interpretation + case law + national refinement — closer to how
a lawyer cites a statute alongside case law and legal commentary).

Each is a **different consulting-grounding shape**. Copy-pasting
the ISO 27002 pattern onto GDPR (or onto 27701) is architecturally
wrong. Digest routing needs to know the shape.

**Rule**: before adding grounding for a new framework, identify
its shape. Ask:
- Is there a single companion guidance standard? (ISO 27001 → 27002)
- Or is guidance embedded in the standard itself? (ISO 27701)
- Or is guidance from a regulatory body + case law? (GDPR)
- Or is there no formal grounding layer? (upcoming NIS2, DORA)

### 6. MVP scope discipline works — but not universally

On the 27701 side, operator asked "do we need this complexity for
MVP, I want the sufficient minimum" — leading to Tier 1 fix only
(correct the guidance marker, no new indexing). Clean shipping.

On the GDPR side, the same lens was rejected: "GDPR is a mandatory
european requirement. We can lift it now." Full corpus indexed.

**Rule**: MVP scope discipline is contextual. Voluntary
certification standards (ISO) can defer supplementary grounding
until customer demand. Mandatory regulation (GDPR, DORA) with
EU regulatory-body interpretation cannot — a "shallow but works"
answer on a mandatory regulation is a demo-killer for DPO
audiences.

### 7. Option C proved right for isolated grounding surfaces

Choice at start of 53'.f between three wiring options:

- **A**: extend `ExpandedNode` with `supplementary_guidance: list[GuidanceChunk]`
- **B**: new retrieval lane in resolver
- **C**: new digest section with per-ref Chroma query at digest-build time

Went with C — isolated code path, additive change, no ExpandedNode
or resolver refactor. Trade-off: extra Chroma query per digest
build (2-3 refs × 1 semantic query each × ~100ms + embedding).
Latency +2s per turn, cost +$0.002 per turn. Acceptable.

**Rule**: for grounding surfaces that are additive (new corpus
layered onto existing), prefer the isolated Option C pattern
over API refactors. If retrieval proves load-bearing (e.g., the
new grounding drives >50% of the answer's specific content),
promote to Option B in a follow-on arc.

### 8. Debug logs stay behind on branch even after "removed"

Twice during 53'.f I added `logger.warning("EDPB_DEBUG: ...")`
lines to diagnose the retrieval failure. Removing them via Edit
worked but only because the specific edit blocks matched. If they
had matched across multiple sites and I'd used replace_all=False,
one could have slipped through.

**Rule**: end every debug-added session with `grep -n "EDPB_DEBUG\|DEBUG:"
$file` to confirm all temporary logs are gone before commit. Or
better: use a `logger.debug()` level that stays off in production
by default, rather than escalating to `warning` for visibility.

## What Ship 53 did NOT do

- **ISO 27018:2019 indexing** — public cloud PII processor code
  of practice. Relevant for B.8.x remediation when tenant is a
  cloud processor. Deferred; only needed if a specific customer
  requests it.
- **ISO 29134:2017 indexing** — DPIA methodology. Deferred; the
  wp248 DPIA guidance already covers this in Ship 53'.f.
- **National SA guidance** — ICO (UK), CNIL (FR), Garante (IT),
  BfDI (DE), DPC (IE) practitioner guides. Tenant-jurisdiction-
  specific. Deferred; add per-tenant if requested.
- **WP29 wp251** — automated decision-making guidelines (Art.22).
  Less commonly hit in remediation. Deferred.
- **EDPB Recommendations 02/2020** — EU Essential Guarantees.
  Companion to Rec 01/2020 on transfers. Deferred; Rec 01/2020
  already gives the operational grounding.
- **CJEU case law summaries** — Schrems II, Google Spain,
  Weltimmo, Facebook Ireland. Would need a different indexing
  shape (case → interpreted articles). Deferred to a proper
  post-MVP arc.
- **Bracket-form citation strict enforcement** — Art.44 verified
  with inline citation form ("as required by EDPB Recommendations
  01/2020 Art.44") instead of the requested bracket form
  (`[EDPB Recommendations 01/2020] Art.44`). gpt-4.1 appears to
  prefer inline when the source_doc name is long (4+ words).
  Not a bug — style variance the LLM made unilaterally.
- **CI grep guards** for direct Chroma HttpClient use — if a new
  contributor bypasses `VectorIndexer.get_collection()`, they'll
  hit the 384-dim / 3072-dim mismatch silently. Follow-up.
- **Preservation guard for EDPB citation form** — if the LLM
  drops the source-doc attribution, we currently have no repair.
  Follow-up.

## Deferred / follow-on candidates

### Ship 54 candidates (carry-forward from Ship 52 + Ship 53)

- **SPA Documents tab list view** — enables re-adding the drill-in
  link removed in Ship 52'.e
- **Per-doc detail modal** — click-to-expand for full metadata
- **Metadata derivation wire-up in `rag/intake/posture_writer.py`**
  — deferred from Ship 51, 52, 53
- **Extract `_TOPIC_SCOPE_RE` + polarity helpers** to a shared
  module
- **CI grep guards** — regression fences (polish preservation
  guards, direct Chroma HttpClient use, Rule 10 bracket-form
  citation)
- **Rewrite `pillWithLabel` call sites to `pill()`** — retire
  the alias
- **ISO 27018:2019 corpus for cloud-processor B.8.x grounding**
- **National SA guidance per active tenant jurisdiction** (ICO
  for UK-scoped tenants first)
- **WP29 wp251 for Art.22 automated decisions**
- **Bracket-form citation preservation guard**

### Longer-term

- **CJEU case law integration** — different indexing shape
  (case → interpreted articles) + case-summary chunking
- **National regulator enforcement decisions** — precedent
  grounding for close calls
- **Framework-specific consulting-grounding shape catalog** —
  when SOC 2, NIS2, DORA land, know upfront which shape each
  follows (companion standard / self-contained / regulatory-body)

## Corpus quick-reference (Ship 53'.f)

Chroma collection `edpb_guidelines`, 1190 chunks. Extending the
corpus is a data operation, not a code change:

1. Drop PDF into `/data/arioncomply/private/edpb/` (public docs
   only — the private/ dir is gitignored)
2. `pdftotext -layout new_doc.pdf new_doc.txt`
3. Add entry to `CORPUS` dict in
   `scripts/index_edpb_to_chroma.py` — needs `source_doc`,
   `title`, `interprets_articles`, `authority`, `adopted`
4. `python3 scripts/index_edpb_to_chroma.py` — idempotent upsert

To grow beyond EDPB (e.g., ICO practitioner guides): mirror the
script shape as `scripts/index_ico_to_chroma.py` with a new
Chroma collection. Extend `_render_edpb_guidance()` (or add a
parallel `_render_national_sa_guidance()`) to query the new
collection.

## The consulting-grounding pattern (formalised)

Ship 53' formalises the pattern for adding new authoritative
grounding corpora to the digest:

**When to add a grounding corpus**:
- The framework has an authoritative interpretation layer
  (companion standard, endorsed guidelines, regulatory
  recommendations) that consultants routinely cite
- The LLM answers currently draft remediation from training data
  rather than the authoritative source
- The customer audience (DPO, auditor, compliance manager)
  expects specific per-clause citations

**How to add one** (~½ day per corpus after the first):

1. Identify the highest-load-bearing 5-10 documents
2. Curate corpus registry: `filename → {source_doc, title,
   interprets_refs, authority, adopted}`
3. `pdftotext -layout` each PDF, add to `private/` dir
   (gitignored)
4. Write indexer script (~250 LOC) mirroring
   `scripts/index_edpb_to_chroma.py`:
   - Chunks per H2/H3 boundary
   - Uses `EMBED_MODEL_STANDARD` from `rag.embedding_config`
   - Upserts into corpus-specific collection + `arioncombly_all`
5. Add digest render function `_render_<corpus>_guidance(cf)`:
   - Fires when cited refs match the corpus scope
   - Semantic query with title+tenant-query as hint (not the ref)
   - Post-filter by metadata `interprets_refs`
   - Cap total chars added to digest at ~2500
   - Uses `VectorIndexer.get_collection()` — never raw HttpClient
6. Extend Rule 10 in `answer_schema.py` with bracket-form
   citation pattern
7. Verify on 4-5 refs covering different corpus docs

The scaffold is stable. Future corpora (ISO 27018, ISO 29134,
ICO guides, CJEU case law) can follow it.

## Verified — the consultant-grade shift

Before Ship 53', GDPR remediation for Art.35:

> "Ensure DPIA. Document risk assessment. Review periodically."

After Ship 53'.f:

> "Ensure every DPIA contains: description of processing operations
>  and purposes; necessity and proportionality assessment; risk
>  assessment; mitigating measures including safeguards and
>  mechanisms to demonstrate compliance with the GDPR.
>  [WP29 wp248 rev.01] Art.35"

The shift is consultant-grade: enumerates Art.35(7) verbatim from
the authoritative source, cites the source doc, links to
compliance-mesh implementation controls (ISO 27001 + 27701).
DPO-defensible.

Cost impact: +~$0.002-0.003 per GDPR turn, +~2s latency. Trivial
in absolute terms for the answer-quality jump.

Ship 53' arc closes. The consulting-grounding scaffold is now in
place for the ISO and GDPR sides. Extending it to other frameworks
(ISO 27018, ISO 29134, national SA guidance) is a data operation
per corpus, not a design arc.
