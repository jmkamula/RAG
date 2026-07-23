---
name: ship-18-prime-a-structured-answer-design-2026-07-23
description: "Ship 18'.a — design memo for structured chat response payload (intro + actions[] + related[]); LLM emits JSON directly + backend augments with deterministic role/verdict/relation from posture data; retires prose footer"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 18'.a — opens Ship 18 arc (structured chat response).
Direct follow-up to a user report that the current prose-blob +
`↳ Compliance facts:` footer confused them (unclear how related
refs relate to the primary control; item enumeration was vague;
truncated text mid-word). Redesign into cards.

## Root-cause analysis

Today's chat response shape (from a live "how do I remediate
A.5.15?" query):

```
To remediate ISO 27001 A.5.15 (Access control), which requires...
you need to address the following gaps identified in the current
posture:

1. Complete the required items: Currently, only 1 of the 4
   required items is present...
2. Enhance evidence: For the items with partial evidence...
3. Review and update policies...
4. Training and awareness...

↳ Compliance facts: 10.1 [NC-DRAFT] — ALL: 0 of 4 required items
present (2 with partial evidence); still needed: operating
procedure, sc…; 10.2 [NC-DRAFT] — ALL: 0 of 4 required items
present (2 with partial evidence); still needed: operating
procedure, sc…; A.5.15 [OFI-DRAFT] — ALL: 1 of 4 required items
present ...
```

Failure modes:
1. **Vague enumeration** — "1 of 4 required items is present" but
   items aren't named. Tenant can't act.
2. **Cryptic footer** — refs 10.1 / 10.2 appear without
   explaining they're ISMS clauses that relate to A.5.15 by
   role-model (obligation/program relationships).
3. **Truncation** — "still needed: operating procedure, sc…"
   drops mid-word. Preservation-check appends footer under a
   truncation cap; auditor-critical data lost.
4. **No visual hierarchy** — 4 numbered points share a paragraph;
   the LLM stochastically drops one across retries; UI can't
   render actions distinctly from context.

## The fix: structured payload

Extend `ChatResponse` with a new optional `answer_structured`
field carrying an explicit payload the frontend renders as cards.
Keep `answer` (prose) for backwards compatibility + fallback.

### Payload schema

```python
class StructuredAnswer(BaseModel):
    intro:   IntroCard         # required — always present
    actions: list[ActionCard]  # 0..N; empty for definition/status queries
    related: list[RelatedCard] # 0..N; one per cited/derived ref

class IntroCard(BaseModel):
    text: str                  # 1-2 sentences; primary framing
    primary_ref:  Optional[str]      # e.g. "A.5.15" — the query focus
    primary_role: Optional[str]      # program / extension / obligation / guidance

class ActionCard(BaseModel):
    title: str                 # short imperative — "Complete the register"
    body:  str                 # concrete guidance; names items when known
    refs:  list[str] = []      # refs this action addresses (populated by backend scan)

class RelatedCard(BaseModel):
    ref:            str        # "A.5.15" / "Art.32" / "10.1"
    standard_id:    str        # "ISO27001:2022"
    standard_display: str      # "ISO 27001:2022" (Ship 7' gateway)
    title:          str        # control title (deterministic from Neo4j)
    role:           str        # program / extension / obligation / guidance
    verdict:        str        # NC / OFI / Comply / N/A / Unknown
    draft:          bool       # True when posture not auditor-confirmed
    relation:       str        # primary / demonstrated_by /
                               # cross_framework_bridge / isms_clause / context
    relation_display: str      # gateway-humanized ("Cross-framework link", etc.)
    evidence_summary: str      # deterministic: "1 of 4 required items present"
    still_needed:   list[str] = []  # deterministic: name items with no evidence
    dashboard_url:  Optional[str]   # deep-link to /dashboard drill-in
```

### Origin: LLM emits JSON directly

Chosen path (see Ship 18 direction question 2026-07-23): use
OpenAI `response_format={"type": "json_object"}` — the LLM's
raw response IS the payload. Backend validates + augments.

LLM contract:
- Emits `{intro: {...}, actions: [...]}` — **NOT `related`**.
- Refs appear naturally in `intro.text` + `action.body`.
- Backend extracts refs from all string fields, then builds
  `related[]` deterministically from posture data.

Why LLM doesn't emit `related`:
- Every field on `RelatedCard` (role, verdict, relation,
  evidence_summary, still_needed) is deterministic — LLM would
  either hallucinate or paraphrase what the digest already
  contains verbatim. Cheaper + more accurate to derive.

Why backend augments rather than LLM listing refs:
- LLM stochastically drops refs (Ship 2'.j lesson). Backend
  scans + reconciles against the CaseFile's required_refs set.
- If LLM output has fewer refs than the required_refs set,
  backend still emits missing ones as `related` cards with
  `draft: true` — auditor visibility, APPEND-ONLY discipline.

### Preservation-check migration

Ship 2' preservation-check today appends `↳ Compliance facts:
...` to the LLM's prose. Ship 18'.b migrates the same logic
to structured-payload verification:

| Old (prose append) | New (structured) |
|---|---|
| Missing required ref → append `↳ Compliance facts: A.5.15 [OFI-DRAFT] ...` | Missing required ref → INSERT `RelatedCard` with `draft: true` if unconfirmed |
| Missing [DRAFT] tag near mentioned ref → append draft note | `draft` field on card carries this — no repair needed if card exists |
| Missing verdict adjacent to ref → append verdict | `verdict` field on card carries this — no repair needed if card exists |
| Missing bridge footer → append `↳ Bridges to ISO 27001 ...` | Emit cross-framework refs as `RelatedCard` with `relation: cross_framework_bridge` |

**Discipline preserved**: APPEND-ONLY. LLM prose never rewritten.
Missing structural elements INSERTED as new cards, not injected
into prose. `chat_casefile_log.repair_events` still captures
what was augmented.

### Backend augmentation flow

```
LLM emits:  {intro: {text, primary_ref?}, actions: [...]}
     ↓
extract_all_refs(intro.text + actions[].body + actions[].title)
     ↓
for each ref:
    lookup posture, role, evidence_summary from CaseFile
    build RelatedCard
     ↓
preservation_check:
    for ref in cf.required_refs:
        if ref not in structured.related:
            insert RelatedCard (repair event)
     ↓
StructuredAnswer(intro=..., actions=..., related=[cards...])
```

Deterministic sources (all from CaseFile, no LLM):
- `role` — from `RequirementNode.role` (Neo4j)
- `verdict` + `draft` — from `posture_by_ref` (Postgres)
- `evidence_summary` + `still_needed` — from
  `build_per_must_advisory_data` (Ship 15'.d
  `demonstrated-by` uses the same)
- `title` — from `RequirementNode.title` (Neo4j)
- `relation` — computed:
  * "primary" if ref == `intro.primary_ref`
  * "demonstrated_by" if the primary_ref is an obligation and
    this ref is one of its DEMONSTRATES sources
  * "cross_framework_bridge" if this ref lives in a different
    standard from the primary AND has an IMPLEMENTS/SUPPORTS/
    ENABLES edge
  * "isms_clause" if ref is 4.x-10.x ISO body clause and
    primary is Annex A
  * "context" otherwise (LLM cited but not related structurally)
- `standard_display` + `relation_display` — Ship 7' gateway
- `dashboard_url` — `/#dashboard/control/{ref}?standard_id={sid}`

### LLM prompt changes

Extend `_SLIM_SYSTEM` (in `rag/casefile/digest.py`) with:
1. Output-format section: "Return a JSON object with exactly two
   keys: `intro` and `actions`. Never emit `related` — the backend
   computes it."
2. Card-shape hints per query type: DEFINITION → `actions=[]`;
   GAP_ANALYSIS/REMEDIATION → 3-5 action cards; POSTURE_STATUS →
   `actions=[]`; CROSS_FRAMEWORK → 0-3 action cards.
3. Rule for `body`: "When you know specific item names from the
   POSTURE / OBLIGATIONS section, name them. Never write '1 of 4'
   without naming which items are present + missing."
4. Rule for `title` (action): "Imperative, ≤80 chars. Not a
   restatement of the body."

Prompt token budget grows ~200 tokens for the JSON schema
description. Case-file digest itself doesn't change.

### Frontend renderer

`static/arioncomply.html` — client-side changes only in 18'.c:

- Chat response handler checks `resp.answer_structured` first;
  falls back to `resp.answer` prose if absent.
- Render 3 sections:
  1. **Intro card** — top; `primary_ref` chip badge + prose.
  2. **Action cards** — middle; iterate `actions[]`; each shows
     `title` (bold header) + `body` (paragraph) + ref chips.
  3. **Related-control cards** — bottom; iterate `related[]`;
     each shows:
     - ref chip + `standard_display` + `title`
     - verdict badge (color-coded NC/OFI/Comply/N/A)
     - `[DRAFT]` chip if `draft: true`
     - one-line evidence summary + `still_needed` bullet list
     - `relation_display` label (small, muted)
     - dashboard drill-in button
- Retire the `↳ Compliance facts:` line from the answer_text
  render path when `answer_structured` is present (footer
  becomes redundant — first-class UI carries the same info).
- Templates block continues to render below related cards (it
  serves a different purpose — action-oriented starter downloads).

### Streaming

`GET /api/v1/chat/stream` yields SSE events. Extend with:
- `type: "answer_structured"` — sent AFTER the prose completes
  (backend needs full LLM output to validate JSON). Frontend
  swaps the prose render for the structured render on receipt.
- If JSON validation fails (LLM emitted malformed output),
  keep the prose render + log the failure. Fail-open.

## Ship 14'.a addendum alignment

| Check | Applied |
|---|---|
| Role split? | YES — `RelatedCard.role` is FIRST-CLASS field (program/extension/obligation/guidance). Reinforces the framework-role-model discipline in the UI. |
| Parallel CaseFile view? | YES — digest still drives what's shown; only OUTPUT shape changes. LLM sees identical CaseFile. |
| Deterministic routing? | YES — consensus signals + digest plan unchanged. Ship 18 is presentation-layer only. |
| Guidance-normative discipline? | YES — cards carry `role`; guidance controls render distinguishably from normative (program/extension) so tenant doesn't confuse ISO 27002/27003 references with 27001 posture claims. |

## Backwards compatibility

- `ChatResponse.answer_structured` is `Optional[dict] = None`.
- Frontend falls back to `answer` (prose) if structured absent.
- External SDK (`sdk/python/arioncomply`) can adopt structured
  in a follow-up minor version; existing consumers unaffected.
- Streaming: prose events continue to emit; structured event
  is additive.

## Sub-arc plan

### 18'.b — Backend

- `rag/casefile/answer_schema.py` — new `StructuredAnswer` +
  card models + JSON schema string for LLM prompt.
- `rag/casefile/digest.py::_SLIM_SYSTEM` — add output-format
  section + card-shape hints.
- `rag/llm_client.py::call` — add `response_format` passthrough
  (currently no `json_object` support).
- `rag/llm_answer.py::_casefile_flow` — parse LLM JSON output,
  call `build_related_cards(cf, structured, cited_refs)`,
  call `augment_and_repair(structured, spec, cf)`, attach to
  `ComplianceAnswer.answer_structured`.
- `rag/casefile/answer_augment.py` — new module:
  - `build_related_cards(cf, structured, refs)` — deterministic
    role/verdict/relation/evidence lookup
  - `augment_and_repair(structured, spec, cf)` — missing-ref
    insertion; returns RepairEvents
- `rag/casefile/repair.py` — keep existing prose-repair for
  fallback (when LLM emits malformed JSON). Two paths:
  structured OR prose.
- `api_server.py::ChatResponse` — add `answer_structured` field.
- Streaming: emit `answer_structured` SSE event.

### 18'.c — Frontend

- `static/arioncomply.html`:
  - New helpers `renderIntroCard()` / `renderActionCard()` /
    `renderRelatedCard()`.
  - Chat message renderer branches: structured → cards; else
    prose. Card CSS uses existing Tabler card classes for
    consistency with templates block.
  - Verdict badge color mapping (reuse
    `_POSTURE_BADGE_CLASSES` from dashboard).
  - Related card dashboard drill-in reuses
    `showControlDetail(ref, standard_id)`.
  - Strip `↳ Compliance facts:` from prose IF structured
    present (defensive — backend should suppress the footer,
    but belt-and-suspenders).

### 18'.d — Eval + retro

- Adjust `EvalCase` for structured mode: new `shape="cards"`
  with slot-level assertions (has_intro, has_actions with
  specific titles, related contains specific refs with
  specific verdicts).
- Migrate 5-10 representative cases as pilots; keep the rest
  on prose-shape (both paths coexist).
- Retro codifies the pattern.

## Design decisions locked in 18'.a

1. **LLM emits `intro` + `actions` only** — `related` is 100%
   deterministic. Cheaper, more accurate, no hallucination
   surface for structural metadata.

2. **APPEND-ONLY preservation** preserved — missing elements
   INSERT new cards, never rewrite LLM prose. Audit-safety
   invariant carried forward from Ship 2'.

3. **`answer_structured` is additive** — existing `answer` prose
   field stays. Migration is opt-in per response, per client,
   per SDK version.

4. **Streaming: prose first, structured second** — SSE order:
   `chunk` (prose stream) → `structured` (after LLM completes).
   Prose keeps the perceived-latency feel; structured swaps in
   for the final render.

5. **Fail-open on malformed JSON** — if `json.loads()` raises
   or Pydantic validation fails, keep the prose path + log to
   `chat_casefile_log.repair_events` with a new kind
   `structured_parse_failed`. Don't block the answer.

6. **`related` cards render at the bottom** — action cards are
   the answer's payoff; related cards are supporting evidence.
   UX-wise: action first, provenance second. Matches how
   auditors read (recommendation → evidence trail).

7. **Deterministic augmentation always fires** — even if LLM
   omits ALL refs in prose, backend still builds `related[]`
   from `cf.required_refs`. Missing structural metadata is a
   design guarantee, not a best-effort.

## What Ship 18 does NOT do

- **Retire prose `answer`** — the field stays. Structured is
  additive.
- **Migrate all eval cases** — pilot only in 18'.d; broader
  migration is a future arc.
- **Change consensus / classifier / digest logic** — presentation
  layer only.
- **Rewrite `build_templates_block`** — templates block serves
  a different purpose (starter downloads for NC/OFI). It renders
  alongside the new related cards, not replaced by them.
- **Support Anthropic response_format** — Anthropic uses a
  different JSON-mode API. First cut is OpenAI-only; Anthropic
  path stays on prose. Case-file chat uses OpenAI models today
  so no coverage gap.
- **Retire the `↳ Compliance facts:` footer entirely** — Ship
  18 makes it redundant WHEN `answer_structured` is present.
  If frontend can't render structured (older SDK / API-only
  consumer), the prose footer still fires. Full retirement is
  a future arc.

## Ship 18 progress

| Sub-arc | Status |
|---|---|
| **18'.a Design memo (this)** | **✓** |
| 18'.b Backend schema + LLM structured output | next |
| 18'.c Frontend card renderer | pending |
| 18'.d Eval + arc retrospective | pending |

## Related

- [[ship-2-prime-casefile-arc-2026-07-15]] — the case-file arc
  whose preservation-check discipline Ship 18 extends
- [[ship-2-prime-j-preservation-footer-2026-07-16]] — the prose
  `↳ Compliance facts:` footer this arc migrates to cards
- [[ship-7-prime-arc-retrospective-2026-07-19]] — output gateway
  used for `standard_display` + `relation_display`
- [[tier4-starter-kit-arc-2026-07-02]] — precedent for structured
  card payload alongside prose (templates block)
- [[ship-15-prime-d-demonstrates-sdk-2026-07-22]] — DEMONSTRATES
  traversal reused for `relation: demonstrated_by`
- [[framework-role-model-arc]] — the program/extension/obligation/
  guidance vocabulary that `RelatedCard.role` carries
