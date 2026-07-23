---
name: ship-18-prime-arc-retrospective-2026-07-23
description: "Ship 18' arc closer — structured chat response payload (intro + actions[] + related[]); LLM emits JSON directly + backend builds related[] deterministically; 231/232 baseline restored after two JSON-mode prompt-rule fixes"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 18' arc retrospective — 4 sub-arcs across one day
(2026-07-23) delivering the structured chat response feature.
Origin: user report that the current prose blob + `↳ Compliance
facts:` footer was confusing (vague "1 of 4" enumeration, cryptic
related refs, truncation mid-word, no visual hierarchy).

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 18'.a | Design memo (schema + LLM emits intro+actions, backend builds related) | 477ca39 |
| 18'.b | Backend schema + JSON output + deterministic augmentation + preservation migration | c05e669 |
| 18'.c | Frontend card renderer + JSON-mode prompt-rule fixes (rules 7 + 8) | 68a36af |
| **18'.d** | **Eval + retrospective (this doc)** | pending |

## Feature summary

**Before**: single prose blob + `↳ Compliance facts: 10.1 [NC-DRAFT]
— ALL: 0 of 4 required items present (2 with partial evidence);
still needed: operating procedure, sc…` footer with truncation.

**After**: three-tier card render:
- **Intro card** — 1-2 sentence LLM framing + primary_ref chip
- **Action cards** — one per remediation step, each with title
  (imperative), body (concrete guidance with named items), refs
  chip row
- **Related-control cards** — one per cited/derived ref, with:
  * ref chip + standard_display + control title
  * verdict badge (color-coded NC / OFI / Comply / N/A)
  * DRAFT chip if posture unconfirmed
  * evidence_summary + still_needed items as inline chips
  * relation label (Primary / Demonstrates / Cross-framework link
    / Management-system clause / Related)
  * dashboard drill-in link

## Origin split — key architectural decision

**LLM emits ONLY `intro + actions[]`** via
`response_format={"type": "json_object"}`. Backend builds
`related[]` deterministically from CaseFile — role, verdict,
relation, evidence_summary, still_needed are all sourced from
Postgres + Neo4j.

Why the split:
- Every field on `RelatedCard` is deterministic. If we asked the
  LLM to emit them, it would either hallucinate or paraphrase the
  digest verbatim — cheaper + more accurate to derive.
- LLM stochastically drops refs (documented in Ship 2'.j). Backend
  scans all string fields for refs and reconciles against
  `cf.required_refs`. Missing refs still get RelatedCards inserted
  (APPEND-ONLY preservation invariant carried forward).

## Preservation-check migration

Ship 2' preservation-check today appends `↳ Compliance facts: ...`
to LLM prose. Ship 18 migrates the same logic to structured-payload
verification:

| Old (prose append) | New (structured) |
|---|---|
| Missing required ref | INSERT `RelatedCard` |
| Missing [DRAFT] tag | `draft: true` on card (deterministic) |
| Missing verdict adjacent | verdict field on card |
| Missing bridge footer | RelatedCard with `relation: cross_framework_bridge` |

Discipline preserved: APPEND-ONLY. LLM prose (intro + actions)
never rewritten. `chat_casefile_log.repair_events` still captures
what was augmented. New event kinds:
- `missing_ref_structured` — required ref got surfaced via card
  insertion
- `missing_draft_structured` — card.draft should have been true
  (defensive; deterministic path always sets correctly)
- `structured_parse_failed` — LLM emitted malformed JSON, prose
  path took over

## Eval outcome

| Baseline | Before | Ship 18'.b initial | **Ship 18'.c final** |
|---|---|---|---|
| PASS | 231/232 | 228/232 | **231/232** |
| WARN | 1 (#200) | 1 (#200) | **1 (#200)** |
| FAIL | 0 | 3 | **0** |

Ship 18'.b's initial eval regressed 3 cases:
- **#31** ISMS scope contents — musts_listing shape check wanted
  ≥5 enumerated items; LLM in JSON mode compressed to a
  comma-separated inline list
- **#222** ISO 27005 guidance — LLM in JSON mode dropped the
  literal "27005" mention
- **#224** ISO 27004 guidance — same failure mode as #222

All three closed in Ship 18'.c by adding two rules to
LLM_OUTPUT_RULES:
- **Rule 7**: GUIDANCE citations MUST appear by full ISO
  standard name in intro.text. Names 27002/27003/27004/27005/
  27701/27017/27018/27552/27799 explicitly.
- **Rule 8**: LISTING queries MUST enumerate every OBLIGATIONS
  item as newline-separated bullets prefixed with `- `. Includes
  an example format in the prompt.

Verified end-to-end: #31 → 18 bulleted items, #222 → contains
"27005", #224 → contains "27004". Full re-eval: 231/232 PASS
identical to prior baseline.

## Ship 14'.a addendum alignment (retroactive)

| Check | Applied |
|---|---|
| Role split? | YES — `RelatedCard.role` is FIRST-CLASS field (program/extension/obligation/guidance). Backend uses `cf.role_of(ref)` populated from tenant.scope role-map. |
| Parallel CaseFile view? | YES — digest unchanged; only OUTPUT shape changes. LLM sees identical CaseFile. |
| Deterministic routing? | YES — consensus + classifier + digest_plan unchanged. Presentation-layer arc only. |
| Guidance-normative discipline? | YES — cards carry role; guidance-role controls render distinguishably. Rule 7 makes guidance-standard citations explicit. |

## Codified properties post-Ship 18

- **Structured chat responses ship as an additive optional field**
  (`answer_structured`) — every existing consumer keeps working;
  frontend + SDK adopt on their schedule.
- **LLM emits only what it can't get wrong** — narrative text
  (intro + action title/body). Structural metadata (role, verdict,
  relation, evidence details) is 100% backend-computed. No
  hallucination surface for compliance-load-bearing facts.
- **APPEND-ONLY preservation carries forward to structured** —
  missing refs INSERT cards, LLM prose never rewritten. Same
  audit-safety idiom as Ship 2'.j (prose footer) and Ship 6'.d
  (claim scan).
- **Fail-open on malformed JSON** — LLM emits invalid JSON →
  `structured_parse_failed` event, prose path fires,
  `answer_structured` stays None. User still sees an answer.
- **JSON-mode prompt rules must be explicit** — LLM defaults to
  brevity in JSON mode. Rules 7 + 8 codify: guidance-standard
  names must appear verbatim, listing queries must bullet each
  item on its own line. Empirical from Ship 18'.b regressions.

## Design decisions that held

1. **`response_format=json_object` over prompt-only structured**
   — reliable JSON envelope from OpenAI; no parse-failure retries
   needed on happy path. Fail-open handles the edge case.

2. **Prose reconstruction from structured** — every structured
   response also emits `answer_text` composed as `intro.text +
   actions[title:body]`. This preserves eval assertions that
   scan `answer_text`, the preservation-check prose repair path,
   and downstream consumers (SDK / streaming clients) that
   haven't migrated.

3. **Related cards deterministic-only** — LLM never gets asked
   to populate the related-card fields. That would have made the
   LLM prompt significantly longer + introduced hallucination
   risk on role/verdict.

4. **Card render is opt-in per turn** — frontend prefers cards
   when `answer_structured` present, falls back to prose bubble
   otherwise. No forced migration.

## What Ship 18 did NOT do

- **Retire prose `answer` field** — kept for backward compat;
  future arc can retire once every consumer migrates.
- **Retire the `↳ Compliance facts:` prose footer** — it fires
  only when the structured path fails (fail-open). Full
  retirement is a future arc after we're confident LLM JSON
  output is reliable.
- **Migrate eval cases to structured shape** — assertions still
  scan `answer_text` (the reconstructed prose). Migrating to
  structured-payload assertions is a follow-up.
- **Anthropic response_format** — Anthropic uses a different
  JSON-mode API. Ship 18 is OpenAI-only for structured path.
  Anthropic prompt path stays on prose (fail-open catches it).
- **Extend structured to short-circuits** — deterministic
  short-circuits (postgres+llm, timeline queries etc.) still
  emit prose only. Only the case-file (LLM-generated) path
  produces `answer_structured`.

## Lessons

1. **JSON-mode compresses; codify the exceptions in prompt rules.**
   Regressions #31 / #222 / #224 all shared the same pattern:
   what the LLM did naturally in prose mode (bullet-listing,
   citing guidance standards by name) got compressed in JSON
   mode. Not a JSON limitation — a prompt calibration gap. Fixed
   by explicit rules with examples. Lesson generalizes: whenever
   you swap output modes, re-run eval, expect ~2% surface-level
   drift, close via prompt calibration not schema changes.

2. **LangGraph state schemas silently strip fields.** The first
   Ship 18'.b smoke test returned `answer_structured: null`
   despite the backend correctly populating it. Root cause:
   `ArionState` (TypedDict) didn't declare `answer_structured`.
   LangGraph's state machinery dropped it. Fix was one-line
   addition to `arion_state.py`. Pattern lesson: any new field
   that flows from a graph node → response envelope must be
   declared in the state schema first, or it disappears in
   transit.

3. **Deterministic derivation is safer than LLM structured emit.**
   The two-tier split (LLM prose fields / backend structural
   fields) delivered a payload that has no hallucination surface
   for role/verdict/relation. Same pattern applies elsewhere:
   any structural metadata that has a canonical source SHOULD be
   derived, not asked-for.

4. **Additive-optional lets you ship without a migration event.**
   `ChatResponse.answer_structured` is `Optional[dict]`. Frontend
   falls back. SDK unaffected. External API unaffected. Eval
   unaffected (prose reconstruction). One commit shipped a
   response-shape change without touching a single consumer.

## Ship 18 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 18'.a | Design memo + LLM-emits-what + preservation strategy | Locked JSON-mode-with-backend-augment split |
| 18'.b | Backend schema + JSON output + augmentation + preservation-check migration + state-schema fix | Structured payload end-to-end; 228/232 baseline (3 regressions surfaced) |
| 18'.c | Frontend card renderer + rules 7-8 (JSON-mode listing + guidance-name) | Baseline restored to 231/232 identical to Ship 15'.e |
| **18'.d** | **Eval + retrospective (this doc)** | **231/232 PASS + 1 WARN (#200) + 0 FAIL** |

## Related

- [[ship-2-prime-casefile-arc-2026-07-15]] — case-file architecture
  Ship 18 extends
- [[ship-2-prime-j-preservation-footer-2026-07-16]] — prose footer
  Ship 18 supersedes for structured turns
- [[ship-7-prime-arc-retrospective-2026-07-19]] — output gateway
  used for `standard_display` / `relation_display`
- [[ship-14-prime-a-role-model-arc-2026-07-22]] — role model
  `RelatedCard.role` implements
- [[ship-15-prime-d-demonstrates-sdk-2026-07-22]] — DEMONSTRATES
  traversal reused for `relation: demonstrated_by`
- [[tier4-starter-kit-arc-2026-07-02]] — precedent for structured
  payload alongside prose (templates block pattern)
- [[framework-role-model-arc]] — vocabulary carried through
  `RelatedCard.role` field
