---
name: ship-100-prime-c-retire-dryrun
description: Ship 100'.c — CLAUDE_DRYRUN.md retired. Original content moved verbatim to docs/history/CLAUDE_DRYRUN.md; a redirect stub sits at the well-known repo-root path. All live references swept to point at CLAUDE_OPERATOR.md instead. Closes Ship 100' arc.
metadata:
  type: project
---

# Ship 100'.c — Retire CLAUDE_DRYRUN.md (2026-08-28)

## Framing

Ship 100'.a delivered `CLAUDE_OPERATOR.md`. Ship 100'.b
closed the last content gap (remote-driving patterns +
wrapper). CLAUDE_DRYRUN.md's forward guidance was fully
subsumed; retiring it prevents future readers from starting
at the wrong doc.

## Delivered

### `docs/history/CLAUDE_DRYRUN.md` (git-mv from repo root)

The full 390-line Ship 48 validation runbook, preserved
verbatim via `git mv` so history follows the move. Anyone
auditing the Ship 48 UX validation exercise (or re-running it)
finds it here.

### `CLAUDE_DRYRUN.md` (new redirect stub at repo root)

35 lines. States clearly:

- File was retired 2026-08-28 in Ship 100'.c
- Forward guidance moved to CLAUDE_OPERATOR.md
- Points at the 4 companion assets (OPERATOR.md, prep
  checklist, DEPLOY_GUIDE §2.6, remote_diagnose.sh)
- Historical content preserved at docs/history/
- Explicit "do NOT use the historical file as guidance for
  new customer installs" callout

The well-known path stays valid — any external doc / README /
Slack link pointing at `CLAUDE_DRYRUN.md` at repo root
doesn't 404; it lands on a stub that redirects.

### Reference sweep

- `CLAUDE.md:387` — "If you are running the pre-POC dry-run …
  read CLAUDE_DRYRUN.md first" rewritten to point at
  CLAUDE_OPERATOR.md with the Ship 100' arc lineage
- `CLAUDE.md` Ship-lineage line — added Ship 100'.a + 100'.b
  retro links alongside Ship 48'
- `CLAUDE.md` Companion documents — added
  `scripts/ops/remote_diagnose.sh` alongside `diagnose.sh`
- `CLAUDE_OPERATOR.md §7` (safety guardrails) — removed the
  "All dry-run rules from CLAUDE_DRYRUN.md §6 apply" cross-
  reference. The rules are inlined below the header; no
  external file needs to be read to know them
- `CLAUDE_OPERATOR.md §Related` — DRYRUN entry updated to point
  at `docs/history/CLAUDE_DRYRUN.md` with a "do not use for
  forward engagements" note
- `deploy/arion_status.sh:27` — comment updated: "Claude Code
  (per CLAUDE_OPERATOR.md) runs this between phases" + added a
  usage example for remote SSH invocation

### Verified no live references remain

Post-sweep grep across `*.md` / `*.html` / `*.sh`:

- 2 remaining hits, both intentional:
  - `CLAUDE_OPERATOR.md:7` — "supersedes CLAUDE_DRYRUN.md"
    (the historical note)
  - `CLAUDE_DRYRUN.md` (the stub's self-reference)

No orphaned pointers.

## Ship 100' arc close

Three sub-arcs delivered:

- 100'.a — Operator runbook + customer prep checklist +
  banners on existing HTML playbooks
- 100'.b — CLAUDE_DEPLOY_GUIDE.md §2.6 remote-driving
  patterns + `scripts/ops/remote_diagnose.sh` wrapper
- 100'.c — CLAUDE_DRYRUN.md retired + reference sweep
  (this arc)

**6 codified lessons across the arc** (156–161 with this
arc's additions):

- 156: Actor-model changes want doc splits, not edits
- 157: Customer-facing checklists want checkbox + explicit
  NOT-acceptable lists
- 158: Wrappers preserve underlying tool discipline
- 159: Verify the disciplining rule before automating it
- 160: Well-known paths deserve redirect stubs
- 161: Reference sweeps end at grep confirmation

Ship 100' arc is functionally complete for customer PoC
engagements. Deferred: handback template refinement after
the first real engagement (natural post-launch activity, not
a separate arc).

## Codified lessons

**Lesson 160: Well-known paths deserve redirect stubs, not
deletions.** Deleting `CLAUDE_DRYRUN.md` would have 404-ed
external links (bookmarks, README references, Slack pins,
CI configs, other repos' documentation). A 35-line stub at
the same path preserves the URL, tells readers what happened,
and points at the forward doc. Rule: when a well-known file
is retired, keep the path alive with a redirect stub for at
least one release cycle. Delete only after grep across the
consuming universe returns clean.

**Lesson 161: Reference sweeps end at grep confirmation, not
"I think I got them all."** After moving the file + rewriting
callers, ran `grep -rnE "CLAUDE_DRYRUN"` across all
`*.md`/`*.html`/`*.sh` and read the output. Two hits both
turned out to be intentional (the supersession note in
OPERATOR + the stub's self-reference). Any UNexpected hit
would have been an orphaned pointer. Rule: after a rename or
retire arc, the finalization step is a grep confirmation
across all consuming file types. Don't ship on faith.

## Related

- [[ship-100-prime-a-operator-runbook]] — the arc that
  introduced the replacement
- [[ship-100-prime-b-remote-diagnose]] — the arc that
  closed the remote-driving pattern gap
- `CLAUDE_OPERATOR.md` — the forward runbook
- `docs/history/CLAUDE_DRYRUN.md` — the retired original
  (verbatim)
- `CLAUDE_DRYRUN.md` — the redirect stub
