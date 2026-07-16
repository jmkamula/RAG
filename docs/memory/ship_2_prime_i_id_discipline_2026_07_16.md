---
name: ship-2-prime-i-id-discipline-and-digest-fix-2026-07-16
description: "Ship 2'.i (2026-07-16) — introduces rag/id_types.py (TenantUUID / NodeId / ControlRef / LeafId as validating-at-construction str subclasses); fixes arion_state.py:89 (tenant_id was the display name); ROLE-AWARE digest replacing the primary/xfw layer split (aligned with framework-role-model-arc). Adds Read-the-arc-first table + Legacy-do-not-extend section to CLAUDE.md as codified discipline against drift."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 2'.i landed 2026-07-16. Three concerns addressed together,
plus a codified anti-drift discipline in CLAUDE.md.

**Q1 (tenant_id sprawl)** — audit-driven fix. Post-Ship-2'.h eval
surfaced that `chat_casefile_log` had ZERO rows even though the case-
file path executed for every eval turn. Root cause: `arion_state.py:89`
was setting `state["tenant_id"] = tenant.name` (the DISPLAY NAME).
Downstream writers cast to `::uuid` and silently failed inside best-
effort try/except blocks. My initial Ship 2'.f/g/h wiring papered
over it with an explicit `tenant_id` kwarg + `_is_uuid_shape()` band-
aid; Ship 2'.i fixes the root.

**Q2 (definition-query regression)** — same eval surfaced 5 new fails
in the definition family (#15, #22, #23, #213, #214). Root cause was
compound: (1) digest POSTURE section led over OBLIGATIONS, biasing
LLM toward listing findings; (2) 160-char obligation cap chopped mid-
sentence before key words; (3) `xfw_edges` was the primary/xfw
discriminator, misclassifying an ISO control with GDPR bridges as xfw
and dropping it from OBLIGATIONS; (4) `gap_description` carried
engine jargon ("0/4 children satisfied") straight into the LLM prose.

**Q3 (primary/xfw split is a legacy artifact)** — mid-session review
against [[framework-role-model-arc]] (2026-07-05) revealed that the
primary/xfw layer split is deprecated. Every enrolled standard has
a role: **program** (ISMS spine — ISO 27001), **extension** (PIMS
overlay — ISO 27701), **obligation** (regulatory — GDPR, NIS2).
Obligation postures are partly materialised from PROGRAM/EXTENSION
demonstrators (Phase 2b/2c). Splitting on "primary/xfw" fights this
model. Ship 2'.i retires the split from the case-file flow:
- CaseFile: new `role_of(ref)`, `demonstrated_by(ref)`,
  `obligations_of_role(role)` accessors. `xfw_bridges()` iterates
  `all_nodes()`, not `xfw_nodes()`. `primary_nodes()` /
  `xfw_nodes()` kept as backward-compat but marked LEGACY.
- Digest: role-aware section layout. OBLIGATION cited → DEMONSTRATED
  BY leads. PROGRAM/EXTENSION cited → OBLIGATIONS+POSTURE default.
  New FRAMEWORKS ENROLLED section makes the enrolled-standards
  hierarchy visible to the LLM (programs / extensions / obligations
  grouped).
- System prompt: retires the "Layer 2 inherits" wording. Replaced
  with role-aware guidance: OBLIGATION refs get posture partly from
  DEMONSTRATED BY; PROGRAM/EXTENSION refs carry direct posture.
- `_pick_primary_std` in llm_answer.py retired from classification
  (still exists inline in the legacy `rank_and_answer` path, which
  itself is scheduled for retire-by 2026-08-15).

**Anti-drift discipline** — codified in CLAUDE.md 2026-07-16:
- "Before touching module X, read arc Y" table — before working on
  multi-framework code, tenant-id handling, chat routing, or
  digest/casefile paths, load the referenced arc doc FIRST. Prevents
  rebuilding legacy patterns on top of an already-superseded model.
- "Legacy — do not extend" section — enumerated anti-patterns with
  retire-by dates. Each pattern that's been superseded (layer split,
  `_is_uuid_shape` band-aid, `node_id.split(":")`, AnswerPayload
  dispatcher, etc.) is listed so a grep of the diff catches new
  extensions. When a retire-by date passes, delete the legacy path.

**Why to apply going forward:**

1. **Use `rag/id_types.py` for new code.** `TenantUUID(value)` raises
   ValueError at construction if the input isn't UUID-shaped. Same
   for `NodeId`, `ControlRef`, `LeafId`. Retire the pattern of
   validating shape only at write time.

2. **Naming rule (see CLAUDE.md):** if a field is called `X_id`, it
   MUST be the canonical UUID. Display names → `X_name`. Slugs →
   `X_slug`. Composite refs → `X_ref` or `X_node_id`. Enforced at
   review time.

3. **Primary/xfw split in rank_and_answer must use `standard_id`**,
   not `xfw_edges`. An ISO control with GDPR bridges is still primary
   from the tenant's perspective — the bridges make it cross-
   referenced, not cross-framework.

4. **Digest section budgets shift by intent** — DEFINITION /
   STANDARD_KNOWLEDGE queries get OBLIGATIONS-first + 400-char
   excerpts + trimmed POSTURE (3 items × 80 chars). This is soft
   branching in `_plan_for(cf)` — no per-taxonomy dispatch table.
   Adding a new intent means adding one entry to `_DEFINITION_INTENTS`
   or extending `_plan_for`, nothing more.

5. **Sanitize engine jargon at the digest boundary**, not at write
   time. `_sanitize_gap_text` in `rag/casefile/digest.py` — same
   principles as the [[dejargonize-ux-pass-2026-07-01]]. The repair
   pass footer (`_compliance_facts_footer`) uses the same
   sanitizer.

**Migration strategy for id_types:** opportunistic. Use in NEW code,
migrate old sites when touched. Not a big-bang refactor.

**Deferred to Ship 2'.j (pre-external-API launch):**
- FastAPI `pydantic.UUID4` typing on all path/body ID params (returns
  400 before Postgres does — currently 500 via `::uuid` cast).
- Shared `parse_node_id` helper to retire the 14 `.split(":")` sites
  documented in the ID audit.
- Validate `session_id` against caller's tenant.

**Component map:**
- `rag/id_types.py` — TenantUUID / NodeId / ControlRef / LeafId
- `rag/arion_state.py:89` — `tenant_id = TenantUUID(tenant.tenant_id)`
  + separate `tenant_display_name` field
- `rag/arion_graph.py` — call site now passes `tenant_id` +
  `tenant_display_name` correctly
- `rag/casefile/digest.py` — `_plan_for(cf)`, `_sanitize_gap_text`,
  intent-aware `build_prompt_digest`
- `rag/casefile/repair.py` — `_compliance_facts_footer` uses
  `_sanitize_gap_text`
- `rag/llm_answer.py` — primary/xfw split uses `standard_id`;
  `_is_uuid_shape` retired in favour of `id_types.is_uuid`
- `chat.py` — fallback fixture uses UUID (was slug)
- `CLAUDE.md` — object-id discipline section

**Related memories:**
- `[[ship-2-prime-casefile-arc-2026-07-15]]` — Ship 2'.a–h that
  introduced the case-file pattern.
- `[[feedback-eval-with-each-feature]]` — 12 new eval-shape unit
  tests added.
- `[[dejargonize-ux-pass-2026-07-01]]` — the jargon-sanitization
  principle Ship 2'.i extends to the digest boundary.

**Reversal:** setting `CASEFILE_ENABLED=0` disables the whole case-
file path (unchanged from Ship 2'.h). The id_types + arion_state.py
fixes are permanent (Ship 2'.i doesn't gate them on the flag) since
they benefit all downstream writers regardless of digest path.
