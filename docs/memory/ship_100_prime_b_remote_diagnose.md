---
name: ship-100-prime-b-remote-diagnose
description: Ship 100'.b — added CLAUDE_DEPLOY_GUIDE.md §2.6 remote-driving patterns section (SSH + scp + bundle extract for Claude-on-operator-laptop model) + new scripts/ops/remote_diagnose.sh wrapper that automates the three-command pattern into one call. Ship 100'.a deferred item now landed.
metadata:
  type: project
---

# Ship 100'.b — Remote-diagnose pattern + wrapper (2026-08-28)

## Framing

Ship 100'.a landed `CLAUDE_OPERATOR.md` for the
Claude-on-operator-laptop model but noted `CLAUDE_DEPLOY_GUIDE.md`
still assumed on-VM execution for every `§2.x` diagnostic
pattern. Ship 100'.b closes the gap: adds an explicit
remote-driving section + a wrapper script so the three-command
SSH-diagnose-scp-extract pattern becomes one call.

## Delivered

### `CLAUDE_DEPLOY_GUIDE.md` §2.6 — Remote-driving patterns

New section inserted after the on-VM patterns (§2.1-2.5). Four
building blocks:

1. **Push a one-off inspection command** — `ssh <target>
   '<command>'` for `arion_status.sh`, `systemctl status`,
   `journalctl` etc.
2. **Produce + retrieve a diagnostic bundle** — the
   three-command SSH → scp → extract pattern, plus the
   single-command wrapper alternative
3. **Read a specific file inside a bundle without extracting** —
   `tar xzOf` piping
4. **Applying a fix from the operator laptop** — post-fix
   verification via `arion_status.sh --json`

Key discipline codified: **"Never SSH back to the VM to look
up details you can find in the bundle."** The bundle is
self-contained by design; if it's missing information you need,
that's a `diagnose.sh` bug worth filing rather than working
around indefinitely.

### `scripts/ops/remote_diagnose.sh` (new, ~90 LOC)

Bash wrapper that takes an `<ssh-target>` and optional
`[local-scratch-dir]`, then:

1. Verifies SSH works (BatchMode + 10s timeout) before doing
   anything
2. SSHes in, runs `bash /data/arioncomply/scripts/ops/diagnose.sh`
3. Extracts the tarball path from `diagnose.sh`'s output (grep
   for the `/tmp/arion-diag-*.tar.gz` pattern), with a
   `ls -1t /tmp/arion-diag-*.tar.gz | head -1` fallback if the
   grep misses
4. `scp`s the tarball to the scratch dir
5. Extracts into a named subdirectory (side-by-side with the
   tarball for easy cleanup + re-extraction)
6. Prints the local extraction path to stdout — Claude's next
   read operations use that path directly

Guardrails:

- Refuses to write to `$HOME` or `/` directly (must be a
  named subdirectory)
- Uses `set -euo pipefail` — any failure aborts cleanly
- Uses standard sysexits.h exit codes (64 usage, 70 software,
  74 IO, 77 nopermission, 78 config) so callers can branch on
  failure mode

Safe to run repeatedly (each invocation produces a fresh
timestamped scratch dir if the caller doesn't specify one).

## Sanity verification

- Usage error exit path — invocation with 0 args prints usage,
  exits 64 ✓
- HOME guard — invocation with `$HOME` as scratch dir fires the
  "must be a named subdirectory" refusal + exits 78 ✓
- `diagnose.sh` output format check — line 418 emits
  `Diagnostic bundle written: /tmp/arion-diag-<host>-<ts>.tar.gz`;
  matches wrapper's grep pattern ✓

End-to-end SSH+scp path was NOT tested on this dev VM (no
passwordless SSH to localhost configured); real validation
happens on the first remote engagement.

## Codified lessons

**Lesson 158: Wrapper scripts should preserve underlying
tool discipline, not hide it.** The wrapper collapses three
commands into one but the underlying pattern (SSH → produce
bundle → scp → extract) stays visible via the `§2.6` docs
that lead with the raw commands. The wrapper is the
convenience layer; the raw commands are the truth. Rule:
when writing a wrapper for a multi-step pattern, document
the raw steps FIRST so future readers understand what the
wrapper does. Reverse order breeds cargo-culting.

**Lesson 159: Verify the disciplining rule before automating
it.** CLAUDE_DEPLOY_GUIDE.md §2.6 explicitly says "never SSH
back to look up details you can find in the bundle." Adding
the wrapper INCREASES the temptation to keep SSHing (it's
so easy now) — the disciplining note is more important, not
less. Rule: when automation makes a tool cheaper to use,
tighten the "when NOT to use it" discipline; don't relax
it.

## Ship 100' arc status

- 100'.a — Operator runbook + customer prep (shipped)
- 100'.b — Remote-diagnose pattern + wrapper (this arc)
- 100'.c candidates: handback template refinement after
  first real engagement; retire CLAUDE_DRYRUN.md when
  practical

## Related

- [[ship-100-prime-a-operator-runbook]] — the arc this
  completes
- `CLAUDE_OPERATOR.md §Phase 3` — where the wrapper gets
  invoked
- `CLAUDE_DEPLOY_GUIDE.md §2.6` — the pattern documentation
- `scripts/ops/diagnose.sh` — the underlying tool (unchanged)
- `deploy/arion_status.sh` — post-fix verification tool
