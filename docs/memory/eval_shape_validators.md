---
name: eval-shape-validators
description: "SHIPPED 2026-06-09 (376628d + 4eba6ff): EvalCase.shape='stage2' replaces strict-string must_contain for state-sensitive queries. _check_stage2_shape accepts any of 3 valid post-engine states + verifies internal consistency. 157/157 Stage-2 cases converted."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

State-sensitive eval cases (e.g. `pending engine verdict for X`)
cycle through several valid chat-surface states as tenants act:

  - **pending**     — `Art.18: engine proposes 'OFI', live finding
                       is 'NC'. Reason: ALL: 1/4 children satisfied.`
  - **approved**    — `Art.18: engine verdict 'OFI' already approved.
                       Live finding: 'OFI'.`
  - **concurrence** — `Art.18: engine concurs with live at 'NC'.
                       Reason: ...`

Pre-2026-06-09, every state shift required re-ratcheting
`must_contain` per case. Two ratchets in one session on the same 9
cases (06-09 AM + PM) proved the cost wasn't sustainable.

## What ships

**`tests/eval_suite.py`**:

- `EvalCase.shape: Optional[str] = None` — new field.
- `_check_stage2_shape(answer, expected_refs) -> (passed, failures)`:
  detects state via phrase markers, then runs internal-consistency
  checks. See function docstring.
- Runner: when `case.shape == "stage2"`, skip `must_contain` and call
  the validator. `must_not_contain` still applies (defense in depth).

**Stage-2 EvalCase convention** (157 cases, all converted):
```python
EvalCase(
    id=N,
    query="pending engine verdict for X",
    expected_refs=["X"],
    expected_type="posture_check",
    shape="stage2",
    must_contain=[],
    must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                      "I need more information", "could you clarify"],
    notes="...",
),
```

The `must_not_contain` lines are now somewhat redundant with the
shape validator's `_STAGE2_FORBIDDEN_PHRASES` — keep them as
documentation of the regression catches the case cares about.

## What the validator checks

1. **Ref present**: at least one `expected_refs` member appears in
   the answer.
2. **State detection**: exactly one of `engine proposes` /
   `already approved` / `engine concurs with live`. Any other shape
   → FAIL.
3. **Finding label**: `\b(NC|OFI|Comply|N/A)\b` matches somewhere.
4. **For pending state**: `N/M children satisfied` with M ≥ 2.
   Single-leaf shapes (`0/1`) are a regression signal — the spec
   should be multi-leaf curated.
5. **Forbidden regression**: none of these substrings —
   `0/1 children satisfied`, `no curated multi-leaf`,
   `I need more information`, `could you clarify`.

## When to add a new shape validator

Mirror this pattern for any other query family where the chat
surface has multiple valid states cycling on tenant action. Likely
candidates:

- `pending workbook finding for X` (Stage-1 queue cycles
  pending → approved → rejected → empty)
- `documents needed for X` (cycles registered → uploaded → assessed)
- `incident obligations for X` (cycles open → triaged → closed)

For each: define the state-detection phrases + internal-consistency
rules + forbidden regression substrings, add a `_check_NAME_shape`
function, add the name to the runner's branch, set
`shape="NAME"` on the relevant cases.

## How to apply

- New Stage-2 EvalCases: default to `shape="stage2"`, leave
  `must_contain=[]`. Don't add ratchet-prone literal strings.
- Debugging a shape failure: read the `failures` list — each entry
  is prefixed `stage2_shape:` so you can tell shape-validator
  rejects from ordinary `MISSING required phrase` rejects at a
  glance.
- Tightening the validator: add new entries to
  `_STAGE2_FORBIDDEN_PHRASES` or extend the regex set. Removing
  things from the validator is the harder direction — every
  removal weakens what counts as "valid Stage-2 shape" for all 157
  cases at once.

## Related

- [[feedback-eval-with-each-feature]] — the eval doctrine this
  closes a follow-up on.
- [[compose-posture-any-progress-ofi]] — the strict-rule decision
  that made Stage-2 state churn worth solving rather than ignoring.
- [[stage1-engine-kick-after-batch]] — the auto-kick that made
  Stage-2 state shift on every Stage-1 approval, accelerating
  ratchet pressure.
