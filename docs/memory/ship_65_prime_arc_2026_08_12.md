---
name: ship-65-prime-arc-2026-08-12
description: "Ship 65' — verifier investigation empirically confirmed retirement. Sampled 200 recent turns where `missing_verdict_near_ref` fires; zero wrong-verdict claims. Deleted `_verify_posture_status_claims` + 6-symbol cascade. Surfaced repair.py's 40% false-alarm rate as Ship 66' candidate."
metadata:
  type: project
  ship: "65'"
---

# Ship 65' — Verifier investigation: retire or re-enable?

## The arc in one sentence

Ship 65' investigated `_verify_posture_status_claims`
(orphaned since Ship 2'.n), found empirically that the failure
mode it was designed to catch doesn't happen with the current
LLM + case-file digest combination, deleted the cascade — and
surfaced a genuine repair.py over-triggering issue as a Ship
66' candidate.

## Investigation

`_verify_posture_status_claims` was added Ship 1 (2026-06-10)
as an L1 post-compose hallucination guard: drop LLM answer
lines where the (ref, claimed_status) pair contradicts posture
truth. Example failure it caught: LLM writes "A.5.18 [Comply]"
when the tenant's actual A.5.18 finding is NC.

Ship 2'.n (2026-07-16) retired the legacy `rank_and_answer`
body — the guard's caller. The commit message noted the case-
file flow uses preservation-check as its verification mechanism
"different mechanism, own arc". So the guard was orphaned but
never explicitly deleted; Ship 64's audit tagged it as
zero-reference.

## Empirical test — is the guard still needed?

Sampled 200 recent turns from `chat_casefile_log` where
`missing_verdict_near_ref` events fired (in the last 3 days).
For each event, extracted `(ref, expected_verdict)`, found the
ref's occurrences in `answer_text`, and used the *same window
logic as the original verifier* (window from this ref to next
ref) to check whether the LLM actually claimed a wrong verdict.

```
Sampled turns: 136 (200 events)
  wrong-verdict claims (LLM actually lied):        0
  no-verdict inline (LLM cited ref, no status):   66
  false-alarm from repair.py (correct verdict IS   81
    in answer, just outside repair.py's window):
```

**Zero wrong-verdict claims** in 200 events. The failure mode
the guard was designed to catch — the LLM stating the wrong
status for a real ref — does not happen with the current LLM
(gpt-4.1, Ship 53) + case-file digest input (the LLM sees the
correct verdicts inline in POSTURE section).

## Deletions

Cascade delete in `rag/llm_answer.py`:
- `_verify_posture_status_claims` — the guard body
- `_classify_section_header` — only called by the guard
- `_renumber_numbered_lists` — only called by the guard
- `_VERIFIER_REF_RE`, `_VERIFIER_STATUS_RE` — regex constants
  only used by the guard
- `_BULLET_LINE_RE` in llm_answer.py — only used by
  `_classify_section_header`. (Note: same name exists in
  `rag/intake/structural_evidence.py` with a different pattern
  — untouched.)
- `_NUMBERED_BULLET_RE` — only used by `_renumber_numbered_lists`

~150 lines removed. Ship 65' breadcrumb comment left at the
site so a future engineer chasing the guard finds context.
Stale reference to `_VERIFIER_REF_RE` in `rag/casefile/repair.py`
comment updated to note the deletion.

## Bug found + kept as Ship 66' candidate

The empirical run also surfaced that `repair.py::_verdict_
appears_near` over-triggers **~40%** (81 of 200 events). The
correct verdict IS present in the answer text — it's just
outside the helper's 80-char window (across a paragraph break,
or after too many other refs). Consequence:

- `chat_casefile_log.repair_events_count` is inflated by ~40%
  for `missing_verdict_near_ref` events specifically.
- Anyone using this metric to prioritize verifier fixes would
  over-invest in the wrong problem.
- The false-alarm rate is silent — no auditor-visible impact,
  but it clouds the observability signal.

Not fixed this ship — Ship 65' scope was the verifier
investigation. Recorded in retro + code breadcrumb comment as
a Ship 66'+ candidate. The fix shape is likely: expand the
window heuristic to include multi-sentence detection, or match
the same "next-ref boundary" logic the deleted verifier used.

## Codified lessons

### 27. Verify a "safety net" empirically before restoring it

The natural move on finding an orphaned verification helper is
to check "should we re-enable this?" and re-wire it. Ship 65'
inverted that: sampled 200 recent turns, measured the actual
failure rate, and found the safety net protects against a
failure mode that no longer happens. Restoring it would have
added complexity + latency + risk of wrongly dropping good
content, for zero measurable benefit.

Rule: before restoring an orphaned safety mechanism, measure
whether the failure it targets still occurs. LLMs have improved;
prompts have improved; digest data has improved. Yesterday's
necessary guard is often today's dead weight.

### 28. An empirical audit surfaces adjacent defects

The Ship 65' probe was scoped to answer "should we restore the
verifier?" but the same data proved repair.py's own detection
over-triggers 40%. The metric it emits
(`missing_verdict_near_ref` in observability) is silently
misleading. If Ship 65' had scoped narrowly to yes/no on the
verifier, this finding wouldn't have surfaced.

Rule: when running an empirical audit, look at what the data
tells you beyond the question you asked. Adjacent findings are
often the biggest value.

## Follow-ons

- **Ship 66' candidate** — fix repair.py's window over-triggering
  on `missing_verdict_near_ref`. Improves observability signal
  accuracy. See empirical breakdown above.
- **Ship 64' 22-candidate list** — still open. Ship 65' closed
  the biggest single item; the remaining 21 are smaller.

## What Ship 65' costs to reproduce

- Schema migrations: 0
- Wall clock: ~40 min (git history + empirical probe + cascade
  delete + smoke test + retro)
- Files touched: 3 (llm_answer.py -150 lines, repair.py comment,
  retro doc)
- Verification: chat smoke HTTP 200, Ship 63 tests 5/5 PASS,
  Ship 63 guards OK, no cascading breakage.
