---
name: feedback-verify-stability-claims
description: "Verify eval-case stability claims against recent eval history before asserting a failure is \"pre-existing\" or \"known-stochastic.\" CLAUDE.md notes describe what CAN happen, not what IS happening now."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Before framing an eval failure as "pre-existing" or "known-stochastic
residual" based on a CLAUDE.md / retro note, check recent eval CSVs
on disk to see whether the described weakness is currently active.
`ls -t /data/arioncomply/results/eval_*.csv` + `/tmp/eval_*.csv` gives
the recent history; `awk -F, 'NR==1 || $1 == "<case_id>"'` on each
shows the pattern.

**Why:** Ship 75'.e retro claimed case #5 was a "pre-existing residual
that has tripped intermittently since Ship 43'.a." User pushed back
("i dont recall case #5 being a pre-existing residual") — investigation
showed case #5 had PASSed every recent eval on disk (6+ files) and
4/4 post-hoc re-runs. The CLAUDE.md note about a rare "physical" trip
was accurate as a description of what CAN happen, but hadn't actually
been happening in months. Leaning on the cached note without checking
current state cost me a correction commit + credibility.

**How to apply:**
- Any eval FAIL you're inclined to write off as "known residual" —
  check `awk -F, 'NR==1 || $1 == "N"' recent_eval*.csv` first.
- If recent history shows PASS, the current failure is either (a) a
  rare stochastic firing (verify with re-runs) or (b) a fresh
  regression (bisect against the code you just changed).
- Only frame as "pre-existing residual" if the current data supports
  it — recent evals show intermittent failures, not consistent PASS.
- CLAUDE.md stability notes describe classes of behavior. They don't
  auto-refresh; a note from Ship 43'.a might not describe today's
  reality. Treat them as one input, not authority.

Related: [[feedback-eval-state-drift]] — assertions on tenant-state
data decay over time. Same principle: don't trust a snapshot claim
without verifying against current data.
