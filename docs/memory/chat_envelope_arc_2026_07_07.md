---
name: chat-envelope-arc-2026-07-07
description: Chat pipeline refactor — 13 scattered retrieve() return sites collapsed into build_answer_envelope; templates_block + per-MUST advisory unified into a single next-action payload
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Extension of the "deterministic-first" arc that started with the
role model + LLM-free intake. Chat layer's turn: the retrieve()
function had ~13 return dicts, each open-coding its own subset of
{answer_text, cited_refs, question_type, intent_type, templates_block,
posture_findings, ...}. That divergence produced the class of bugs
we saw today alone — templates_block dropped by the POSTURE_CHECK
enumeration path; `type: None` in enumeration; two overlapping
"what next" surfaces (templates_block cards + per-MUST advisory
prose appendix).

Tenant surfaced this asking "why do we have two chat surfaces for
what next?" — good instinct. The fix is architectural, not cosmetic.

## Design

Single `build_answer_envelope()` function at module level in
`rag/arion_graph.py`. Every retrieve() return site calls it. The
envelope enforces:

- `answer_text` also set as `answer` (alias — some consumers read either)
- `question_type` also written to `intent_type` (both fields are read
  downstream; comment at ~line 2055 explains why they must be kept
  in sync — timeline short-circuit context)
- When `state` supplied, spread it first (chat short-circuit shape);
  explicit fields override
- Auto-attach `templates_block` when `attach_templates=True` AND
  cited_refs non-empty AND tenant resolvable AND question_type
  is action-oriented (matches answer_footer._RELEVANT_QUESTION_TYPES)
- Auto-append per-MUST advisory appendix when `attach_advisory=True`
  AND exactly ONE cited_ref AND question_type in {posture_check,
  cross_framework}. Uses `intent.cited_refs` preferentially (matches
  pre-envelope classifier-refs-first behavior)
- LLM-path metadata (`verified`, `posture_findings`, `node_count`,
  `neo4j_ms`, `resolver_trace`, `last_entity`) included only when
  supplied — chat short-circuits typically pass None → keys omitted

## Migration in three waves

**Wave 1 (43685d6)** — Migrated the 2 fresh-dict paths (LLM
fallback + deterministic POSTURE_CHECK enumeration). Also
fixed the API-side `type: None` bug: question_type isn't in
ArionState schema, so LangGraph strips it from graph.invoke()
output; intent_type IS in schema. API now reads intent_type as
primary fallback for the `type` response field.

**Wave 2 (67ea47c)** — Migrated the 11 chat short-circuit
sites: deictic clarify, acknowledge-gap, stage-1 chat, stage-2
chat, scope N/A, cascade follow-ups, cascade suppressions,
cascade implications, timeline, upload status, resolver
short-circuit. All passed `attach_templates=False +
attach_advisory=False` — these are conversational
confirmations or process-state reports; pushing template
downloads on top would misfire.

**Wave 3 (part of 341a985)** — Retired the per-MUST advisory
text appendix from the envelope entirely. Advisory data now
flows through templates_block.leaves[] via new fields:
`items_missing[]`, `items_have[]`, `upload_hint`. Chat prose
stays about the finding; actionable "what next" lives entirely
on the structured cards.

## Unified next-action payload (#204 / 341a985)

`build_templates_block` enriches each leaf with per-MUST advisory
data via `build_per_must_advisory_data`. Same standard-id
disambiguation (Art. → GDPR, B. → 27701, A.x.y.z → 27701, else
→ 27001). Cards now show:

- `progress` — bound/total/remaining counts
- `items_missing[]` — MUSTs with no active binding (SPA shows
  up to 3 bullets + "…and N more" overflow)
- `upload_hint` — one-line remediation prompt per leaf
- `primary_download` + `alt_downloads` — template CTAs
- `cite_acceptable` — external-system attribution flag
- `dashboard_url` — drill-in link

Impact — "is A.5.15 compliant?" answer_text: 6100 → 1381 chars.
Advisory prose retired; same data now visible on cards, one
per leaf.

Eval case #199 re-authored: was locking prose strings
("How to strengthen", "Still needed:", "Source: ISO/IEC"). Now
locks structural routing (A.5.15 as posture_check + no hedging).
Data validation moves to direct API probes since the eval
framework doesn't yet inspect templates_block (a `templates_shape`
validator would be a natural Wave 4 enhancement).

## What NOT to do next time

- Never wrap 13 return sites in an abstraction that just
  copies the mess. The envelope was designed after cataloging
  what each site ACTUALLY set — real needs, not defensive
  superset. Every field in the envelope's signature is a real
  need at ≥1 site; anything absent from all 13 sites doesn't
  belong.
- Don't leave `attach_advisory` parameter as dead weight
  forever — Wave 4 should drop it once no callers reference
  it (kept for now to avoid API surface churn).

## Related

- [[llm-free-intake-arc-2026-07-06]] — the deterministic-first
  direction this extends
- [[framework-role-model-arc]] — the architectural precedent
  (deterministic classification via role/subject metadata)
- [[feedback-eval-state-drift]] — Pattern 3 (LLM prose drift)
  explains why locking specific advisory phrases was fragile
