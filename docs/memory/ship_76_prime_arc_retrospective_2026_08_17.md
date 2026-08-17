---
name: ship-76-prime-arc-retrospective-2026-08-17
description: "Ship 76' arc close-out (76'.a → 76'.f). Ship 66'.a introduced posture_controls.applicability_status as scope SSoT; Ship 66'.b/c/d enforced at 3 critical sites. Ship 76' extended enforcement to every posture-rendering surface: audit → SSoT predicate consolidation → 3 casefile leaks fixed → 3 API leaks fixed → CaseFileShim duck-type bug fix (76'.f, silent 161-fail regression). 4 codified lessons: SSoT-introduce ≠ SSoT-cascade, one rule with shape-appropriate call sites, deterministic prevention beats stochastic detection, duck-typed interfaces need shim mirroring. Cross-arc: Ships 66 → 76 mirror Ships 72 → 74 → 75."
metadata:
  type: project
  ship: "76'"
---

# Ship 76' arc close-out

Six sub-arcs (76'.a → 76'.f) across one working day (2026-08-17).
Extended Ship 66'.a's `posture_controls.applicability_status` SSoT
from 3 critical enforcement sites to every posture-rendering
surface. Case #5's rare stochastic "physical" trip is locked
deterministically. And one silent duck-type regression got caught
+ closed the same day.

Opens directly out of Ship 75'.f's investigation: user pushed back
on my initial "patch this one site" fix ("we are trying to make
sure there is only one truth"). The audit then revealed the
pattern was systemic — 6 LEAK sites, 1 FINDING-CHECK site — and
the arc scoped the exhaustive cascade.

## Sub-arcs

| Sub | What shipped | Files |
|-----|---|---|
| 76'.a | Audit + design doc. 6 LEAK sites catalogued + 1 FINDING-CHECK + 3 CLEAN. Design decisions D1-D6 locked (SSoT predicate + per-site policy + 404 semantics + opt-in flag). | `docs/memory/ship_76_prime_a_2026_08_17.md` |
| 76'.b | Promote `CaseFile.in_scope(ref)` as SSoT predicate + `rag/posture/scope.py` mirror helpers (4 entry points for different call shapes). Migrate 3 CLEAN sites + 1 FINDING-CHECK site. Zero behavior change — consolidation only. Eval: 232 PASS + 1 pre-existing WARN. | `rag/casefile/types.py`, `rag/casefile/digest.py`, `rag/posture/scope.py`, `rag/posture_loader.py`, `rag/posture/stage2_approval_chat.py` |
| 76'.c | Fix 3 casefile LEAK sites: `build_related_cards` soft filter (LLM-cited N/A refs render for grounding; auto-injected N/A drops), `_render_xfw_bridges` hard filter, `_render_demonstrated_by` hard filter. Case #5 stress test 50/50 clean, 0 physical leaks. **BUT** silently introduced a duck-type gap (see 76'.f). | `rag/casefile/answer_augment.py`, `rag/casefile/digest.py` |
| 76'.d | Fix 3 API LEAK sites: dashboard `/api/v1/dashboard/posture` (hard SQL filter), external `/posture` bulk (soft filter with `?include_na=true` opt-in), external `/posture/{ref}` detail (404 with structured error code `control_out_of_scope`). Dogfood: 4/4 endpoints correct. | `api_server.py`, `rag/external/endpoints/posture.py`, `rag/external/errors.py` |
| 76'.e | This retro (revised post-76'.f). | — |
| 76'.f | Fix silent duck-type regression from 76'.c. `build_related_cards` was migrated to call `cf.in_scope(ref)` but `CaseFileShim` (the duck-typed stand-in every short-circuit path uses) never got the mirror method → AttributeError silently swallowed by try/except → 161 Stage-2 chat cases (~70% of the suite) degraded to case-file flow. Add `CaseFileShim.in_scope()` — same rule (`applicability_status != 'na'`), one-line body. | `rag/casefile/answer_augment.py` |

## What shipped end-to-end

Before Ship 76':
- Scope SSoT `applicability_status` enforced at 3 sites only
  (engine-overlay guard, Stage-2 approval, digest OBLIGATIONS).
- 6 LEAK sites rendered N/A controls as if assessed on tenant-
  facing surfaces (chat "Related controls", digest xfw_bridges +
  demonstrated_by, dashboard heatmap, external API bulk + detail).
- 1 FINDING-CHECK site (`_rank_posture_refs`) used the legacy
  `finding == "N/A"` column check — worked today via data
  mirroring, but not the SSoT.
- Case #5's rare stochastic "physical" trip (documented in
  CLAUDE.md as a Ship 43'.a residual) actually surfaced this
  systemic gap.

After Ship 76':
- **One predicate** (`applicability_status != "na"`) implemented
  via 4 shape-appropriate entry points (`CaseFile.in_scope(ref)`,
  `is_ref_in_scope`, `refs_in_scope`, `row_in_scope`,
  `status_in_scope`). Every consumer that reads posture data
  applies the same rule via the appropriate shape.
- **6 LEAK sites closed.** N/A controls no longer surface as
  cards / bridges / demonstrators / heatmap cells / API rows.
- **1 FINDING-CHECK site migrated** to the SSoT predicate.
  Zero behavior change today; drift-proof going forward.
- **Case #5 locked deterministically.** Stress test 50/50 clean.
  The mechanism that could produce "physical" (A.7.2 auto-injected
  as demonstrator when Art.32 cited) is gone; the LLM has no
  N/A-primed surface to reference.
- **External API contract enhanced.** `?include_na=true` for
  auditors reviewing scope decisions; `control_out_of_scope`
  error code distinguishes "no such control" from "you scoped
  this one out."

## Design patterns locked

### Same predicate, different call shapes

`rag/posture/scope.py` exposes 4 entry points that all delegate to
the same rule. Different callers need different shapes:

```python
is_ref_in_scope(pg_conn, tenant_id, ref)   # no context — needs query
refs_in_scope(pg_conn, tenant_id, refs)    # batch query for a list
row_in_scope(row_dict)                     # caller has the row
status_in_scope(applicability_status)      # caller has the scalar
```

Plus `CaseFile.in_scope(ref)` for casefile-holding callers. The
scope check inside chat pipelines uses the `CaseFile` shape; the
loader uses row_dict; Stage-2 uses scalar; API endpoints use SQL
(via inline `applicability_status != 'na'` clause with a comment
pointing to the SSoT rule).

**Rationale**: one function name would either force every caller
to build up the arg shape it needs, or force the function to
handle every possible input shape internally. Multiple entry
points keep call sites clean; the SHARED RULE (the string
comparison) is what makes it SSoT, not a shared function name.

### Soft-filter grounding rule (Ship 66'.c → 76'.c generalized)

When an LLM voluntarily cites an N/A ref, we render it (with the
appropriate marker) so the mention has grounding. When a ref is
auto-injected via graph traversal / demonstrator overlay / cross-
role neighbor fetch, and it's N/A, we drop it.

Ship 66'.c applied this to the digest OBLIGATIONS section. Ship
76'.c generalized it to `build_related_cards`. The pattern:

```python
llm_narrative_refs = set(cited) | set(extras)  # LLM's actual + expected mentions
for ref in all_refs:
    if not cf.in_scope(ref) and ref not in llm_narrative_refs:
        continue  # auto-injected N/A → drop
    # else render (with N/A marker if applicable)
```

Not every surface needs this policy — hard filter is right for
dashboards + APIs where the surface is auditor-facing and there's
no LLM narrative to ground. Soft filter is right for chat prose
where the LLM has already committed to naming a ref.

### External API scope-out contract

- Detail endpoint: 404 with `control_out_of_scope` error code.
  "This control isn't in your scope" is a legitimate 404 from
  the partner's perspective — the resource doesn't exist for them.
- Bulk endpoint: default excludes; `?include_na=true` opt-in.
  Matches the OBLIGATIONS digest section's soft-filter policy at
  API layer. Auditors reviewing scope decisions have visibility;
  everyday callers see the assessed inventory only.
- Structured error code via message-marker heuristic in
  `rag/external/errors.py` (mirrors 401 `missing_api_key` sub-code
  pattern). Extending the error contract with a new sub-code is
  ~5 LOC.

## Codified lessons

3 new (54-56).

### 54. SSoT-introduce ≠ SSoT-cascade

Ship 66'.a introduced `posture_controls.applicability_status` as
the scope SSoT and Ship 66'.b/c/d applied it at 3 critical
enforcement points. That was strategic enforcement — the load
boundary, the Stage-2 approval gate, and the digest OBLIGATIONS
section. But every other consumer (RelatedCard builder, xfw
bridges, demonstrator overlay, dashboard, external API) still
read the underlying data blind to scope.

The gap was invisible until Case #5's rare stochastic failure
surfaced it. My initial "patch this one site" fix would have
added a fifth inline copy of the same predicate. User pushback
("only one truth") caught the SSoT violation before it happened.

**How to apply:** an SSoT introduction is not complete until
every consumer that reads the underlying data applies the rule.
An audit-and-cascade sub-arc closes the gap. If a rule you're
enforcing has fewer than N enforcement sites where N is the
number of consumers, either enforce it at every consumer OR
document the intentional carve-outs. Ship 66 → 76 is the pattern:
foundational schema arc + follow-up cascade arc.

### 55. One rule, shape-appropriate call sites

`rag/posture/scope.py` provides 4 entry points (query, batch,
row, scalar). Same rule, different arg shapes. Consolidating on
one FUNCTION NAME would force every caller to build up matching
args; consolidating on one RULE lets each caller use the shape it
already has.

The SSoT is the string comparison + the column name — not the
Python function. Callers with different data availability get
appropriate wrappers. New consumers that don't fit any existing
shape either use one of the wrappers with light adaptation, or
add a new entry point that delegates to the same rule.

**How to apply:** when consolidating a predicate across N call
sites with different arg shapes, expose N entry points that share
implementation, not one entry point that forces every caller into
one shape. The "one truth" claim applies to the RULE, not the
function.

### 56. Deterministic prevention beats stochastic detection

Case #5's rare "physical" trip could have been "fixed" by adding
a post-answer forbidden-phrase check that stripped "physical"
retroactively. That would have been detection + repair — same
category as the preservation-check pattern (Ship 6'.c).

Ship 76'.c chose prevention instead: remove the mechanism that
lets A.7.2 into the answer at all. A.7.2 no longer appears as a
demonstrator card when Art.32 is cited on a cloud tenant. The
LLM has no primed surface to reference; "physical" can no longer
appear voluntarily.

50/50 stress test clean. Not "232/233 with 1 rare fail;" 233/233
deterministic.

**How to apply:** when facing a rare stochastic failure, prefer
removing the mechanism that produces it over detecting +
repairing the output. Detection has recall gaps by construction;
prevention has zero. The Ship 6' preservation-check pattern is
still right for cases where prevention isn't feasible; but when
prevention IS feasible (the failure has a specific mechanism you
can close), close it.

### 57. Duck-typed interfaces need shim mirroring

When adding a method to a class that has a duck-typed stand-in
(shim, mock, adapter, subclass hierarchy), grep for stand-in
implementations before considering the change complete. If they
share an interface with the primary class, they need the same
method — or the change silently breaks callers that receive the
stand-in shape.

**How Ship 76'.f manifested**: 76'.c added `cf.in_scope(ref)`
inside `build_related_cards` in `answer_augment.py`. That function
is duck-typed: callers pass either a real `CaseFile` (from the
LLM chat path) or `CaseFileShim` (from every short-circuit path —
Stage-1, Stage-2, Acknowledge, Topic-bundle, Risk, Documents).
The Shim implements 4 of the 5 methods `build_related_cards` uses.
I added a 5th to the interface without adding it to the Shim.

Short-circuit paths threw AttributeError → the per-block
`try/except` at `arion_graph.py:2880` etc. logged a warning and
fell through to case-file flow. The queries got a plausible-
looking generic answer instead of the deterministic Stage-2
response. 161 eval cases silently degraded — 70% of the suite —
until the full-suite eval fired.

**How the bug hid**: individual verification steps couldn't see
it:

  - 76'.b eval: PASS (didn't add any `cf.in_scope()` call sites
    yet — Shim gap wasn't exercised).
  - 76'.c case #5 stress test: PASS 50/50 (case #5 uses the
    case-file flow, not short-circuits — Shim gap wasn't
    exercised).
  - 76'.d dogfood: PASS 4/4 (API endpoints, not chat short-
    circuits — Shim gap wasn't exercised).
  - Full-suite eval after 76'.d: 161 FAIL.

Each of the individual checks was correct for what it tested;
the interface asymmetry only became visible when the full suite
exercised the paths that use the Shim.

**How to apply:**

1. When adding a method to a duck-typed interface, grep for
   `Shim`, `Mock`, `Stub`, `class.*Duck` in the same directory
   family before you commit. If a stand-in exists, either add the
   method there or make the call optional (`getattr(cf, "in_scope",
   default_impl)`) with an explicit reason.
2. Silent try/except in short-circuit paths hides bugs. When
   graph nodes are wrapped in exception handlers for
   "resilience," any AttributeError from an interface change gets
   swallowed. If you make an interface change, temporarily remove
   or narrow the surrounding except-clauses to surface the
   AttributeError before shipping.
3. Full-suite eval before commit is the last line of defense.
   The stress test + dogfood answered questions about the
   changed code; the full suite catches the code the change
   didn't cover. Ship 76' had a window where I moved from
   76'.c → 76'.d without running the full suite in between;
   that window is where the Shim gap ran undetected.

### Reinforced: 48 ("automatically" claims need runtime proof)

Ship 76' arc's 76'.c commit could have said "case #5 will pass
now." Instead: 50-iteration stress test with DB-verified physical
counts. Same shape as Ship 74'.a's runtime SELECT after
schema_v98 — the retro claim is paired with runtime evidence, not
just a code walkthrough.

But lesson 57 is the flip side: runtime evidence for ONE claim
doesn't cover unrelated regressions. 76'.c had solid case #5
evidence + a silent 161-fail regression at the same time.

## What broke and how it got caught

Post-76'.c code shipped clean by every metric I was measuring:

- `test_finding_contract.py`, Ship 74' guards, all 5 Ship 75'
  regression tests: green.
- Case #5 stress test: 50/50 clean.
- Ship 76'.d API dogfood: 4/4 correct.

Then Ship 76'.d fired the full eval → 71 PASS / 161 FAIL / 1 WARN.
Massive regression pattern: 158 of 161 fails were `pending engine
verdict for Art.X` queries + 3 adjacent Stage-1 chat queries.

Root-cause chain:

1. Live curl of `pending engine verdict for Art.44` → case-file
   flow output ("GDPR Art.44 (General principle for transfers)
   requires...") instead of Stage-2 short-circuit
   ("Art.44: engine verdict 'NC' already approved...").
2. Direct call `parse_stage2_intent(query)` → returns intent
   correctly. So the Stage-2 block WAS reachable + the intent
   parser worked.
3. Instrumented arion_graph.py:2813 with debug log →
   `STAGE2_DEBUG intent=Stage2Intent(action='list_one', ...)` —
   confirmed intent detected.
4. Instrumented line 2848 with debug log →
   `STAGE2_DEBUG_ANSWER len=65` — confirmed the Stage-2 handler
   generated the correct answer text.
5. So the answer was correct but the client got case-file prose
   → something between the answer generation + `return
   build_answer_envelope(...)` was throwing.
6. `build_answer_envelope` calls `build_short_circuit_structured`
   which calls `build_related_cards(cf, ...)` — my Ship 76'.c
   added `cf.in_scope(ref)` there.
7. Grep for CaseFileShim → confirmed it duck-types 4 methods but
   not `in_scope`. Every short-circuit path was throwing
   AttributeError. The try/except was catching it silently.

Fix: add `CaseFileShim.in_scope()` — same rule, one-line body.
Verified live: case #5 still 0/0 physical leaks; Art.44 now
returns the Stage-2 response.

**Cost of the miss**: ~90 minutes to diagnose + fix. The bug
existed for ~2 hours between the 76'.c code write and the
diagnosis.

## What's parked

- **Case #200 still WARN** (posture_check vs gap_analysis
  routing on "NC findings on identity"). Documented in CLAUDE.md
  as pre-existing since Signal C doesn't fire on this phrasing.
  Own arc — not scoped for Ship 76.
- **[[revisit consensus vs critic-verifier]]** (parking-lot from
  Ship 76' priming session). User surfaced at open of 76'.a;
  needs its own scoping session.
- **Notification producers audit.** Ship 76' audit focused on
  posture-rendering surfaces. Notification producers
  (`rag/notifications/*`, `rag/cascade/notify.py`) also read
  posture data but weren't in the audit scope. May have latent
  N/A leaks in notification kinds like `posture_flip_to_comply`.
  Micro-arc candidate.
- **Dashboard scope-out summary verification.** 76'.a Risk 2
  noted the heatmap change is mitigated by the scope-out summary
  panel elsewhere. Verify that panel is still complete post-76'.d.

## Session shape

Standard audit → design → migrate-per-surface → retro cadence,
same as Ships 74 + 75. Trigger: user pushback on my initial fix
approach for case #5. That pushback caught an SSoT violation
before it happened; the resulting arc scoped the exhaustive fix.

Cross-arc pattern locked. Two arc families now:
- **Ships 72 → 74 → 75**: FindingContract SSoT (contract) →
  observability (silent-drop guards) → coverage (every extractor)
- **Ships 66 → 76**: applicability_status SSoT (schema) →
  cascade (every renderer)

Same shape: SSoT introduced with strategic enforcement, follow-up
arc completes cascade across every consumer. Each arc's
foundation earns the next arc's reach.

## Codified lesson candidate for the next SSoT-family arc

**When introducing an SSoT, plan the cascade arc from day zero.**
Ship 66'.a introduced the schema column; Ship 76' arrived 5 days
later to finish the cascade. That gap wasn't planned — it took
Case #5's stochastic failure to surface. If Ship 66 had shipped
with a "cascade audit pending" task recording every consumer that
needed migration, the gap would have been visible from day one.
Not a hard rule (some cascades legitimately wait for the
enforcement pattern to prove out); but for schema SSoT introductions,
the cascade should be a companion task at the outset.

## Numbers

- **6 LEAK sites closed**: build_related_cards, _render_xfw_bridges,
  _render_demonstrated_by, dashboard/posture, external /posture
  bulk, external /posture/{ref} detail.
- **1 FINDING-CHECK site migrated**: _rank_posture_refs.
- **5 SSoT predicate entry points** (one rule):
  CaseFile.in_scope, CaseFileShim.in_scope (added 76'.f),
  is_ref_in_scope, refs_in_scope, row_in_scope, status_in_scope
  (+ implicit SQL inline).
- **Case #5 stress test**: 50/50 clean, 0 physical leaks.
- **API dogfood**: 4/4 endpoints correct behavior verified.
- **Eval baseline preserved** post-76'.f (232 PASS + 1
  documented WARN).
- **Silent regressions caught + fixed same day**: 1 (76'.f,
  duck-type interface asymmetry).
