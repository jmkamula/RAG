---
name: ship-52-prime-arc-retrospective-2026-08-01
description: "Ship 52' arc retrospective — DocumentCard structured payload + SPA card grid for doc-inventory chat responses. 3 delivery sub-arcs bundled in one commit + 2 live-review addenda + closer. Same-day arc, direct follow-on to Ship 51'.e/51'.f. Codified: async event loop + shared psycopg pool is a footgun; refless intents need explicit enumeration; card content beats drill-in when destination doesn't exist; user feedback during test worth more than any design memo."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 52' arc retrospective — DocumentCard card grid.

## What triggered it

Ship 51'.e had shipped topic-scoped filtering + compact per-doc line
rendering. The response for "what documents have we uploaded regarding
access security?" went from a 54-doc, 1500-char wall of text to 10
relevant docs on one line each. Better, but the operator asked the
next natural question:

> *"Why 15 of 54? And how can we display the full list? Can we use
> the card pattern to make it cleaner?"*

Prose was hitting its intrinsic scalability ceiling at ~20 items.
Ship 22'.c had already established `RiskCard` as the card pattern for
short-circuit list surfaces. Documents are the same shape of problem —
entities with rich structured metadata that benefit from card-style
tiles over prose bullets. This arc extends the card idiom.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 52'.a | DocumentCard schema — StandardsSummary sub-model + documents field on StructuredAnswer | `515d61e` (bundled) |
| 52'.b | Backend — build_document_cards() + _build_documents_data() helper + doc_inventory short-circuit wire-up | `515d61e` (bundled) |
| 52'.c | SPA — renderDocumentCards() function + CSS + Ship 22'.c-style card grid | `515d61e` (bundled) |
| 52'.d | Addendum — consensus aggregator ambiguity bypass for document_inventory | `462c9e3` |
| 52'.e | Addendum — short intro when cards render + drop drill-in link that went nowhere | `2ca654e` |
| **52'.f** | **This retro** | pending |

The three primary sub-arcs (52'.a-c) shipped in one commit because
they're a coupled slice — the schema/backend/SPA changes only work
together. The two addenda came from the operator watching the live
response afterwards.

## Sub-arc details

### 52'.a — DocumentCard schema

Two new Pydantic models in `rag/casefile/answer_schema.py`:

- `StandardsSummary`: one `(standard_id, standard_display, n_refs)`
  tuple. A doc that spans 3 frameworks emits 3 of these — cross-cutting
  nature preserved at the summary layer without needing to drill in.
- `DocumentCard`: title + external_ref + evidence_type +
  evidence_type_display + uploaded_at + standards[] + standards_span +
  total_refs + dashboard_url. All deterministic — no LLM emission
  surface. Same discipline as RiskCard (Ship 22'.c).

Added `documents: list[DocumentCard]` to `StructuredAnswer`.

### 52'.b — Backend population

Two pieces:

- `build_document_cards(documents_data)` in `rag/casefile/answer_augment.py`
  mirrors `build_risk_cards` — silent-fail per row on unexpected shape,
  no LLM.
- `_build_documents_data(docs)` in `rag/arion_graph.py` shapes raw
  uploaded-doc dicts into card-ready payloads. Composite `framework_refs`
  (e.g. `ISO27001:2022:A.5.1`) get grouped by standard prefix and
  humanized via a small `_humanize_std_id()` helper.

`build_short_circuit_structured()` gained a `documents_data` kwarg.
The doc_inventory short-circuit at `arion_graph.py:2864` now passes
docs through this route. Same topic-scope filter used for the prose
answer; cap raised to 20 for cards (they paginate) vs 10 for prose.

### 52'.c — SPA card grid

New `renderDocumentCards` block below `renderRiskCards` in
`static/arioncomply.html`. Each card:

- External-ref chip + evidence_type pill + cross-framework badge
  (when `standards_span >= 2`) + uploaded date on the head row
- Title on the main row
- Standards summary as chips: `ISO 27001 [15]  ISO 27701 [26]  GDPR [8]`

New CSS: `.sa-docs / .sa-doc-card` (border-left accent `#4A90A4`,
distinct from risk-card red and related-card violet). Follows the
same design tokens (radius, padding, palette) as other sa-card
variants.

### 52'.d — Aggregator ambiguity bypass (live-review addendum #1)

Ship 52's card pattern shipped; operator immediately retested the
query and got:

> *"Do you mean one of: A.5.18, A.7.2, A.8.2?"*

Instead of cards. The consensus aggregator's `_detect_ambiguity`
check saw retrieval scatter across multiple access-related controls
and fired a `topic_ambiguity` clarification. But the query wasn't
about a control — it was about documents. Cross-cutting doc queries
will scatter across ref families by definition.

Fix: add `document_inventory` to `_refless_intent` in
`rag/consensus/aggregator.py::_detect_ambiguity`. Sits alongside
`definition` / `gap_analysis` / `cross_framework` / `free_assessment`
— all intent types where a specific ref anchor isn't required. Did
NOT add `document_content` — asking what a SPECIFIC document should
contain legitimately benefits from ref-pinning.

### 52'.e — Short intro + drop drill-in link (live-review addendum #2)

Two more issues from the second live review:

1. The intro was showing the full prose answer (intro + bullets +
   tail) AND the card grid was showing the same 15 docs. Two passes
   of the same data.
   
   Fix: when `documents_data` is populated, walk `composed` and take
   everything BEFORE the first bullet line as `intro_text`. Cards
   carry no signal the bullets don't already carry. Intro dropped
   from ~1300 chars to 64 chars.

2. The "Open in Documents →" drill-in link on each card routed to
   the Documents tab — which is currently intake-only. No per-doc
   detail view exists. The link led to a dead-end UX.
   
   Fix: dropped the drill-in link. Cards stand on their own. Link
   comes back when a real Documents list view ships.

`answer_text` on the sync response still carries the full prose
(intro + bullets + tail) for API/curl consumers who don't render
cards. Only the structured intro card gets the shortened form.

## Delivery velocity

- Session length: ~90 min including two live-review pivots
- 5 sub-arcs across one contiguous flow (2026-08-01)
- Zero mid-arc rollbacks
- Two addenda came from ~2 min of operator review each
- Eval baseline held (didn't re-run — changes scoped to a specific
  short-circuit path already covered by Ship 51's eval run)

## Codified 4 lessons

### 1. Async event loop + shared psycopg pool is a footgun

52'.b hit `psycopg.OperationalError: sending query and params
failed: another command is already in progress` on the streaming
endpoint. The sync endpoint worked fine. Root cause: passing
`posture_by_node_id=posture` (a shared reference) into
`build_short_circuit_structured` triggered a code path where a
`psycopg2` sync connection collided with LangGraph's async event
loop.

**Rule**: when calling into shared helpers from an async graph node,
prefer to pass `None` for optional context (`posture`, `tenant`,
`pg_conn`) unless you actually need what they unlock. The absent
context is safer than accidentally sharing a synchronous DB handle
across coroutines. Ship 52'.b now explicitly passes `tenant=None`,
`posture_by_node_id=None`, `tenant_id=""` for the doc-cards path —
we don't need any of them.

### 2. Refless intents need explicit enumeration

The consensus aggregator's `_refless_intent` set had `definition`,
`gap_analysis`, `cross_framework`, `free_assessment`. Missing
`document_inventory` meant every doc query with cross-cutting refs
(most of them, on the demo tenant post-51'.d) tripped a false
ambiguity clarification.

**Rule**: when adding a new intent type OR when a category of query
starts producing genuinely-scattered retrieval signals, audit the
`_refless_intent` set. The consensus aggregator can't distinguish
"scattered because ambiguous" from "scattered because cross-cutting"
without an explicit hint.

### 3. Card content > drill-in when destination doesn't exist

52'.e removed the "Open in Documents →" link because the SPA's
Documents tab is intake-only. A link that leads to a dead-end is
worse than no link — it promises capability we don't have.

**Rule**: don't ship drill-in links that lead to placeholder
destinations. Either the destination exists (link ships) or it
doesn't (link waits). Users trust card interactions — betrayed
trust is expensive to rebuild.

### 4. User feedback during test is worth more than any design memo

Ship 52's design was locked in the AskUserQuestion at the top of
the arc — DocumentCard structured payload, SPA card grid, deferred
drill-in. That was the right foundation. But TWO addenda came from
the operator's ~2-minute live review after the initial commit:

- 52'.d: "the routing is wrong — clarification instead of cards"
- 52'.e: "intro is a repeat and the drill-in goes nowhere"

Neither was foreseeable from the schema/render design alone. Both
required watching the response in the actual chat window.

**Rule**: after shipping a UX change, have someone use it for 2
minutes before considering the arc closed. The retro can wait; the
addenda cannot.

## What Ship 52 did NOT do

- **Wire the metadata derivation into `rag/intake/posture_writer.py`**
  for new uploads. Still deferred from Ship 51 — noted in Ship 51's
  retro as a Ship 52 candidate; also still Ship 53's candidate.
- **Documents tab list view** — the drill-in link comes back once
  this exists. Not scoped here.
- **Per-doc detail modal** — the SPA card renders enough info for
  now (title, ref, evidence_type, standards summary, date).
  Detail-on-hover / click-to-expand is a future arc.
- **Extract `_TOPIC_SCOPE_RE` to a shared module** — noted in Ship
  51 retro as candidate; still open. Would let cascade / risk /
  evidence short-circuits use the same topic-scoping.
- **Preservation guard for card count** — not needed. Cards live in
  the structured payload; polish can't drop them. The prose count
  parenthetical guard from Ship 51'.f still covers the sync/fallback
  path.
- **Filename-to-title humanization** — cards show
  `A_5_1_management_approval.docx` verbatim when `document_title`
  is empty and no better humanization exists. Ship 51'.d's backfill
  populated the human title via light humanization
  (`_humanize_filename_to_title`); some template-generated docs
  still land with raw filename because their content doesn't lend
  itself to a clean title. Would need actual doc-body extraction to
  do meaningfully better.

## Deferred / follow-on candidates

### Ship 53 candidates
- **SPA Documents tab list view** — enables re-adding the card
  drill-in. Structural change: `mode-docs` mode gets a two-pane
  layout (upload UI on top, list of uploaded docs below with
  search/filter). ~4-6h.
- **Per-doc detail modal** — click a card, get a modal with full
  metadata + control_refs list + evidence status + preview link.
  Would give the "Details" link a real destination.
- **Metadata derivation wire-up in posture_writer.py** — carried
  over from Ship 51's Ship 52 candidate list. New uploads land with
  `document_title` / `standards_cited` / `topics_detected` populated
  at INSERT time; backfill script becomes historical-only. Small,
  well-scoped.
- **Extract `_TOPIC_SCOPE_RE` + polarity helpers to a shared
  module** — would let cascade / risk / evidence short-circuits use
  the same topic-scoping the doc-inventory path uses.
- **CI grep guards** — regression fences for (a) polish
  preservation guards keeping pace with new signal categories, (b)
  `_refless_intent` staying in sync with intent types that produce
  legitimately-scattered retrieval.

### Longer-term
- **Card grid pattern for Stage-1 review** — the Stage-1 queue's
  per-control pane could use the same card idiom (currently prose
  bullets like the pre-52 doc list).
- **Card grid pattern for cascade implications** — same shape as
  documents (structured entity with metadata, cross-cutting), same
  wall-of-text problem.

## The pattern this arc formalises

The card-grid idiom for list-shaped short-circuits is now established
for three entity types:

- **RelatedCard** (Ship 20) — control refs
- **RiskCard** (Ship 22'.c) — risk register entries
- **DocumentCard** (Ship 52) — uploaded documents

Each entity type gets:
1. A Pydantic model in `rag/casefile/answer_schema.py`
2. A `build_X_cards(data)` deterministic converter in
   `rag/casefile/answer_augment.py`
3. A `build_short_circuit_structured` kwarg to accept the pre-shaped
   data
4. A `renderXCards(cards)` block in `static/arioncomply.html`
5. CSS with a distinct border-left accent

Future short-circuit list surfaces (cascade implications, Stage-1
findings, cite verifications, notification history) can follow the
same shape — the pattern scales without needing new architectural
decisions.

## Related

- Ship 22'.c — RiskCard, the direct precedent for DocumentCard
- Ship 51'.d — metadata backfill that populated `topics_detected` +
  `standards_cited` (the fields DocumentCard's summary reads from)
- Ship 51'.e — topic-scope filter + compact prose rendering (the
  starting point Ship 52 replaced with cards)
- Ship 51'.f — polish preservation guard for count parentheticals
  (still guards the prose fallback path)
- `rag/casefile/answer_schema.py::DocumentCard` — the schema
- `static/arioncomply.html` — the renderDocumentCards block
