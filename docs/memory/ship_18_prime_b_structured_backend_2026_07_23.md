---
name: ship-18-prime-b-structured-backend-2026-07-23
description: "Ship 18'.b — backend implementation of structured chat response; LLM emits intro+actions[] as JSON, backend builds related[] deterministically from CaseFile; end-to-end verified; initial eval regressed 3 cases closed in 18'.c"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 18'.b — backend implementation of the structured chat
response payload designed in 18'.a. Commit `c05e669`.

## New modules

- **`rag/casefile/answer_schema.py`** — Pydantic models:
  * `IntroCard` (text, primary_ref, primary_role)
  * `ActionCard` (title, body, refs[])
  * `RelatedCard` (ref, standard_id, standard_display, title,
    role, verdict, draft, relation, relation_display,
    evidence_summary, still_needed[], dashboard_url)
  * `StructuredAnswer` (intro + actions[] + related[])
  * `LLM_OUTPUT_RULES` — the OUTPUT FORMAT section appended
    to the case-file system prompt

- **`rag/casefile/answer_augment.py`** — deterministic augmentation:
  * `parse_llm_json(raw)` + `parse_structured_answer(raw)` —
    tolerates markdown-fenced JSON + trailing prose; returns
    None on malformed input
  * `collect_all_refs(structured)` — scans intro.text +
    actions[].title/body for cited refs
  * `build_related_cards(cf, structured, pg_conn, tenant_id,
    extra_refs)` — deterministic role/verdict/relation lookup
    + `build_per_must_advisory_data` for evidence_summary +
    still_needed items; classifies relation as primary /
    demonstrated_by / cross_framework_bridge / isms_clause /
    context (uses `cf.demonstrated_by(primary_ref)` for the
    demonstrated_by set)
  * `augment_and_repair(structured, cf, spec, ...)` — inserts
    missing required_refs as RelatedCards; APPEND-ONLY (LLM
    prose never rewritten); returns repair_events for the log

## Wiring changes

- **`rag/llm_client.py::call`** — `response_format` passthrough
  to the OpenAI-compatible payload. No-op on Anthropic wire.
- **`rag/llm_answer.py::_call_llm`** — forwards
  `response_format` to `llm_client.call`.
- **`rag/llm_answer.py::_casefile_flow`** — new flow:
  1. `build_structured_prompt_pair(cf)` — system prompt gains
     `LLM_OUTPUT_RULES`
  2. `_call_llm(response_format={"type": "json_object"})`
  3. `parse_structured_answer(raw)` — on success:
     * Open short-lived pg connection (SET LOCAL app.tenant_id)
     * `augment_and_repair(structured, cf, spec, pg_conn, tenant_id)`
     * Compose prose `answer_text` from `intro.text +
       actions[title:body]` for backward compat +
       preservation-check parity
  4. Prose repair pass (`check_and_repair`) still fires — repair
     events from both structured + prose paths merge into
     `chat_casefile_log`.
  5. Fail-open: on `parse_structured_answer(raw) is None`, log
     `structured_parse_failed`, use raw as prose, prose repair
     path takes over.
- **`ComplianceAnswer.answer_structured: dict | None`** added.
- **`ArionState.answer_structured: dict | None`** added.
  Critical — LangGraph strips fields not declared on the state
  schema. This was the bug in the first Ship 18'.b smoke test
  (`answer_structured` came back None despite backend populating
  it correctly).
- **`arion_graph.build_answer_envelope`** accepts + propagates
  `answer_structured` into result dict.
- **`api_server.ChatResponse.answer_structured`** added; sync
  chat wires it via `result.get("answer_structured")`.
- **Streaming endpoint** emits new SSE event
  `type: "answer_structured", block: {...}` BEFORE the
  `templates` event.
- **`rag/output/gateway.py`** — new `structured_card` surface
  chain (strip_markdown_escapes + humanize_snake_case +
  format_standard_id) for standard_display / relation_display
  humanization.

## Verified end-to-end on live tenant

| Query | Structure |
|---|---|
| "how do I remediate A.5.15?" | intro + 3 action cards + 3 related cards (A.5.15 primary OFI 1/4 + 10.1 isms_clause NC 0/4 + 10.2 isms_clause NC 0/4) — still_needed names 3 concrete leaves |
| "what is A.5.18?" | definition-shaped payload |
| "are we GDPR compliant?" | 5 actions + 6 related (obligation role recognized) |
| "what are our NC findings?" | 5 actions + 9 related |

## Initial eval outcome

**228/232 PASS + 1 WARN + 3 FAIL** — regressed from Ship 15'.e
baseline of 231/232.

The 3 regressions:
- **#31** "what must our ISMS scope statement contain?" —
  `musts_listing: 0 enumerated items (expected ≥5)`. LLM in
  JSON mode compressed 18 items into a comma-separated inline
  list instead of newline-bulleted.
- **#222** "what does ISO 27005 recommend..." —
  `MISSING required phrase: '27005'`. LLM dropped the literal
  standard name from intro/actions text.
- **#224** "what does ISO 27004 say..." — same failure mode as
  #222.

Root cause: `response_format=json_object` biases the LLM toward
brevity. Prose-mode behaviors (enumerated bullets, cross-
framework guidance-standard citations by name) got compressed.
Not a JSON limitation — a prompt calibration gap.

Fixed in Ship 18'.c via two new LLM_OUTPUT_RULES entries.

## Fail-open behavior

If `json.loads` raises or `parse_structured_answer` returns
None, the case-file flow logs `structured_parse_failed` to
`repair_events` and continues with the raw text as prose. Prose
`check_and_repair` fires as normal. `answer_structured` stays
None on the response; frontend falls back to prose bubble
render. User gets an answer either way.

## Backwards compat

- `ChatResponse.answer_structured` is `Optional[dict] = None` —
  existing consumers unaffected.
- SDK unchanged in this arc.
- Eval assertions still scan `answer_text` (composed from
  structured for parity).
- External API (`/api/external/v1/query`) unaffected — that
  endpoint returns its own shape and doesn't emit
  `answer_structured` yet (future arc if partners ask).

## Ship 14'.a addendum alignment

1. **Role split?** YES — `RelatedCard.role` field is FIRST-CLASS.
   Backend uses `cf.role_of(ref)` populated from tenant.scope
   role-map.
2. **Parallel CaseFile view?** YES — digest unchanged; only
   OUTPUT shape changes.
3. **Deterministic routing?** YES — consensus + classifier +
   digest_plan unchanged.
4. **Guidance-normative discipline?** YES — cards carry role;
   guidance controls render distinguishably. Ship 18'.c's
   Rule 7 makes this explicit for guidance-standard citations.

## Ship 18 progress

| Sub-arc | Status |
|---|---|
| 18'.a Design memo | ✓ (477ca39) |
| **18'.b Backend schema + LLM structured output** | **✓ (c05e669, this doc)** |
| 18'.c Frontend card renderer + prompt rules | next |
| 18'.d Eval + arc retrospective | pending |

## Related

- [[ship-18-prime-a-structured-answer-design-2026-07-23]] — design
- [[ship-2-prime-casefile-arc-2026-07-15]] — case-file arc extended
- [[ship-2-prime-j-preservation-footer-2026-07-16]] — prose footer
  Ship 18 supersedes for structured turns
- [[ship-14-prime-a-role-model-arc-2026-07-22]] — role model that
  `RelatedCard.role` implements
- Ship 18'.c: frontend renderer + rules 7+8 to close regressions
