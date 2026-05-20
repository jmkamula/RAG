---
name: claude-code-hooks-run-under-sh
description: "Claude Code hooks on this VM execute under /bin/sh (dash), not bash — write POSIX-compatible commands or they fail silently"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e02ef53a-6116-4dde-a064-7c0a9bab0a34
---

When writing any `hooks.*.command` in `.claude/settings.json` or `.claude/settings.local.json` on this VM, use POSIX-shell syntax. Bash-isms (`[[ ... ]]`, `==`, `[[ -v var ]]`, `<<<`, arrays) fail with errors like `/bin/sh: 1: [[: not found`.

**Why:** Claude Code's `shell: "bash"` setting (the default) uses `$SHELL` — and on this Azure Ubuntu VM that resolves to `/bin/sh` → dash. Discovered 2026-05-20 while building the memory-sync hook: the `[[ ... ]]` test silently failed (errors went to stderr, hook still exit 0), so the hook appeared to "not fire" when in fact it ran but did nothing. Adding `echo $f >> /tmp/claude-hook-debug.log` to the start of the command surfaced the real error.

**How to apply:**
- Pattern matching → use `case "$f" in PATTERN) ... ;; esac`, not `[[ "$f" == PATTERN ]]`
- String comparison → use `[ "$a" = "$b" ]` (single bracket, single `=`)
- Test if variable empty → use `[ -z "$v" ]`
- Don't assume any bash array support, `${var,,}`, `<<<`, `&>`, etc.
- If you must have bash, set `"shell": "bash"` in the hook block AND explicitly invoke `bash -c '...'` inside the command — relying on the `shell` field alone is not enough on this VM.
- **Always pipe-test hooks under `/bin/sh -c`** before declaring victory, not under interactive bash:  
  `echo '<payload>' | /bin/sh -c '<command>'`

The active example is `.claude/settings.json` (the memory-sync hook). Future hooks should follow the same constraint.
