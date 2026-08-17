---
name: ship-75-prime-arc-retrospective-2026-08-17
description: "Ship 75' arc close-out (75'.a → 75'.e). Deterministic-path FindingContract migration complete. Ship 72'.a routed the LLM extractor through FINDING_CONTRACT.bind(); Ship 75' extended the same SSoT to the fingerprint / consensus / critic-verifier paths. Every extractor now uniformly protected by the contract's 4 skip-reason gates. 3 codified lessons: (51) per-path sub-arc + mirrored regression test scales linearly; (52) design invariants preserved during migration (null-item_id pass-through by intent); (53) audit → design → migrate one-at-a-time cadence outperforms bulk refactor."
metadata:
  type: project
  ship: "75'"
---

# Ship 75' arc close-out

Five sub-arcs over ~24 hours (2026-08-16 evening → 08-17 morning).
Extended Ship 72'.a's FindingContract SSoT from the LLM path to
all three deterministic extractor paths (fingerprint, consensus,
critic-verifier). Every extractor now uniformly protected by the
contract's `EMPTY_TEXT` / `PURE_SCAFFOLDING` / `MANGLED_ITEM_ID` /
`UNRESOLVABLE_REF` gates.

Opens directly out of Ship 74's silent-drop hygiene work: with
Ship 74'.b/c enforcing tracer symmetry + producer forwarding, the
next natural gap was "the LLM path is the only extractor that
runs its findings through a shared contract; the others construct
DocumentFinding directly." Ship 75' closes that gap.

## Sub-arcs

| Sub | What shipped | Files |
|-----|---|---|
| 75'.a | Audit + design doc. Located each deterministic path's construction point (fingerprint:3518, consensus:362, critic:546), mapped their fields to `ExtractedCandidate`, identified friction (critic derives `standard_id` post-hoc from priming/pool). Decided: no new SkipReasons this arc, gates stay upstream of bind(), one path per sub-arc. | `docs/memory/ship_75_prime_a_2026_08_17.md` |
| 75'.b | Fingerprint path migrated. Simplest — all fields provided directly. Regression test at `test_fingerprint_contract_wiring.py`. Template for the remaining migrations. | `rag/intake/extractor.py`, `tests/test_fingerprint_contract_wiring.py` |
| 75'.c | Consensus path migrated. Mirrors 75'.b shape; fields harvested from aggregator's fingerprint_keyword signal metadata. | `rag/intake/extractor.py`, `tests/test_consensus_contract_wiring.py` |
| 75'.d | Critic-verifier path migrated. Standard_id derivation kept inline just above the ExtractedCandidate construction. Upstream gates (grounding + shape + semantic-fit) preserved. Regression test locks + 4th case for null-item_id pass-through. | `rag/intake/extractor.py`, `tests/test_critic_verifier_contract_wiring.py` |
| 75'.e | This retro. | — |

## The migration shape

Each path's migration was structurally identical:

```python
# Before
findings.append(DocumentFinding(
    upload_id=..., control_ref=..., standard_id=...,
    evidence_text=quote, checklist_item_id=must_id,
    extraction_path="<path>",
    ...
))

# After
from rag.intake.finding_contract import FINDING_CONTRACT, ExtractedCandidate
candidate = ExtractedCandidate(
    item_id=must_id, excerpt_text=quote,
    control_ref=..., standard_id=...,
    extraction_path="<path>",
    source_context={"path": "<path>", ...},
    ...
)
bind_result = FINDING_CONTRACT.bind(candidate, metrics=doc.extraction_metrics)
if bind_result.finding is not None:
    findings.append(bind_result.finding)
```

Every case where the pre-migration code post-conditioned on emit
(e.g. `covered.add(m["leaf_id"])` in the fingerprint path) moved
inside the `if bind_result.finding is not None:` branch — a
leaf whose only match was scaffolding really isn't covered.

## Test shape

Same pattern across all three regression tests:

- **Substantive quote → binds + emits.** Real MUST id, non-scaffolding
  text. Assert 1 finding, correct fields, no `contract_skip_*`
  counter increment.
- **Scaffolding quote → drops + counter.** Well-known scaffolding
  shape (`▽ Standard text ▽`). Assert 0 findings,
  `contract_skip_pure_scaffolding=1`.
- **Mangled item_id → drops + counter.** Deliberately-fake catalog
  id. Assert 0 findings, `contract_skip_mangled_item_id=1`.

Critic path added a 4th case:
- **Null checklist_item_id → passes through.** By intentional
  design (`finding_contract.py:321`), empty item_id skips the
  catalog check so the LLM path's own null-binding gate can
  handle it. Locked as-behavior.

Each test bypasses upstream infrastructure via targeted
`unittest.mock.patch` — different scaffolding per path, but the
end shape is the same three assertions.

## Design decisions codified

### D1 — bind() sits AFTER extractor-specific gates

Fingerprint has specificity threshold + content-shape filter.
Critic has grounding + content-shape + semantic-fit. Consensus
has verdict aggregation + no-excerpt-auto-drop invariant + LLM
arbiter. All those stay in place, upstream of bind(). The
contract's 4 reasons are additive safety net, not replacements.

Rationale: extractor-specific gates capture path-specific
knowledge ("fingerprint over-firing token sets," "critic quote
grounded in body"). They aren't universal skip-reasons. The
contract's reasons are: adversarial input class caught once,
enforced everywhere.

### D2 — no new SkipReason values in this arc

The audit found no path had a rejection class not already
covered by the 4 existing SkipReasons. Every deterministic path
either accepted the migration cleanly or needed a small field-
plumbing fix (critic's `standard_id`).

If a future arc surfaces a new class (semantic-fit-below-threshold
as a first-class skip, evidence-quote-too-short as a first-class
skip), that arc grows the enum. Ship 75' inherits the current
shape.

### D3 — null item_id passes through by design

Discovered during 75'.d test authoring: `bind()` at line 321
explicitly guards the catalog check with `if candidate.item_id
and not catalog_recognises(candidate.item_id):`. An empty
item_id skips the check because the LLM path's own gate
(`bound_item_id is None` in `_extract_llm_findings_from_chunk`)
handles null-binding rejection before bind() runs.

Critic path preserves that behavior post-migration. If we later
want to tighten null-item_id acceptance across all paths, that's
a `bind()` change — affects every extractor uniformly. Correct
place to enforce a policy that applies to every extractor.

### D4 — one path per sub-arc, dogfood + eval per migration

Ship 74'.b caught a real pre-existing bug on its first-run
guard. Every deterministic-path migration got its own regression
test dogfood; each test uncovered small behavior details (real
catalog IDs required for substantive-quote cases, empty-item_id
design invariant). Batching the migrations would have obscured
those details.

## Codified lessons

Adding 3 new (51-53).

### 51. SSoT migration scales linearly with per-site sub-arcs + mirrored tests

Ship 72'.a wired the contract at 6 LLM/templated call sites in
one arc. Ship 75' extended it to 3 deterministic paths across 3
sub-arcs, one per path. Each sub-arc took ~20 minutes: 2 minutes
to read the current construction, 3 minutes to write the migration
edit, 10-15 minutes to write + debug the regression test.

The mirrored test shape (substantive / scaffolding / mangled)
worked for every path — the specifics of what "substantive" and
"mangled" look like changed per path, but the three-case
structure was invariant.

**How to apply:** SSoT extensions across N call sites should be
scoped as N sub-arcs, not one refactor arc. Each sub-arc includes
a regression test built from the same shape; the shape becomes a
template. Diverges only when a path has a genuinely different
failure mode (75'.d's 4th test for null-item_id).

### 52. Preserve behavior during migration; policy changes are separate arcs

Ship 75' had two chances to tighten null-item_id acceptance
(75'.b, 75'.d) and both times deferred it. Reasoning: the null-
item_id pass-through is a documented design (`finding_contract.py:
321`). Changing it during a migration arc would conflate two
different intentions — "extend the SSoT" vs "change what the SSoT
accepts."

Migrations that only extend the reach of existing rules are
straightforward. Migrations that quietly change what rules apply
where are landmines. Test 3 in the critic path locks the current
behavior explicitly; a future arc that wants to change it will
land as a bind() edit + this test flipping — both intentional.

**How to apply:** when a migration surfaces a "we could tighten
this while we're here" opportunity, resist the urge. Ship the
migration cleanly; open a separate arc for the tightening. The
migration retro should record the discovered behavior so the
follow-on arc has context.

### 53. Audit → design → migrate one-at-a-time outperforms bulk refactor

Ship 75'.a's audit produced concrete file:line pointers for every
migration site + a small sub-arc plan. Ship 75'.b-d each landed
in ~20-30 minutes with high confidence because the audit had
already answered the "what field goes where" questions.

Contrast with a bulk-refactor approach: read all three sites in
one PR, change all three at once, hope the tests catch anything
that went sideways. Per-path staging surfaces divergences (75'.d
required standard_id plumbing that 75'.b/c didn't; 75'.d's null-
item_id case triggered a design-intent discovery). Bulk refactor
would have papered over both.

**How to apply:** an SSoT migration touching >1 call site earns
an audit sub-arc even if the migration itself is small. The
audit's concrete file:line inventory + friction notes drive the
sub-arc plan; the sub-arcs execute against it deterministically.

## What's parked

- **Templated LLM path's ExtractedCandidate is field-tighter**
  than the deterministic ones — its `source_context` includes
  `chunk_id` explicitly. Deterministic paths' `source_context`
  is more sparse (path + leaf_id or path + bucket). Not a bug —
  intentional per-path context — but a future observability arc
  might unify the shape.

- **Consensus telemetry writer** (`consensus_extraction/log.py`)
  runs INSIDE `_extract_via_consensus`, after the accepted
  verdicts are materialised. If bind() drops a candidate the
  aggregator accepted, the telemetry log's `n_accept` count no
  longer matches the emitted findings count. Small observability
  drift; document in the log writer or add a `n_bind_rejected`
  field. Micro-arc.

- **Critic-verifier's null-item_id pass-through** — locked as a
  design invariant (test 3 in 75'.d). If a future arc wants to
  tighten this, the natural home is `finding_contract.py:321`
  (affects all paths uniformly). Documented in that test's
  docstring.

- **75'.b eval landed 231/233 PASS, 1 FAIL (case #5).** Case #5
  tripped on `FORBIDDEN phrase present: 'physical'`. CLAUDE.md's
  Ship 43'.a stabilization note documents this as a "rare" residual
  from the LLM voluntarily invoking logical-vs-physical scope framing,
  even though `tenant_must_overrides` marks A.5.15:physical_rules as
  N/A for cloud-only Arion. **Actual observation**: case #5 has been
  PASSing across every recent eval on disk (74'.a, 74'.b, 72'.d,
  73'.b, 20260811, 20260810). Ship 75'.b eval was the first FAIL in
  the recent record. Post-hoc re-runs (4 consecutive) all PASS.
  Ship 75'.b's code change touches only the intake fingerprint path,
  which doesn't participate in chat query answering — so a
  regression mechanism would have to run through the intake module's
  import side-effects. No such path identified. Verdict: rare
  stochastic firing of the documented residual, not a 75' regression.
  Baseline 223/226 → 233 gives comfortable headroom at 231/233. Also
  a codified lesson for me — leaning on a stability note without
  checking recent eval history is a mistake; the note describes what
  CAN happen, not what IS happening.

## Session shape

Cadence: audit (75'.a) → migrate one path + test (75'.b) →
migrate next path + test (75'.c) → migrate hard path + test
(75'.d) → retro (75'.e). Same shape as Ship 74's silent-drop
class fix (74'.a fix instance + 74'.b/c guards + 74'.d promote).

Both arcs share a theme: **extending an SSoT from one enforcement
point to every enforcement point.** Ship 74 did it for the trace
column set; Ship 75 did it for the extractor emit path. The
pattern is: audit-then-migrate-per-site, one sub-arc per migration
target, mirrored regression tests.

Cross-arc lesson: Ships 72 → 74 → 75 form a coherent SSoT arc
family. Ship 72 introduced the FindingContract; Ship 74 added the
observability layer that lets us prove the contract's decisions
are landing; Ship 75 extended the contract's reach to every
extractor. Each ship's foundation earned the next one's coverage.
