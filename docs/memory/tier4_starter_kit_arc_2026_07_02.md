---
name: tier4-starter-kit-arc-2026-07-02
description: "SHIPPED 2026-07-02 → 2026-07-03 (2 commits: 649a4ce Tier-4 chat block + 8334690 Get Started mode): structured 'starter kit' for compliance work. Two coordinated surfaces: (1) chat answers now emit a STRUCTURED templates_block payload — per-cited-NC/OFI-control card with primary download in the right format (docx narrative / xlsx tabular via _is_tabular check), progress line 'N of M elements to fill in', cite-mode secondary CTA for cite-acceptable leaves, dashboard drill-in link. Plain-text '↳ Templates available:' footer retired. (2) New Get Started sidebar mode for fresh tenants — full 20-anchor foundation sequence with per-anchor completion state icon (○/◐/✓), phase-progress strip, next-recommended-action card from journey.next_actions[0], cite-mode nudge footer. Design conversation locked TWO tenants get different UX: contextual per-finding for existing journey, browsable foundation for fresh. Chat's starter_nudge field points fresh tenants at Get Started mode. Backend serialises JourneyState.foundation_anchors via asdict() through the unchanged /api/v1/journey/state endpoint. Streaming API emits new 'templates' SSE event before 'done'. LLM prompt updated to know structured block renders below — no more 'To achieve compliance, focus on...' hollow closers."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What this is

Two-surface starter-kit arc landed on top of the 2026-07-01
de-jargonize pass. The de-jargonize pass made every tenant-facing
string natural; this arc adds a STRUCTURED action surface where
before there was a plain-text footer of URLs.

## Design conversation carry-forward

Two tenant modes needed different treatment:
- **Existing-journey tenant** asking about an NC/OFI — wants
  the concrete next step for THIS specific finding, right in
  chat. Progress-aware ("5 of 7 elements to fill"), right
  format, cite-mode alternative visible, respects evidence
  sovereignty ("if you already have this in another system,
  cite it instead").
- **Fresh tenant** — wants a browsable overview of the whole
  path before starting. Doesn't need per-finding progress
  because they have no findings yet.

Two surfaces, one shared data spine (`rag/journey/state.py`
+ catalog).

## Surfaces

### Chat: contextual templates block (commit 649a4ce)

`rag/templates/answer_footer.py:build_templates_block(cited_refs,
question_type, tenant_id, pg_conn)` returns:

```python
{
  "mode": "contextual" | "nudge_only" | None,
  "leaves": [ ... per-NC/OFI-ref cards ... ],
  "starter_nudge": {"message": "...", "url": "/#getstarted"} | None
}
```

Per-leaf card shape:
```python
{
  "control_ref":       "A.5.19",
  "leaf_id":           "req:A.5.19:supplier_risk_procedure",
  "title":             "Supplier Risk Procedure",
  "finding":           "OFI",
  "evidence_type":     "procedure",
  "progress":          {"bound": 8, "total": 8, "remaining": 0},
  "primary_download":  {"format": "docx", "label": "Word starter", "url": "..."},
  "alt_downloads":     [{"format": "md", ...}],
  "cite_acceptable":   false,
  "dashboard_url":     "/#dashboard?control=A.5.19"
}
```

**Cited refs filtered to NC/OFI only** — no template offers for
Comply/N/A (would suggest downloading something already covered).
**Format selection**: `_is_tabular(evidence_type)` decides docx
(narrative: policy/procedure/plan/scope_note/…) vs xlsx (tabular:
register/record/matrix/log/inventory).

`ComplianceAnswer.templates_block` field carries payload through
the graph state. Sync `ChatResponse.templates: Optional[dict]`;
streaming emits `{"type": "templates", "block": {...}}` SSE event
after tokens, before `done`.

Frontend `renderTemplatesBlock()` renders card block below the
assistant bubble. Streaming client captures SSE event and passes
to `appendMsg`.

LLM prompt (RANK_AND_ANSWER_SYSTEM in `rag/llm_answer.py`) updated
with rule: structured block renders below, no need to list
templates in prose or write "To achieve compliance, focus on…"
closers. Optional single-sentence bridge OK.

**Retired**: plain-text `↳ Templates available:` footer appended
to `answer_text`. `build_template_footer` still present in the
module for any external consumer but arion_graph doesn't call it.

### Get Started sidebar mode (commit 8334690)

New sidebar item (rocket icon) as the FIRST workspace nav item —
above Dashboard. Data source: existing
`GET /api/v1/journey/state`, extended with new
`JourneyState.foundation_anchors: list[dict]` field.

Each anchor dict:
```python
{
  "sequence":         1..20,
  "control_ref":      "4.3",
  "leaf_id":          "req:4.3:isms_scope",
  "title":            "ISMS Scope Statement",
  "evidence_type":    "scope_note",
  "is_tabular":       False,
  "must_total":       N,
  "must_satisfied":   K,
  "completion_pct":   0..100,
  "primary_download": {...},
  "alt_downloads":    [{md}],
  "dashboard_url":    "..."
}
```

Populated by iterating `_ANCHOR_LEAVES` (documented sequence:
4.3 → 5.2 → 5.3 → 6.1.2 → 6.1.3 RTP → 6.1.3 SoA → 7.5 → 9.2 →
9.3 → 10.1 → A.5.1 → A.5.9 → A.5.15 → A.5.18 → A.5.19 → A.5.24
→ A.5.29 → A.6.3 → Art.30 → Art.32).

`renderGetStarted()` lays out:
1. **Phase progress strip** — 4-tile (Profile / Foundation /
   Operational / Annual), current highlighted.
2. **Phase message card** — phase_name + phase_message from
   journey computer.
3. **Next recommended action card** — `next_actions[0]` with big
   download button + dashboard drill-in.
4. **Foundation templates list** — all 20 anchors in sequence,
   state icon + step number + ref + title + progress line +
   right-format primary + `.md` alt + drill-in arrow.
5. **Cite-mode nudge footer** — italic reminder.

## Vocabulary decisions (locked)

- "starter kit" (not "template pack" / "starter templates" /
  "compliance kit") — matches how tenants think about getting
  started.
- "Foundation templates" (not "Anchor templates" / "Phase 1
  templates") in the tenant-visible list heading.
- Phase names: Profile / Foundation / Operational / Annual
  (already in `_determine_phase`, kept as-is).
- Progress phrasing: "N of M elements covered" (not "N/M MUSTs"
  or "N of M checklist items") — matches the dashboard
  evidence-class panel wording.
- "Cite it" for cite-mode alternative CTA (short, verb-first).

## Deliberate exemptions

- Chat block does NOT show a starter kit inline for fresh
  tenants. That would put a heavy foundation-list block under
  every chat answer for tenants who haven't done anything yet —
  intrusive. Instead, chat emits a small `starter_nudge` link
  ("New here? See where to start →") pointing at the Get
  Started mode. Full experience lives on its dedicated surface.
- Chat block does NOT enumerate Comply/N/A cited refs — no
  point offering a template for something in place.
- Chat block does NOT include per-leaf format toggle buttons
  (`.docx` + `.xlsx` + `.md`) — one primary in the right shape,
  one `.md` alt link only. Full format matrix lives on the
  dashboard evidence-class panel. Chat stays uncluttered.

## Data spine (single source)

`rag/journey/state.py:compute_journey_state()` is the canonical
data path — computes per-leaf completion, per-anchor sequence,
phase, next actions. Both surfaces read from it:
- Get Started page: reads full state including
  `foundation_anchors`.
- Chat contextual block: reads posture from `posture_controls`
  (which is what `compute_journey_state` reads too, but
  independently — the chat block runs synchronously in
  `arion_graph.py:retrieve_node` and doesn't call the full
  journey computer to avoid latency).

## Files

- `rag/templates/answer_footer.py` — build_templates_block +
  helpers (_is_tabular, _formats_for, _fetch_finding_by_ref,
  _fetch_leaf_progress, _cite_acceptable_types)
- `rag/journey/state.py` — foundation_anchors field + compute
- `rag/llm_answer.py` — ComplianceAnswer.templates_block field +
  RANK_AND_ANSWER_SYSTEM rule
- `rag/arion_graph.py` — retrieve node wire
- `rag/arion_state.py` — ArionState.templates_block field
- `api_server.py` — ChatResponse.templates + streaming
  `templates` SSE event
- `static/arioncomply.html` — renderTemplatesBlock (chat) +
  loadGetStarted/renderGetStarted (mode) + sidebar nav item +
  setMode router

## Related memory

- [[dejargonize-ux-pass-2026-07-01]] — the natural-language
  pass this arc builds on. Every string in these two surfaces
  respects the vocabulary decisions locked there.
- [[tenant-journey-wizard-2026-06-24]] — the journey compute
  layer that both surfaces read. Extended (foundation_anchors
  field) not replaced.
- [[templates-v2-anchors-complete-2026-06-25]] — the 20
  hand-refined foundation templates that the Get Started page
  presents.
- [[per-must-advisory-2026-06-14]] — sibling surface
  (per-control advisory in chat + dashboard). Templates block
  complements it: advisory tells the tenant WHAT they need,
  the templates block gives them the artifact to fill.
- [[product-principle-evidence-stored-vs-cited]] — the cite-
  mode principle both surfaces respect ("you don't have to use
  these — cite existing systems instead").

## Carry-forward

The pattern of "structured payload → structural UI render" (not
"text-appended footer → renderMd") is now established. Any new
inline artifact surface for chat (e.g. per-answer evidence
gaps, per-answer verification prompts) should follow the same
pattern: emit as a structural field, render as a card block,
don't inject text into `answer_text`.

The `foundation_anchors` payload shape is reusable for future
work — the dashboard could also surface it if we want to hint at
foundation-first progress on the heatmap.
