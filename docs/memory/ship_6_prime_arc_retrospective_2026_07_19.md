---
name: ship-6-prime-arc-retrospective-2026-07-19
description: "Ship 6' arc retrospective — 5 sub-arcs auditing + hardening LLM role boundaries + observability for compliance stakes"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 6' arc — start-to-finish log of the LLM-role audit that
Ship 5'.f's retrospective opened. Entry-point for future work on
anything touching the chat pipeline's LLM boundaries, the
grounding gate, or the joined observability stack.

**Arc window:** 2026-07-18 → 2026-07-19. 5 sub-arcs across ~1.5
days.

## Motivation

Ship 5' hardened the LLM plumbing (consistent embedding model,
temperature=0.0 for structured JSON, single dispatch through
`llm_client.call`). Ship 5'.f left a follow-up that the user
picked up immediately as Ship 6':

> "audit the way we are using LLMs, every LLM use site and which
> LLM is in use, evaluate the role of LLM against a security
> compliance platform with no room for control hallucination"

The compliance-stakes framing is what makes this different from
5'. On a general RAG platform, an LLM hallucination is a
correctness bug. On ArionComply, it can be the difference
between "auditor sees NC" and "auditor sees Comply" — the
platform sits between a tenant and their regulator.

## Sub-arc inventory

| Sub-arc | Kind | Key win |
|---|---|---|
| 6'.a | Audit memo | Classification of 10 LLM sites as Determinative / Navigational / Compositional / Diagnostic; inventory of 13 anti-hallucination safeguards; **confirmed every compliance-load-bearing decision is deterministic** (engine, posture writes, cascade, notifications) |
| 6'.b | Code + tests | schema_v81 `document_findings.grounding_method` column + writer wiring + 8 formal grounding tests; backfilled 3839 rows |
| 6'.c | Retrospective | Data-driven look at `chat_casefile_log`: 87.7% of turns fire ≥1 preservation repair; ~3ms latency; verdict = feature not bug |
| 6'.d | Code + tests | schema_v82 `answer_text` + `claim_events` columns; passive claim scanner; 41-assertion test suite |
| 6'.e | Code + observability | schema_v83 `chat_llm_decision_trail` view + admin endpoint; fixed 0%-populated `request_id` wire-up |

Total: 3 schema migrations (v81/v82/v83), 2 new modules
(`claim_scan.py`, view+endpoint), 49 formal test assertions
across 2 test files, 2 memos, 1 retrospective memo (6'.c), 8
git commits.

## The framing shift 6'.a produced

Every LLM site got classified through a compliance-stakes lens:

- **Determinative** — outputs land in the DB as evidence
  claims. Extractor (`rag.intake.extractor`) is the only site.
  BOUNDED BY: verbatim-substring grounding gate at pass1 + pass2
  (`_evidence_grounded()`).
- **Navigational** — outputs drive routing. Classifier +
  consensus gatekeeper. BOUNDED BY: 7-signal consensus (Ship 1)
  with curator-authored lexicon as top-tier weight (1.00);
  gatekeeper can approve/modify/reject but never invent.
- **Compositional** — outputs are prose for humans. Chat answer
  (`rank_and_answer`) + document enricher. BOUNDED BY: case-
  file digest of verbatim MUST/SHOULD content + append-only
  preservation-check repair (Ship 2') + Ship 6'.d claim scan.
- **Diagnostic** — outputs feed observability, not decisions.
  Every LLM call writes to `ai_call_log` (Ship 5'.e allowlist).

The audit's most important finding: **no LLM site is
compliance-load-bearing without a deterministic gate in front
of or behind it.** The engine writes postures; the LLM only
proposes candidates for the engine to accept, reject, or
override. This wasn't obvious before 6'.a; now it's a codified
architectural property.

## Ship 6'.b corrected the framing further

The audit memo called extractor hallucination "material risk."
Ship 6'.b's implementation phase surfaced that
`_evidence_grounded()` already runs a punctuation-normalised
substring match against `doc.full_text` OR `doc.markdown` at
BOTH call sites (`extractor.py:385, :2151`), and drops findings
that fail. So the extractor path isn't hallucinating findings
into the DB — that specific path is deterministically safe.

What Ship 6'.b delivered was **auditor visibility** into which
safeguard fired:

```
document_findings.grounding_method CHECK-allowlist:
  extractor_verbatim  — LLM path, substring-verified
  workbook            — YAML matcher, value is the row data
  template            — <<MUST item:X>> deterministic path
  fingerprint         — ≥2-signal corroboration gate
  leaf_scan           — HITL-only back-bind
  manual              — UI/API direct
  form                — retired 2026-07-04
  unknown             — pre-6'.b backfill; xfw_bridge
```

Backfill from `inference_source` on 3839 existing rows was a
near-1:1 proxy; new writes populate the column explicitly.

## Ship 6'.c uncovered a design contract's strength

Preservation-check fires on **87.7% of chat turns** — nearly
every one. Instinct says "that's too high, something's
broken." Data says the opposite: the APPEND-ONLY repair pass
runs on almost every turn, adds ~3ms latency (0.1% of turn),
and guarantees that ~4700 events (dropped refs, dropped
`[DRAFT]` tags, dropped verdicts, dropped bridge footers) that
would otherwise silently disappear from LLM prose stay in the
auditor-facing footer.

The pass is a feature. The LLM stochastically drops
preservation-critical elements; deterministic append-only
repair catches them without rewriting prose. Design contract
holds.

## Ship 6'.d built the next tier of observability

Extractor is bounded by `_evidence_grounded()`. Chat pipeline
is bounded by preservation-check. What about the CLAIMS the
chat LLM makes in prose? "Art.32 requires X" statements that
could be paraphrased wrong.

Preliminary sampling on truncated `response_preview` (500-char
cap) showed ~5% raw claim rate; spot-checks accurate. So the
digest architecture is already suppressing this class. But we
had no per-turn record. Ship 6'.d added:

- `chat_casefile_log.answer_text` (8000-char cap)
- `chat_casefile_log.claim_events` (jsonb array of
  `{ref, verb, snippet, ref_in_digest, standard_in_scope}`)
- 3 regex patterns (direct / prepositional / generic)
- APPEND-ONLY passive: no rewrite, no block, no auto-warn

The two per-event signals — `ref_in_digest` +
`standard_in_scope` — surface the risky cases: LLM invoked a
ref not in the digest for this turn, OR a standard the tenant
isn't enrolled in. Neither has fired frequently yet, but the
observability now exists.

## Ship 6'.e closed a wire-up gap Ship 6'.d exposed

Adding claim_events surfaced that `chat_casefile_log.request_id`
was 0% populated. The API endpoint stamped it at request entry
(Wave 4c) into ai_trace ContextVars, but only `log_llm_call`
read the vars back. `log_casefile()` + `log_consensus()` took
the id as a parameter that nobody passed.

Ship 6'.e:

- Exposed getters (`current_session_id()`,
  `current_request_id()`, `current_tenant_id()`) on
  `ai_trace.py`
- Made both log writers fall back to ContextVars
- Built `chat_llm_decision_trail` view joining all three log
  tables on `request_id`
- Added `/api/v1/admin/chat/decision-trail` endpoint with
  filters (request_id / session_id / hours / only_repaired /
  only_ungrounded)

One row per chat turn now shows the full LLM decision trail:
consensus verdict + top_refs + gatekeeper fallback + prompt
tokens + repair events + footers + claim events + LLM call
aggregate (n_calls, tokens, cost, purposes, models). Auditor +
engineer surface without hand-JOINing.

## Architectural constants that emerged

1. **The engine, not the LLM, writes compliance postures.**
   Every load-bearing decision is deterministic. This isn't a
   convention; it's inspectable in the code + data (Ship 6'.a
   memo).

2. **Every LLM site has a verifier gate.** Extractor →
   `_evidence_grounded()`. Chat compose → preservation-check
   repair. Consensus gatekeeper → hard-lock on Signal
   B/C-derived fields. Enricher → downstream deterministic
   readers.

3. **APPEND-ONLY is the pattern for making LLM output
   auditor-safe.** Preservation-check appends footers; Ship
   6'.d claim scan logs claims. Neither rewrites LLM prose.
   The tenant sees natural language; the auditor gets a full
   trail.

4. **ContextVars beat threading ids through signatures.**
   Ship 6'.e's fallback pattern (call
   `current_request_id()` when the caller passes None) is
   less invasive than plumbing session_id through 8 layers.
   Same pattern already worked for `log_llm_call`; extending
   to `log_casefile` + `log_consensus` was 4 lines each.

5. **New columns get CHECK constraints.** `grounding_method`
   allowlist (6'.b) + `claim_events` shape via jsonb + partial
   indexes on "interesting subset" (6'.d
   `WHERE claim_events_count > 0`) prevent drift and make
   auditor queries cheap.

## Test suite impact

| Sub-arc | Tests added |
|---|---|
| 6'.b | `tests/test_extractor_grounding.py` — 8 assertions |
| 6'.d | `tests/test_claim_scan.py` — 41 assertions |
| **Total** | **49 new assertions** across 2 test files |

Eval baseline held at 207/208 PASS + 1 WARN + 0 FAIL across
every sub-arc (only pre-existing #200 gap_analysis WARN).

## Deferred / follow-up

- **Enforcement.** Ship 6'.d is passive; if `claim_events`
  data warrants it, promote to append-only warning footer
  (mirror preservation-check pattern).
- **Chat UI drill-in.** Ship 6'.e's decision-trail is admin-
  only. A tenant-facing "why this answer?" panel could render
  per-turn signals + LLM calls.
- **Preservation-check tuning experiments** from Ship 6'.c:
  digest DRAFT-prominence, prompt DRAFT emphasis, alerting on
  repair-rate drift, per-intent tuning.
- **Materialised decision-trail variant.** Ship 6'.e is a
  live view; if audit teams query historical traffic
  frequently, a materialised nightly refresh is the natural
  upgrade.
- **Model-tier divergence.** Ship 6'.e smoke test showed
  `rank_answer` running on gpt-4o-mini in the aggregate rather
  than gpt-4o. Might be an env override or an LLM-client
  fallback. Not investigated in-arc; a Ship 7 concern if it
  represents a regression from Ship 5'.d's config module.
- **Cross-session claim dedup.** If the same claim repeats 5
  times in one conversation, we want 1 review item, not 5. A
  session-scoped rollup view is the natural next step.
- **Enforcement CI grep** for direct-OpenAI imports outside
  the allowed files — carried over from Ship 5'.f, still
  deferred.

## Lessons carried forward

- **The audit itself was the deliverable.** Ship 6'.a produced
  no code but became the framing every subsequent sub-arc
  reasoned against. Without the Determinative / Navigational /
  Compositional / Diagnostic labels, we would have built
  observability without a coherent story.
- **Data before code.** Ship 6'.c's retrospective (87.7% repair
  rate) turned an instinct question ("is our repair pass a
  band-aid?") into a codified design confirmation. Same
  discipline drove Ship 6'.d's "measure first" landing (option
  A over full claim-check parser).
- **Correcting yourself in a follow-up arc is fine.** Ship
  6'.b explicitly said Ship 6'.a's framing was too strong —
  the extractor's grounding gate was already load-bearing. That
  correction lands in the memo, not in a retracted commit.
- **Ship-name discipline pays off.** 6'.a through 6'.e each
  correspond to a git commit + a memory doc + a CLAUDE.md
  build-sequence line. Every future contributor can trace back
  the exact scope of any sub-arc without archaeology.

## Ship 6' close

| Sub-arc | Status |
|---|---|
| 6'.a Role audit + safeguard inventory | ✓ |
| 6'.b Grounding provenance column + tests | ✓ |
| 6'.c Preservation-check retrospective | ✓ |
| 6'.d Passive claim-scan observability | ✓ |
| 6'.e Joined LLM decision-trail view | ✓ |
| **6'.f Arc retrospective** | **✓ (this doc)** |

## Related

- [[ship-5-prime-arc-retrospective-2026-07-18]] — previous arc
- [[ship-6-prime-a-llm-role-audit-2026-07-18]] — the audit that
  opened this arc
- [[ship-6-prime-b-grounding-provenance-2026-07-18]] — 6'.b
- [[ship-6-prime-c-preservation-retrospective-2026-07-19]] — 6'.c
- [[ship-6-prime-d-claim-scan-observability-2026-07-19]] — 6'.d
- [[ship-6-prime-e-decision-trail-view-2026-07-19]] — 6'.e
