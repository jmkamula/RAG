---
name: feedback-auto-compaction-loses-practice-patterns
description: "Auto-compaction preserves WHAT was built but strips HOW we worked together — save practice patterns as explicit feedback memories, don't trust the summary to preserve them"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Auto-compaction preserves the WHAT of a session — files changed,
commits landed, arcs closed. It strips the HOW — arc cadence,
deferred-item shape, verify-before-assert discipline, deploy patterns,
tone of collaboration, when to ask for approval vs proceed. Mitigate
by saving distinct practice patterns as explicit feedback memories
rather than trusting the summary to preserve them.

**Why:** User observation on 2026-09-06 noticed context loss across
two auto-compaction events in this session. We recovered each time
but iteration cycles cost. Practice patterns aren't code — they don't
survive commit history, don't show up in git diffs, don't get
asserted by eval. If they only live in the current session, they die
at compaction. The mitigation: promote them to durable memory files.

**How to apply:**
- When a distinct practice pattern emerges (a new discipline, a
  preferred cadence, a "we always do X," a naming convention, a
  before/after rhythm), save it as a feedback-type memory file with
  rule + why + how-to-apply structure.
- Watch for the signal "we've done this three times now" — that's a
  pattern, not a coincidence.
- Better to over-save patterns than lose them at the next compaction.
- When the user flags something as "JBTW" (just by the way), it's
  often a real durable observation about how we work; save it even
  if there's no immediate action.
- Cross-link related feedback memories with `[[name]]` so the mental
  model reassembles from any starting point.

Related: [[feedback-arc-cadence-small-sub-arcs]] (a pattern that would
have been lost without capture), [[feedback-verify-before-assert-live-state]]
(a discipline that would have been implicit-only without capture).
