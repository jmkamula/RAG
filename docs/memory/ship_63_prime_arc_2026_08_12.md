---
name: ship-63-prime-arc-2026-08-12
description: "Ship 63' — CI grep guards + Evidence Package snapshot tests. Two tight guards for patterns Ships 60'.k + 60'.b root-caused; 5 snapshot cases covering the Ship 61'/62' hybrid Evidence Package render on the demo tenant."
metadata:
  type: project
  ship: "63'"
---

# Ship 63' — CI grep guards + Evidence Package snapshot tests

## The arc in one sentence

Ship 63' closes the durable-quality debt from Ships 60-62: two
tight CI grep guards against patterns we've root-caused +
5 snapshot tests covering the Evidence Package's Ship 61'.a/62'
hybrid render on the Arion demo tenant.

## What's in the arc

### CI grep guards — `scripts/ci/check_forbidden_patterns.sh`

Two guards where the pattern has a canonical location and any
new occurrence is a genuine regression:

1. **Naive `if ref in answer:` in `forbidden_refs` loop** —
   Ship 60'.k root-caused the "stochastic physical-leak" eval FAIL
   to a substring collision (`A.7.1` inside `A.7.1.5` on a 27701-
   enrolled tenant). The correct pattern uses `re.search(re.escape(
   ref) + r'(?!\.\d)', answer)`. The guard walks
   `tests/eval_suite.py` looking for a `if ref in answer:` line
   within a two-line window of the `for ref in case.forbidden_refs:`
   loop header (via awk). Only fires on the load-bearing loop, not
   every substring check in the file.

2. **Direct `evaluate_one_control()` outside allowlist** — Ships
   58/60/61 consolidated per-MUST fulfilment on
   `rag.posture.must_verdicts.read_must_verdicts_by_control`. New
   callers should read SSoT. Allowlist:
   - `rag/posture/engine_runner.py` (owner)
   - `rag/posture/advisory.py` (Ship 60'.b legacy fallback)
   - `api_server.py` (Stage-2 detail UI — evaluate_one_control's
     documented intended user per its docstring)
   - `scripts/**` (audit + repro)
   - `tests/**` (fixtures + assertions)

The broader disciplines (hardcoded model strings, uncoordinated
`document_findings` reads, direct `openai` SDK imports) are
documented in `docs/memory/` but not enforced here — the false-
positive rate on those grep patterns is too high to be actionable
in CI. Enforcing them would push the check toward "warn on new
violations only" which needs a baseline and adds drift.

**Regression check** — the guards were verified by:
- Injecting `if ref in answer:` under the forbidden_refs loop →
  guard fires with the exact line + filename.
- Reverting to clean state → guard exits 0.

Ship 63' also codifies the rule: two tight guards + a memory file
beats five noisy guards. See lesson 23 below.

### Evidence Package snapshot tests — `tests/test_evidence_package.py`

Runs against the Arion demo tenant since it's the reference
deployment with SSoT + `document_findings` both populated. Skips
cleanly if Postgres isn't reachable (dev laptop without the demo
DB). Plain-Python style matching the existing test module
convention (`python3 tests/test_X.py`), no pytest dependency.

5 cases lock in:
1. `test_bridged_leaf_shows_cross_framework_header` — Art.32:
   program_review renders `**Status:** Partially covered` +
   `**Cross-framework coverage:**` + `ISO 27001:2022` +
   `controls (see below).` Header. Required-elements section has
   ≥1 `- ✓` (direct), ≥1 `- ↗` (bridged), and `↳ Covered via _`
   attribution lines.
2. `test_bridged_leaf_dedupes_source_excerpts` — Ship 62' dedup
   locks: A.5.18 covers multiple bridged Art.32 MUSTs, but the
   verbatim excerpt appears exactly once. Every later reference to
   A.5.18 in the same package is collapsed to
   `source excerpt shown under _ISO 27001:2022 A.5.18_ above`.
   Assertion: `n_pointers == n_covered_via - 1`.
3. `test_fully_satisfied_leaf_renders_no_bridge_header` — A.5.15:
   management_approval is 3/3 direct-satisfied; no cross-framework
   header should render (`n_must_bridged == 0`); every MUST is ✓.
4. `test_fresh_tenant_fallback` — SSoT-empty path: package builds
   without crash, missing MUSTs render as ✗ via the pre-Ship-61'.a
   findings-only heuristic, cross-framework header suppressed.
5. `test_missing_leaf_returns_none` — un-cataloged leaf id returns
   `None`, not empty markdown / not a crash.

All 5 pass on Arion demo.

## Codified lessons

### 23. Two tight guards beat five noisy ones

Initial Ship 63' sketch included five grep guards (naive substring,
`evaluate_one_control`, direct `openai` imports, hardcoded model
strings, raw `document_findings` SQL). Three of those fired on
40+ legitimate hits — every dev workflow would get numb to the
failures. Ship 63' pared to two guards where the pattern has a
canonical location + false-positive rate of zero. The broader
disciplines are documented but not CI-enforced.

Rule: guards must have zero false positives, or devs will normalize
ignoring them. When you can't scope a guard tightly enough, prefer
a memory entry over a "warn only on new violations" mechanism —
baselines rot faster than the rules they encode.

### 24. Snapshot tests against a real fixture beat mocked units

Building fixtures for `posture_must_verdicts` + `posture_must_
bridge_coverage` + `document_findings` + Neo4j leaf structure in
isolation would take longer than the code under test. Ship 63'
uses the Arion demo tenant as a fixture — it's already up-to-date
via the sweep, exercises the whole stack, and any drift in the
demo data surfaces immediately. Trade-off accepted: tests won't
run without the demo tenant available; skipped cleanly instead of
failed spuriously.

Rule: for integration-shaped code (SSoT read + Neo4j + rendering),
snapshot against real fixture data if one exists. Isolating each
layer for pure unit tests inverts the effort/coverage ratio.

## What Ship 63' costs to reproduce

- Schema migrations: 0
- Wall clock: ~45 minutes (design + implement + refine to tight
  scope + snapshot cases + retro)
- Files touched: 3 (`scripts/ci/check_forbidden_patterns.sh` NEW,
  `tests/test_evidence_package.py` NEW, retro doc)
- Lines: ~250 (guard script + tests + retro)
- Eval regression: n/a — no product behavior changed.

## Follow-ons deferred

- Broader disciplines (hardcoded model strings, direct `openai`
  imports, uncoordinated `document_findings` reads) documented in
  their originating retros but not CI-enforced. Culture + code
  review own them.
- Adding snapshot tests for `build_per_must_advisory_data` +
  `build_evidence_class_breakdown` on the same fixture pattern —
  didn't ship this arc but the fixture idiom is ready to reuse.
