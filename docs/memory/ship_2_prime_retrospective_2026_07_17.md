---
name: ship-2-prime-retrospective-2026-07-17
description: "End-of-arc retrospective for Ship 2' (Ship 2 revert through Ship 2'.p). 15 sub-arcs across 2026-07-15/16/17. Case-file architecture + role model + id_types + anti-drift discipline + legacy-path retirement. Baseline held 207/208 throughout. Entry point for future work on the chat pipeline."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 2' arc — RETROSPECTIVE 2026-07-17. Full sequence: 2'.a → 2'.p
(15 sub-arcs) across 3 days. Commits `f246df3` (revert) →
`e198c8b` (leaf_id migration).

**Why the arc happened:** rank_and_answer's prompts were averaging
21,731 tokens per call (peak 61,827) — the LLM was drowning in
context. Case #14 + #33 residuals surfaced the symptom: LLM
stochastically dropped required refs / acronyms from prose. Ship 2
(AnswerPayload dispatcher) was the initial attempt but was
recognized mid-session as duplication of ResolvedContext data
without new information. Reverted. Ship 2' rebuilt lean.

**How the arc unfolded** (in order):

Phase 1 — case-file foundation (a → h, 2026-07-15):
- 2'.a audit: baseline confirmed 21,731 avg / 61,827 peak
- 2'.b CaseFile dataclass (17 tests)
- 2'.c build_prompt_digest (37 tests, 658 tokens on realistic case)
- 2'.d extract_preservation_spec (16 tests)
- 2'.e check_and_repair (23 tests)
- 2'.f wire into rank_and_answer behind CASEFILE_ENABLED flag
- 2'.g schema_v68 chat_casefile_log
- 2'.h docs + eval spot-check (5/5 wins on flaky cases)

Phase 2 — architecture + discipline (i → j, 2026-07-16):
- 2'.i: introduced rag/id_types.py (TenantUUID / NodeId /
  ControlRef / LeafId — validate at construction). Fixed
  arion_state.py:89 (`state["tenant_id"]` was display name, not
  UUID — root of chat_casefile_log silent-fails). Retired
  primary/xfw layer split per framework-role-model-arc. Added
  "Read the arc first" table + "Legacy — do not extend" section
  to CLAUDE.md as anti-drift discipline.
- 2'.j: closed 3 residual eval fails (#11, #31, #214) via
  role-model-aware digest guidance + document-content MUST
  enumeration.

Phase 3 — API-boundary hardening (k → l, 2026-07-16):
- 2'.k: FastAPI Pydantic path-param validators — 36 endpoints
  now return 422 with structured errors on wrong-shape IDs (was
  500 from psycopg2 `::uuid` cast). Also: fail-loud on the
  known silent-fail log-write catches.
- 2'.l: session_id shape validation + build_thread_id() using
  full tenant UUID (was `[:8]` — 2^32 collision surface eliminated).

Phase 4 — mechanical cleanup + legacy retirement (m → p, 2026-07-16/17):
- 2'.m: retired 21 inline `node_id.split(":")` sites via
  `ref_of()` / `standard_of()` helpers.
- 2'.n: retired the legacy `rank_and_answer` body (~912 LOC) +
  inline `_infer_primary_std` + file-scope `_pick_primary_std` +
  `CASEFILE_ENABLED` env flag. Case-file flow is the only path.
- 2'.o: retired `USE_LEGACY_CLASSIFIER` kill-switch +
  `consensus_layer_enabled()`. Consensus always runs; intra-
  consensus fallback stays.
- 2'.p: retired 17 leaf_id / item_id `.split(":")` sites. Added
  ItemId type + accessors. All composite-ID splits now typed.

**Baseline held throughout:**
- Ship 1.7d baseline (pre-2'): 205/208, 2 FAIL (#14, #33 residuals)
- Ship 2'.j → .k → .m → .n → .o → .p: **207/208** across every
  run. Only non-PASS is #200 — pre-existing type mismatch
  unrelated to Ship 2'.
- No arc ever regressed the baseline.

**What stays (going-forward guidance):**

1. **Case-file architecture** is the chat prompt-assembly layer.
   Any new signal → CaseFile once; digest + preservation both
   read from it.

2. **Role model** (framework-role-model-arc) is the multi-framework
   architecture. Programs / extensions / obligations. Never
   re-introduce primary/xfw layer splits.

3. **rag/id_types.py** is where composite-ID logic lives.
   TenantUUID / NodeId / ControlRef / LeafId / ItemId as
   validate-at-construction str subclasses. Add new types here
   as new ID shapes appear. Use safe helpers (ref_of, standard_of,
   leaf_control_ref, etc.) for legacy-fallback consumption; use
   the classes directly for new code that should be strict.

4. **Naming rule** (CLAUDE.md): if a field is called `X_id`, it
   MUST be the canonical UUID. `X_name` for display, `X_slug`
   for URL-safe stable, `X_ref` or `X_node_id` for composite refs.

5. **No feature flags** on newly-introduced infrastructure without
   an explicit retire-by date. `CASEFILE_ENABLED` and
   `USE_LEGACY_CLASSIFIER` both retired at Ship 2'.n / .o
   respectively.

6. **Anti-drift discipline in CLAUDE.md**:
   - "Before touching module X, read arc Y" table
   - "Legacy — do not extend" section with grep-able anti-patterns
   Every new arc should add an entry to both when it
   supersedes something.

**Metrics achieved:**

| Metric | Before Ship 2' | After Ship 2'.p |
|---|---|---|
| avg rank_answer prompt tokens | 21,731 | ~1,200 (17× reduction) |
| Peak rank_answer prompt tokens | 61,827 | ~3,900 |
| Eval baseline | 205/208 (2 fails) | 207/208 (0 fails, 1 WARN) |
| Feature flags | 2 (CASEFILE_ENABLED, USE_LEGACY_CLASSIFIER) | 0 |
| `.split(":")` inline sites | 38+ | 0 (all typed via id_types) |
| API path-param validators | 0 | 36 endpoints |
| Legacy escape hatches | 3 (`_is_uuid_shape`, layer split, kill switch) | 0 |
| Unit tests | ~119 | 240 |
| LOC removed | 0 | ~1,700 (via .n + .m + .o) |

**What remains for future arcs:**

- **Two document_findings tables** (schema.sql + schema_v9) —
  substantial refactor, own arc scope
- **ISO 27001:2013 → 2022 renumbering** (12 stale refs in source
  JSONs)
- **Deferred product items** (outbound notifications, UPDATES_FACT
  recompute, periodic sweep)
- **Cascade eid shape typing** (minor)
- **upload_id TEXT/UUID consistency** in intake_trace_log (minor)

**Related memories:**
- `[[ship-1-consensus-arc-2026-07-15]]` — the intent layer this
  arc composes with. Ship 2' is the answer-assembly layer; Ship 1
  is the intent-classification layer. Together: consensus →
  case-file digest → preservation-checked answer.
- `[[framework-role-model-arc]]` — the model Ship 2'.i aligned
  the digest with.
- `[[ship-2-prime-casefile-arc-2026-07-15]]` — Ship 2'.a-h detail.
- `[[ship-2-prime-i-id-discipline-and-digest-fix-2026-07-16]]` —
  Ship 2'.i detail (id_types + role model + anti-drift docs).

**Reversal path (any sub-arc):**
Every sub-arc is a single commit. `git revert <hash>` for any
single arc is surgical. There are no runtime flags to twiddle —
this was intentional (Ship 2'.n retired the last flag). The
whole arc can be reverted commit-by-commit from `e198c8b` back
to `f246df3` (the Ship 2 revert) if needed.

**End state:** the chat pipeline is a coherent stack. Intent is
consensus-classified with a bounded LLM arbiter (Ship 1). Answer
assembly is case-file → digest → preservation-check-repair (Ship 2').
Every ID has a typed home (Ship 2'.p). Legacy paths are gone.
Anti-drift discipline is codified. Baseline 207/208.
