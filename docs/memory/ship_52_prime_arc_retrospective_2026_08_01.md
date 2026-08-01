---
name: ship-52-prime-arc-retrospective-2026-08-01
description: "Ship 52' arc retrospective (final) — DocumentCard card grid PLUS a GDPR spot-check that turned into a UX quality iteration. 11 sub-arcs in one contiguous same-day session. Card idiom formalised for a 3rd entity type. GDPR sub-paragraph refs unblocked (regex + robust SPA error handling), ref-form canonicalization retires an entire class of latent comparison bugs, Demonstrated-by panel gets a clear explainer + control titles + surgical verdict glossary. Codified 8 lessons around async safety, refless-intent enumeration, ref-form variance, path-validator audits, and one-panel-per-obligation UX discipline."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 52' arc retrospective — DocumentCard card grid + GDPR spot-check
UX quality pass. This file supersedes the interim closer written
after 52'.f — the arc kept going and this is the final record.

## What triggered it

Ship 51'.e had shipped topic-scoped filtering + compact per-doc line
rendering. The response for "what documents have we uploaded regarding
access security?" went from a 54-doc, 1500-char wall of text to 10
relevant docs on one line each. Better, but the operator asked the
next natural question:

> *"Why 15 of 54? And how can we display the full list? Can we use
> the card pattern to make it cleaner?"*

Prose was hitting its scalability ceiling at ~20 items. Ship 22'.c
had established `RiskCard` as the card pattern for short-circuit
list surfaces. Documents are the same shape of problem. This arc
extends the card idiom — and then keeps going as a GDPR spot-check
exposes ~6 latent UX issues on the drill-in surface.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 52'.a | DocumentCard schema — StandardsSummary sub-model + `documents` field on StructuredAnswer | `515d61e` (bundled) |
| 52'.b | Backend — build_document_cards() + _build_documents_data() helper + doc_inventory short-circuit wire-up | `515d61e` (bundled) |
| 52'.c | SPA — renderDocumentCards() function + CSS + Ship 22'.c-style card grid | `515d61e` (bundled) |
| 52'.d | Consensus aggregator ambiguity bypass for document_inventory (retrieval scatter isn't ambiguity for cross-cutting doc queries) | `462c9e3` |
| 52'.e | Short intro when cards render + drop drill-in link that led nowhere | `2ca654e` |
| 52'.f | Interim retro (now superseded by this file) | `aa346f2` |
| 52'.g | Ref-form canonicalization — polish + repair normalize "Art. N" → "Art.N" so machine-form and display-form converge | `adf8f3c` |
| 52'.h | GDPR sub-paragraph regex fix (`Art.5.1.f` / `Art.32.1.b`) + robust SPA error handling for FastAPI 422 detail arrays | `c64a5e0` |
| 52'.i | Demonstrated-by panel: explainer + Neo4j control titles batched onto each demonstrator row | `3747a58` |
| 52'.j | Simplified demonstrated-by explainer — "Cross-framework grounding — implemented by the operational controls below" — correct for both linkage-only and dual (own artefact + linkage) obligations | `486f920` |
| 52'.k | Surgical verdict glossary — bare pills everywhere + one-line legend at the top of the drill-in | `df2942d` |
| **52'.l** | **This retro (final)** | pending |

The first three sub-arcs (52'.a-c) shipped in one commit — a coupled
slice. Then 52'.d-e came from live operator review. The interim retro
(52'.f) declared the arc closed. Then a GDPR spot-check on Art.5.1.f
exposed a chain of latent issues (52'.g-k) that turned into a genuine
UX quality pass.

## Sub-arc details

### 52'.a — DocumentCard schema

Two new Pydantic models in `rag/casefile/answer_schema.py`:

- `StandardsSummary`: one `(standard_id, standard_display, n_refs)`
  tuple. A doc that spans 3 frameworks emits 3 of these.
- `DocumentCard`: title + external_ref + evidence_type + display +
  uploaded_at + standards[] + standards_span + total_refs + drill.
  All deterministic — no LLM emission surface.

Added `documents: list[DocumentCard]` to `StructuredAnswer`.

### 52'.b — Backend population

- `build_document_cards(documents_data)` in
  `rag/casefile/answer_augment.py` — mirrors `build_risk_cards`.
- `_build_documents_data(docs)` in `rag/arion_graph.py` — shapes
  raw uploaded-doc dicts (framework_refs composites, evidence_type,
  document_title / filename) into card-ready payloads.
- `build_short_circuit_structured()` gained a `documents_data` kwarg.

### 52'.c — SPA card grid

`renderDocumentCards` block below `renderRiskCards`. Border-left
accent `#4A90A4`, distinct from risk-card red + related-card violet.

### 52'.d — Aggregator ambiguity bypass

Symptom: "Do you mean one of: A.5.18, A.7.2, A.8.2?" clarification
fired on cross-cutting doc queries because retrieval legitimately
scattered across access-related controls.

Fix: add `document_inventory` to `_refless_intent` in
`rag/consensus/aggregator.py::_detect_ambiguity`. Sits alongside
`definition` / `gap_analysis` / `cross_framework` / `free_assessment`
— intent types where a specific ref anchor isn't required.

### 52'.e — Short intro + drop drill-in link

Two live-review issues:

- Intro was showing the full prose (intro + bullets + tail) while
  cards were rendering the same 15 docs. Fix: truncate intro to
  the header line when cards attach.
- The "Open in Documents →" drill-in routed to intake-only Documents
  tab. Fix: drop the link until a real Documents list view ships.

### 52'.g — Ref-form canonicalization

Symptom: `"Art.32.1GDPR Art. 32.1.b requires..."` — chip and prose
concatenated with no space.

Root cause: refs live in two conventions. Machine form (`Art.32.1`,
no space) meets display form (`Art. 32.1`, space after `Art.`) at
the chip-dedup check. ISO refs (`A.5.15`) have no interior spacing
so both forms coincide — the mismatch was latent until GDPR queries
surfaced. Six comparison sites potentially affected.

Fix: `canonicalize_ref_whitespace()` in `framework_refs.py` rewrites
`Art. N` → `Art.N`. Called at every polish exit
(`polish_short_circuit_answer`) and on the final repaired case-file
answer (`check_and_repair`). Machine form wins so `primary_ref` and
prose match byte-for-byte. Belt-and-braces SPA normalization on the
intro-chip dedup as defense in depth.

### 52'.h — GDPR sub-paragraph regex + robust SPA error handling

Symptom: dashboard drill-in on `Art.5.1.f` showed two different
errors depending on the branch: "No derivation tree available"
(NC/OFI branch) or "Couldn't load evidence sources: [object Object]"
(Comply/N/A branch).

Root cause 1: FastAPI path-param validator regex only accepted
`Art.32(a)` (parenthesized letter) not `Art.32.1.b` (dotted letter).
Curated GDPR data uses the dotted convention → 422 on every
sub-paragraph drill-in.

Root cause 2: FastAPI 422 returns `detail` as an ARRAY of
`{loc, msg, type, ...}` entries. The SPA's `api()` helper did
`new Error(e.detail || r.statusText)` — passing the array to Error
stringifies as `"[object Object]"`.

Fix 1: extended the regex from
`Art\.\d+(?:\.\d+)?(?:\([a-z0-9]+\))?` to
`Art\.\d+(?:\.\d+){0,2}(?:\.[a-z]|\([a-z0-9]+\))?`.
18-case unit test verified: all curated shapes accept, plaintext /
path-traversal / multi-letter suffix reject.

Fix 2: `api()` now coalesces `detail` intelligently — string as-is,
array uses first entry's `msg`, object JSON-stringifies, falls back
to `statusText`. No more `[object Object]` for any 422 anywhere.

### 52'.i — Demonstrated-by explainer + control titles

Symptom: `demonstrated_by` list showed only `A.8.24 · ISO 27001:2022
→ NC` with no titles — user had to know refs by heart.

Fix: batched Neo4j title fetch in the demonstrated-by endpoint (one
`UNWIND` query regardless of demonstrator count). Each entry gains
`src_title`. SPA renders title as a second line inside each
demonstrator row. First iteration also added a 2-sentence explainer
of what "Demonstrated by" means.

### 52'.j — Simplified explainer

The 52'.i explainer claimed "This obligation isn't assessed directly"
— correct for pure-linkage obligations like Art.5.1.f but wrong for
Art.7 (which has both own artefacts AND cross-framework grounding).

Rewrote to a single sentence that reads correctly for both cases:

> "Cross-framework grounding — implemented by the operational
> controls below."

### 52'.k — Surgical verdict glossary

Symptom: verdict expansions repeated everywhere. On Art.7's drill-in
alone, "Non-Conformity" appeared ~9 times and "Opportunity for
Improvement" ~2 times — repeated on the Finding row, Demonstrated by
rows, Evidence coverage tiles, Stage-2 proposals.

Fix: `pillWithLabel()` returns the bare pill (no more inline expansion
everywhere). New `renderFindingGlossary()` renders a one-line legend
under the Finding pill:

```
[NC] not yet met · [OFI] partially met, improvable ·
[Comply] met · [N/A] out of scope
```

Once per drill-in view. Hover tooltips on the individual pills still
carry the full term.

## Delivery velocity

- Session length: ~3-4h across a single 2026-08-01 flow
- 11 sub-arcs
- Zero mid-arc rollbacks (52'.f interim retro doesn't count — arc
  just kept going after it)
- Eval baseline held (didn't re-run — Ship 51's run stood; changes
  scoped to specific short-circuit paths + drill-in surfaces)

## Codified 8 lessons

### 1. Async event loop + shared psycopg pool is a footgun

52'.b hit `psycopg.OperationalError: sending query and params
failed: another command is already in progress` on streaming.
Passing `posture_by_node_id=posture` (a shared reference) triggered
a code path where a `psycopg2` sync connection collided with
LangGraph's async event loop.

**Rule**: when calling into shared helpers from an async graph node,
prefer to pass `None` for optional context unless you actually need
what it unlocks. The absent context is safer than accidentally
sharing a synchronous DB handle across coroutines.

### 2. Refless intents need explicit enumeration

52'.d added `document_inventory` to `_refless_intent`. Cross-cutting
doc queries WILL scatter across ref families — that's not ambiguity,
it's the metadata reality.

**Rule**: when a new intent type or query category produces
legitimately-scattered retrieval, audit the `_refless_intent` set.
The consensus aggregator can't distinguish "scattered because
ambiguous" from "scattered because cross-cutting" without an
explicit hint.

### 3. Card content beats drill-in when destination doesn't exist

52'.e dropped the "Open in Documents →" link because the SPA's
Documents tab is intake-only.

**Rule**: don't ship drill-in links that lead to placeholder
destinations. Users trust card interactions — betrayed trust is
expensive to rebuild.

### 4. User feedback during test is worth more than any design memo

52'.d and 52'.e came from ~2-minute operator reviews after commits.
52'.g through 52'.k all came from a GDPR spot-check that turned
into a 5-sub-arc quality pass. None were foreseeable from the
schema/render design alone.

**Rule**: after shipping a UX change, have someone use it for 2
minutes before considering the arc closed. When they surface a
"one more thing", follow through — the interim retro can wait.

### 5. Ref-form variance is latent until a family with actual variance surfaces

52'.g fixed a `head.includes(primary_ref)` dedup that had worked
"correctly" for every ISO ref family for months because ISO refs
carry no interior spacing. The first GDPR ref that hit the same
code path exposed the bug immediately.

**Rule**: any codebase that supports multiple ref conventions has
LATENT comparison bugs waiting for a family with actual variance.
Prefer a single canonical form (enforced at write time) over
per-site normalization on read.

### 6. Path-param validators need audit when data conventions differ from prompt guidance

52'.h fixed a FastAPI regex that accepted `Art.32(a)` but rejected
`Art.32.1.b` — because the regex was written to match the prompt's
suggested convention while the curated data used a different one.
Every GDPR sub-paragraph drill-in was returning 422 silently.

**Rule**: when adding path-param validators, verify with actual
production data shapes, not just the shapes the prompt/documentation
uses. Query the database for concrete examples before writing the
regex.

### 7. FastAPI 422 response shape needs SPA-side robustness

52'.h fixed the SPA's `api()` helper — `new Error(e.detail)` where
`e.detail` is an ARRAY produces `"[object Object]"` at every user-
facing error rendering site.

**Rule**: SPA API helpers must handle every FastAPI error shape
gracefully — string `detail`, array `detail` (validation errors),
object `detail` — and fall back to `statusText` when everything
fails.

### 8. One panel per obligation — glossary once, don't repeat verdict expansions

52'.k removed inline "[NC] Non-Conformity" repetition. Verdict
acronyms had been expanded next to every pill so tenants new to
the shorthand could learn them — but the same panel had ~11
expansions, which crossed the line from helpful to cluttered.

**Rule**: teach an acronym once per view, not every time it appears.
Contextual glossary at the top of the panel + bare pills throughout
the body reads as designed; expanding-everywhere reads as noise.

## What Ship 52 did NOT do

- **Wire metadata derivation into `rag/intake/posture_writer.py`**
  for new uploads. Still deferred from Ship 51 — Ship 53 candidate.
- **Documents tab list view** — the drill-in link comes back once
  this exists. Not scoped here.
- **Per-doc detail modal** — cards render enough info for now.
- **Extract `_TOPIC_SCOPE_RE` to a shared module** — noted in Ship
  51 retro, still open.
- **Preservation guard for card count** — not needed. Cards live in
  the structured payload; polish can't drop them.
- **Filename-to-title humanization** — cards show
  `A_5_1_management_approval.docx` verbatim when `document_title`
  is empty and no better humanization exists.
- **Retire `pillWithLabel` entirely** — kept as an alias for
  `pill(finding)` because too many call sites for a churn commit.
  Follow-up: rewrite call sites to `pill()` and delete the alias.

## Deferred / follow-on candidates

### Ship 53 candidates
- **SPA Documents tab list view** — enables re-adding the card
  drill-in
- **Per-doc detail modal** — click-to-expand for full metadata
- **Metadata derivation wire-up in posture_writer.py** — deferred
  from Ship 51 + Ship 52
- **Extract `_TOPIC_SCOPE_RE` + polarity helpers** to a shared
  module
- **CI grep guards** — regression fences for polish preservation
  guards keeping pace with new signal categories + `_refless_intent`
  staying in sync
- **Rewrite `pillWithLabel` call sites to `pill()`** — retire the
  alias entirely

### Longer-term
- **Card grid pattern for Stage-1 review** — same wall-of-text
  problem
- **Card grid pattern for cascade implications** — same shape
- **Ref-form canonicalizer for more families** — currently only
  `Art. N` variance is canonicalized; audit for other families
  (ISO 27002 body clauses, upcoming NIS2 / DORA refs) as they land

## The card-grid pattern (formalised)

Ship 52 formalises the card-grid idiom for list-shaped short-circuits
across three entity types:

- **RelatedCard** (Ship 20) — control refs
- **RiskCard** (Ship 22'.c) — risk register entries
- **DocumentCard** (Ship 52) — uploaded documents

Each follows the same 5-step scaffold:

1. Pydantic model in `rag/casefile/answer_schema.py`
2. `build_X_cards(data)` deterministic converter in
   `rag/casefile/answer_augment.py`
3. `build_short_circuit_structured` kwarg
4. `renderXCards(cards)` block in `static/arioncomply.html`
5. CSS with a distinct border-left accent

Future short-circuit list surfaces (cascade implications, Stage-1
findings, cite verifications, notification history) can follow the
same scaffold — no new architectural decisions needed.

## The verdict-glossary pattern (new)

52'.k establishes a UX rule for verdict-carrying detail panels:

- Bare pills throughout the panel body (title-tooltip carries full term)
- One-line glossary rendered ONCE at the top of the view
- Glossary shows every possible verdict with a short definition
- Same idiom is reusable for other acronym-heavy surfaces —
  cascade event types, notification kinds, workbook shapes

## Relation to the Azure dry-run

Ship 52 continues Ship 51's role as the immediate predecessor to
the Azure dry-run. Every UX iteration here (GDPR sub-paragraph
regex, ref-form canonicalization, drill-in explainer, verdict
glossary) fixes a bug the dry-run would have surfaced — and catching
them on the demo VM where the diagnostic tooling is richer saves
hours of Azure-VM investigation.

## Related

- Ship 22'.c — RiskCard, the direct precedent for DocumentCard
- Ship 51 arc — the immediate predecessor arc (topic-scope + polarity
  + backfill script + polish preservation for count parentheticals)
- Ship 19'.c — chip-dedup for the intro card (Ship 52 canonicalization
  makes it correct across ref families)
- Ship 6'.c / Ship 51'.f — preservation-check discipline in polish
- `rag/casefile/answer_schema.py::DocumentCard` — the schema
- `rag/framework_refs.py::canonicalize_ref_whitespace` — the ref-form
  canonicalizer
- `static/arioncomply.html::renderFindingGlossary` — the verdict
  glossary primitive
