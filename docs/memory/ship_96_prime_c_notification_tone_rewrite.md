---
name: ship-96-prime-c-notification-tone-rewrite
description: Ship 96'.c — advisory-tone rewrite of the two remaining offenders on the notification surface (posture_flip_to_comply SPA label + stage2_proposal_ready producer title/body). Adds two narrow regression guards that stop the fixed strings from drifting back. Closes Ship 96'.
metadata:
  type: project
---

# Ship 96'.c — Notification tone rewrite (2026-08-26)

## Framing

Ship 96'.a's audit flagged two tone-drift offenders in the
notification surface but deferred them ("kept in scope
discipline") to keep the audit arc focused on ghost-contract
parity. Ship 96'.c fixes them + locks the fixes with regression
guards that pattern-catch future drift.

The rule being applied is
[[feedback-advisory-tone-not-authoritative]] codified in Ship
93'.c: **tenant-facing prose is advisor voice, not authority
voice.** Two words on the notification surface violated it:

- `"compliant"` — implied ArionComply certifies compliance state
- `"engine proposal"` — system-internal jargon the tenant
  shouldn't need to know
  ([[dejargonize-ux-pass-2026-07-01]] mandates
  "engine proposal" → "posture proposal")

## Delivered

**Two SPA humanization labels rewritten**
(`static/arioncomply.html` `_NOTIF_KIND_LABEL` map):

| Kind | Was | Now |
|---|---|---|
| `posture_flip_to_comply` | `'now compliant'` | `'moved to Comply'` |
| `stage2_proposal_ready` | `'engine proposal ready'` | `'posture proposal ready'` |

`"moved to Comply"` uses the finding-state name `Comply` (which
the tenant already sees on the dashboard heatmap chip alongside
NC / OFI / N/A) — that's system vocabulary the tenant knows,
without the tone problem of "compliant." `"posture proposal
ready"` mirrors the dejargonize-ux-pass rename.

**One producer's title + body rewritten**
(`rag/posture_loader.py::stage2_proposal_ready`):

| Field | Was | Now |
|---|---|---|
| Title | `Review engine proposal for {ref}` | `Review posture proposal for {ref}` |
| Body | `Engine proposes {p} (live is {l}). Open Stage-2 to accept or reject.` | `The posture proposal is {p} (live is {l}). Open your Review queue to accept or reject.` |

Body rewrite also nudges "Stage-2" toward "your Review queue"
which is the sidebar label the tenant sees. Reduces the mental
translation from "the notification says X, I need to go find X in
the UI."

**Two regression guards added**
(`tests/test_notification_producers.py` — 35 → 37 tests):

- `test_no_flagged_tone_in_spa_notif_labels` — parses
  `_NOTIF_KIND_LABEL` + asserts the labels don't contain the
  forbidden words `"compliant"` or `"engine proposal"`. Case-
  insensitive to catch capitalization drift. Would have caught
  the pre-Ship-96'.c state; verified by `git stash pop` cycle.
- `test_stage2_producer_body_uses_posture_proposal_language` —
  isolates the stage2_proposal_ready producer block in
  posture_loader.py + asserts `"engine proposal"` / `"Engine
  proposes"` don't appear, and `"posture proposal"` does.

The existing `test_stage2_proposal_ready_wiring` still passes —
it checks structural fields (kind name, dedup arg, control_ref
arg, severity ladder) that Ship 96'.c doesn't touch. Prose
changes and structural tests are independent by design.

**Verified the guards bite**: `git stash push` (reverting the
fixes) → both guards FAIL with the exact violations surfaced.

## Design notes

**Why regression guards this narrow, not a general grep** —
tempting to write `test_no_authoritative_words_anywhere_in_spa`
that greps every tenant-facing string in the SPA for
"compliant / certified / verified / audit-ready". Rejected: the
false-positive rate is high — "verified" in "cited source needs
re-verification" is fine, "audit" in "audit trail" (an internal
term used in metadata field labels) is fine. General-purpose
tone linting needs an LLM pass or a curated context-aware allow-
list. Narrow guards for the specific fixed strings prevent
regression of THESE fixes without the false-positive maintenance
burden.

**Why `"moved to Comply"` not `"posture improved"`** — considered
softer alternatives. Rejected because the notification IS a
posture flip event; describing it as "posture improved" adds
editorial commentary. "moved to Comply" is what happened.

**Why not fix `Stage-2` as sidebar label** — the sidebar label
is `Review queue` (correct); only the producer body prose used
`Stage-2`. The Stage-2 tab-name inside Review queue is a system-
defined queue name the tenant learns as vocabulary; keeping it
inside the queue but referring to the sidebar entrance in prose
gives the tenant a starting point they can navigate from.

## Eval

232 PASS + 1 WARN + 0 FAIL — baseline preserved (SPA + string
edits, no LLM pipeline touch).

Producer + parity + tone-guard tests: 37/37 pass.

## Codified lessons

**Lesson 133: Regression guards for tone fixes should target the
fixed strings, not the general concept.** Fixing "compliant" here
doesn't mean I can prevent all authoritative-tone drift. But I
can guarantee THIS pair of strings doesn't come back. Rule: after
a tone-audit fixes N specific offenders, write N regression tests
that assert those exact fixed strings don't appear. Broader tone
enforcement needs different tooling; specific-string guards are
cheap durable insurance.

**Lesson 134: Producer body prose is a tenant surface too.**
The tone rule flags UI-visible text. Notification bodies land in
the inbox — the tenant reads them. When auditing tone across the
codebase, notification producers' `title` + `body` prose have to
be in scope alongside the SPA humanization maps + toolbar labels.
Rule: when a tone-audit checklist enumerates surfaces, it must
list producer body strings as first-class items, not just static
UI copy.

## Ship 96' arc close

Ship 96' delivered 3 sub-arcs, all in ~one day:

- 96'.a — Notification-kind audit (3 parity guards + 1 ghost
  contract fix). Lessons 127/128/129.
- 96'.b — Cascade timeline UX check (destination now honors the
  clickable-tile promise). Lessons 130/131/132.
- 96'.c — Notification tone rewrite (2 offenders + 2 regression
  guards). Lessons 133/134.

**8 codified lessons total.** Common pattern across the three:
each one applied a prior lesson systematically to a specific
surface and codified new lessons for the next iteration.
Lesson-driven arcs compound.

## Related

- [[ship-96-prime-a-notification-kind-audit]] — flagged both
  offenders "in scope discipline"; 96'.c retires the deferral
- [[ship-96-prime-b-cascade-timeline-ux]] — sibling arc
- [[feedback-advisory-tone-not-authoritative]] — the tone rule
  applied
- [[dejargonize-ux-pass-2026-07-01]] — the "engine proposal" →
  "posture proposal" rename
- [[ship-93-prime-c-coverage-tab-and-tone-pass]] — original tone
  audit that codified the rule Ship 96'.c enforces
