---
name: feedback-eval-state-drift
description: "Eval assertions on tenant-state-dependent queries (current postures, top-N ranked surfaces) age out of date as the data shifts. Prefer structural assertions (must_contain section headers, format markers, mislabel guards) over data-specific locks (specific control refs, specific titles). Cases on stable infrastructure can lock specifics safely."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Eval cases that assert specific tenant-state values **age out of
date** as the system evolves. The eval keeps the same assertion,
but the underlying data shifts, and the case starts failing for
reasons unrelated to whatever it was originally locking in.

Two patterns of decay I've seen on this codebase:

## Pattern 1 — Posture state drift

**Symptom:** `expected_refs=["A.5.1", "A.5.15"]` for "show me OFI
findings" silently rots when both controls get accepted as NC in
a Stage-2 mass-approval session. The case keeps testing the same
assertion; the assertion was true at authoring; it's false now.

**Concrete:** case #3 was authored 2026-06-02 after a mass-approval
session that left A.5.1 + A.5.15 as the only surviving OFIs.
2026-06-14's 35-NC acceptance flipped them both. Case sat
failing for a day until I dug in.

**Fix:** prefer structural assertions for current-state queries.
For OFI list:
  - `must_contain=["OFI"]` (the verdict label always appears)
  - `must_not_contain=["A.9.2", "A.10.", "A.4."]` (clause-vs-Annex-A
    mislabel guard always relevant)
  - `min_findings=1` (some OFI must surface, but not which one)
  - `expected_refs=[]` (no specific-ref lock)

The case still proves the exhaustive-list rule + clause-vs-Annex-A
labeling. It doesn't pin which controls happen to be OFI today.

## Pattern 2 — Recency-ranked surface drift

**Symptom:** `must_contain=["Access Control Policy"]` for "what
documents have we uploaded?" rots when 20+ newer uploads push that
2026-05-20 doc out of the truncated top-20.

**Concrete:** case #26 was the second to fail today. The short-
circuit answer truncates at 20 with "… and N more". Access Control
Policy didn't disappear from the system — it just moved into the
tail.

**Fix:** assert structural shape (header text, per-line format,
canonical IDs, truncation marker) rather than which specific item
happens to fall inside the window:
  - `"Uploaded documents"`     — short-circuit header
  - `"uploaded"`               — per-line metadata format
  - `"(DOC0"`                  — canonical title format
  - `"and"`                    — the "… and N more" truncation tail

The case still proves the short-circuit fires + names real titles
+ truncates correctly. It doesn't pin which doc happens to be in
view.

## Pattern 3 — LLM prose phrase drift

**Symptom:** `must_contain=["NC"]` for gap-analysis queries silently
decays when the tenant state shifts (mass-approval, sweep, upload
surge). The LLM's answer prose becomes more verbose or uses "non-
conformity" spelled out instead of the abbrev; literal string
`"NC"` may not appear even though the answer is correct.

**Concrete:** 2026-07-06 queue-cleanup arc moved 36 controls to NC
in a batch approve. Cases #2 / #4 / #9 / #28 all had
`must_contain=["NC"]`. Post-batch, the answers now describe 207
NCs — enough that the LLM sometimes phrases prose differently on
the top-N summary. 4 cases dropped from PASS → FAIL for prose-
variance reasons that had nothing to do with correctness.

**Fix:** don't literal-string-check LLM prose that varies. The
`min_findings` counter already uses a **flexible regex**
`r'\bNC\b|non.?conformit'` that catches BOTH "NC" and
"non-conformity" variants. Rely on:
  - `expected_type=gap_analysis` (routing must succeed)
  - `must_not_contain=["I need more information", "could you clarify"]`
    (hedging guard)
  - `min_findings=2` (regex-flexible count check)
  - Drop `must_contain=["NC"]` entirely

The load-bearing signal is that the query routes to gap analysis
with ≥2 findings and doesn't hedge. Literal phrase matching on
LLM prose is fragile.

Same fix for `expected_refs` on LLM-stochastic cases (#16, #21):
drop the ref lock, keep the query-type routing check + prose
keyword. Ref surfacing is prose-order-dependent and stochastic —
locking specific refs turns a working case into a flip-flopper.

## When specific locks ARE safe

Cases on **static infrastructure** (not tenant state):
  - Stage-2 verdict format ("engine proposes 'NC'", "0/4 children
    satisfied" — see `[[eval-shape-validators]]`)
  - Per-MUST advisory anchors ("How to advance X", "Still needed:",
    "To address:" — case #199)
  - Cross-framework bridge footer ("↳ Bridges to ISO 27001 for
    Art.X" — eval case #24/#25)
  - Definitional answers ("NC stands for", "an Annex A control...")

These don't depend on which controls are NC vs OFI today or which
docs are top-uploaded — they lock the system's deterministic
output. Specific assertions are fine here.

## Distinguishing decay from regression

When an eval case starts failing:
  1. Re-run it 3-4 times to separate stochastic from consistent
  2. If consistent failure, check whether the *ground truth*
     changed (look at the data the assertion is about)
  3. If ground truth changed → state drift; re-author with
     structural assertions
  4. If ground truth unchanged but answer regressed → real
     architectural bug; investigate the chat path

The 4-runs-per-case diagnostic surfaced #3 + #26 as consistent
failures (0/4) vs #2/#16 as truly stochastic (2/4). Without that
step I'd have grouped all 4 as "the same LLM noise" and missed
the real distinction.

## Pair rule

Sibling of `[[feedback-eval-with-each-feature]]` — every new
feature gets an eval case. This rule says: every state-dependent
eval case should be re-checked when tenant state shifts (Stage-2
approvals, mass uploads, schema migrations). Author with shape
where possible to amortize.

## Implementations of this pattern today

- `shape="stage2"` validator (eval_suite.py:_check_stage2_shape) —
  accepts any of pending/approved/concurrence states; verifies
  internal consistency. Replaced 157 strict-string assertions.
- `shape="cross_framework"` validator
  (eval_suite.py:_check_cross_framework_shape) — accepts any ISO
  bridge ref; required for the LLM-stochastic cross-framework
  cases #24 + #25.
- #3 + #26 re-author (813c35d) — direct must_contain swap to
  structural markers.
- #2 re-author 2026-06-15 — same pattern. Dropped A.5.26 ref lock
  after it decayed from the 168-NC top-N. Now expected_refs=[],
  must_contain=["NC"], min_findings=2. 4/4 PASS post-fix. CLAUDE.md
  formal known-stale entry retired.

## Related

- [[eval-shape-validators]] — the precursor pattern. Stage-2 cases
  were the first wave of "assert shape, not state".
- [[feedback-eval-with-each-feature]] — pair rule about
  authoring new cases per feature.
- [[case-2-drift-followup]] / [[case-24-art32-bridge-followup]] —
  cases that stayed known-stale because the underlying state was
  too stochastic for either specific or structural assertion.
