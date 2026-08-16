---
name: ship-74-prime-arc-retrospective-2026-08-16
description: "Ship 74' arc close-out (74'.a → 74'.e). Silent-drop class closed end-to-end: 74'.a persisted FindingContract counters that Ship 72'.d retro falsely claimed already landed; 74'.b/74'.c added two durable AST-based guards preventing recurrence; 74'.d promoted 18 previously-invisible high-value counters. Two schemas (v98/v99/v100), 5 files changed, 3 new codified lessons."
metadata:
  type: project
  ship: "74'"
---

# Ship 74' arc close-out

Five sub-arcs over one session (2026-08-16). Started as a single
"forward the counters" fix; expanded into a class-of-bug hunt when
the initial fix uncovered a durable pattern that had bitten before
and would bite again.

Opens directly out of Ship 73'.c's dogfood, which surfaced the
observability gap Ship 72'.d retro had wrongly declared closed.

## Sub-arcs

| Sub  | What shipped | Files |
|------|---|---|
| 74'.a | Persist 6 FindingContract counters to `intake_trace_log`. schema_v98 + `tracer.write()` allowlist entries + extract-stage kwarg forwarding. Root-cause: allowlist filter silently drops unknown kwargs — Ship 72'.a missed BOTH the allowlist AND the forwarding. | `db/schema_v98_*.sql`, `rag/intake/doc_pipeline.py` |
| 74'.b | Static AST-based guard asserting every `tracer.write()` kwarg is in the allowlist. Caught a real pre-existing bug on first run: `dup_of_upload_id` was passed at the duplicate stage but neither the column nor the allowlist entry existed. Fix: schema_v99 + allowlist entry. | `tests/test_intake_tracer_allowlist.py`, `db/schema_v99_*.sql`, `rag/intake/doc_pipeline.py` |
| 74'.c | Producer-drift guard: every key set on `doc.extraction_metrics[...]` must be forwarded to a `tracer.write()` OR listed in `_INTENTIONAL_DEBUG_ONLY` with rationale. Plus 2 hygiene checks (no stale debug-only, no overlap with forwarded). Grandfathered 43 pre-existing unforwarded keys with intent comments. | `tests/test_intake_metrics_drift.py` |
| 74'.d | Promote 18 category-B keys from Ship 74'.c's debug-only set to persisted columns. Critic telemetry (7) + filter drops (2) + fingerprint yield (2) + classifier gate (3) + templated fast-path yield (4). schema_v100 + tracer wiring + guard-set trim. | `db/schema_v100_*.sql`, `rag/intake/doc_pipeline.py`, `tests/test_intake_metrics_drift.py` |
| 74'.e | This retro. | — |

## The silent-drop class, end-to-end

Before Ship 74':
- 6 FindingContract counters (Ship 72'.a) never persisted.
- 2 legacy Task #606 counters (`templated_zones_*`) also never persisted.
- 1 duplicate-stage counter (`dup_of_upload_id`) invisibly dropped for months.
- 25-ish other producer keys emitted onto `doc.extraction_metrics` with no traceable rule for which should persist.
- Every retro that said "surfaces automatically" was gambling on that claim.

After Ship 74':
- Every kwarg passed to `tracer.write()` must be in the allowlist (74'.b guard).
- Every producer key must be forwarded OR explicitly declared debug-only (74'.c guard).
- 18 previously-invisible high-value counters now persist (74'.d).
- The remaining 10 grandfathered category-B keys are documented with intent (74'.c comments); Ship 75'+ can promote them when the observability need surfaces.

## The bug pattern that Ship 74' formalized

The `IntakeTracer.write()` shape is a common one in this codebase:

```python
def write(self, stage, ..., **metrics):
    ...
    allowed = {"col1", "col2", ...}
    for k, v in metrics.items():
        if k in allowed:
            row[k] = v
```

The failure mode: **any caller kwarg NOT in `allowed` is silently
dropped.** No exception, no warning, no log line. The kwarg landed
on the function; the value simply never became a column.

Ship 72'.a added new metric kwargs. The dev checked that the code
compiled + the eval passed + the docx dogfood produced findings.
None of those signals would catch a silently-dropped kwarg —
extraction succeeds either way; the trace log just has NULLs where
it should have counters. Ship 72'.d retro wrote "counters surface
automatically." Ship 73' dogfood proved that false 6 weeks later.

Ship 74'.b's guard makes the drop impossible: adding a kwarg to a
`tracer.write()` call without adding it to `allowed` fails CI.

## Codified lessons

Adding 3 new (48-50), reinforcing 1 existing.

### 48. "Automatically" claims in retros need runtime proof

Ship 72'.d's retro claimed the FindingContract counters "surface
in intake_trace_log automatically." That was code-plausible but
untrue — the tracer allowlist silently rejected the kwargs. The
retro's author (me) had checked the fix compiled, eval passed,
docx uploaded successfully — none of which touch the trace log.

**How to apply:** any retro claim about a value being persisted /
delivered / propagated must be paired with a runtime query proving
the state, not just a code walkthrough. "The code is in place" is
not the same as "the values are landing." A single-row `SELECT`
against the target column is 10 seconds; the alternative is a
6-week silent-drop.

### 49. Two-layer allowlists need symmetry tests

The `IntakeTracer.write(**kwargs)` + `allowed` set pattern is a
common Python shape: iterate kwargs through a whitelist. The
failure mode is uniform — a caller kwarg not in the whitelist is
silently dropped. Any function of this shape needs a symmetry
guard: the union of caller kwarg names must be a subset of the
allowlist.

**How to apply:** when reviewing a change that adds a new `write()`
kwarg or a new column, check for this shape. If you see it, look
for or add a symmetry test. Ship 74'.b's guard is 130 LOC of AST
walk + assertion — small enough that it's cheaper to write than to
skip. The Ship 31'.b loader-SELECT guard is the same pattern for
a different shape (SELECT column whitelist).

### 50. Grandfathering-with-rationale is light discipline for "someday" work

Ship 74'.c faced a choice: the producer-drift guard would either
fail on 43 pre-existing keys (blocking the guard) or grandfather
them (defeating the guard). Neither pure approach worked.

The middle path: catalog all 43 in `_INTENTIONAL_DEBUG_ONLY` with
two comment groups — (A) genuinely inline / debug-only and (B)
not-yet-persisted future forwarding arc. The guard fails ONLY on
keys that are neither forwarded nor listed. Adding a new key still
requires deliberate action.

Ship 74'.d then promoted 18 category-B keys to persisted once we
had a concrete plan (schema + wiring). The grandfathering set is a
low-cost carrying vehicle for "we know but haven't fixed yet"
that survives across sessions.

**How to apply:** when a new guard's ground-truth set is bigger
than the near-term fix budget, don't skip the guard OR skip the
discipline. Catalog the current state with intent, and let the
guard hold going forward. Promote out of the grandfather set as
follow-ons.

### Reinforced: 46 (audit before curating — count what's there first)

Ship 74'.c collected 43 pre-existing unforwarded producer keys via
a 40-LOC AST walk before writing the guard. Without that count,
the guard would have been designed against imagined shape and
either grandfathered nothing (blocked on 43 failures) or
grandfathered too broadly (guard useless). The audit is what made
the two-comment-group split obvious.

## What's parked

Micro-arcs that would round out intake observability:
- **Templated table-zone counters (5)** — narrow observability;
  promote when someone's actively debugging tabular templated docs.
- **Templated xlsx per-leaf detail (7 keys, 2 TEXT)** — deep
  debugging surface for xlsx round-trip authoring; promote when
  someone's actively tuning xlsx templates.
- **Silent-drop guard for `write_findings` / cascade producers** —
  Ship 74'.b/74'.c's guards are tracer-specific. Similar `**kwargs
  + allowlist` shapes may exist in the posture writer or cascade
  event producer; audit next arc that touches those files.

Neighbourhood arcs still open from earlier ships:
- Ship 73' loose end: ISO 27701 complement bridges (~7 plausible
  edges for the 12 GDPR articles Ship 73'.b bridged).
- Ship 72' deterministic-path migration (consensus / critic /
  fingerprints extractors through FindingContract).

## Session shape

Ship 74'.a started as a one-line fix on top of Ship 72'.d's retro
error. Once the root cause landed (silent-drop by allowlist), the
arc expanded to close the class of bug rather than just the instance.
74'.b caught a real pre-existing bug (dup_of_upload_id) on its
first run — a persuasive "we needed this" signal. 74'.c added the
upstream companion. 74'.d turned the invisible catalog of category-B
keys into concrete observability. The retro (this file) codifies
the pattern lessons so future arcs don't repeat the "retro said it
worked" bug.

Cadence: audit → guard → apply → measure → codify. Same shape as
Ship 30-32 loader audits + Ship 69' curation audits.
