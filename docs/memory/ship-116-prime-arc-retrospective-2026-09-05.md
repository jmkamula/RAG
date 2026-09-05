---
name: ship-116-prime-arc-retrospective-2026-09-05
description: Ship 116' arc — split secret provisioning (init-secrets.sh) from install mechanics (install.sh non-interactive)
metadata:
  type: project
---

# Ship 116' — init-secrets.sh + install.sh non-interactive

**Date:** 2026-09-05
**Commits:** `a0085fd7` (a + b bundled) → this doc (c)
**Trigger:** operator observation reading Ship 115'.a's PLAYBOOK.md — the fresh-install section required an interactive SSH session for `install.sh` (password prompts), which broke the "one SSH one-liner" pattern established by Ship 111'.d + Ship 113'.d for per-arc updates.

## Motivation

Ship 111'.a made `install.sh` **update-mode friendly** — reads `.env` if present, prompts only for missing secrets. That fixed the SSH-hang-on-prompt bug that surfaced during Ship 110'.d PoC deploy.

But **fresh install** still needed a TTY: no `.env` yet → 4 prompts. That meant two SSH invocation patterns depending on the box's state:

- Fresh box: `ssh + interactive shell + type passwords + run install.sh`
- Existing box: `ssh ... '<one-liner>'`

Operator asked: **why not always work from `.env`?** If a separate init script owns secret provisioning + writes `.env`, then `install.sh` never prompts, ever. Fresh install becomes a two-step sequence (only init needs TTY); per-arc updates stay one-liners. Uniform mental model.

## Design decisions locked in

Operator picked:

- **A3** — default auto-generate 3 strong passwords, `--prompt` for manual entry
- **B1** — refuse to overwrite existing `.env` (one-time bootstrap by design; rotation is a different flow: edit `.env` directly, restart API)

## Delivery summary

### 116'.a — `scripts/ops/init-secrets.sh` (`a0085fd7`)

One-time secret provisioner. Two modes:

**Default (auto-generate)**:
- Generates 3 × 32-char URL-safe passwords via `openssl rand -base64 32 | tr -d '/+=' | cut -c1-32` (POSIX fallback to `/dev/urandom` if openssl not present).
- Prompts once for `OPENAI_API_KEY` (can be left blank).
- Prints all 3 generated passwords to stdout for operator capture — this is the ONLY time they're shown; `.env` is chmod 600 from that point.

**Alternate: `--prompt`** — each password prompted individually (read -s, hidden).

**Alternate: `--openai-key=<k>`** — skips OpenAI prompt. Combined with auto-generate default → fully headless (`ssh ... 'bash scripts/ops/init-secrets.sh --openai-key=sk-...'` works).

**Guards**:
- Refuses if `.env` already exists at `$ARION_ROOT/.env`.
- Errors if `deploy/.env.example` missing (wrong dir or corrupted repo).

**Output**:
- `.env` written with all 6 canonical keys: `DATABASE_URL`, `SESSIONS_DATABASE_URL`, `PGPASSWORD`, `ARION_OWNER_PW`, `NEO4J_PASSWORD`, `OPENAI_API_KEY` (if provided).
- Same Python replace-or-append writer as Ship 111'.a's install.sh step 6 — behavior parity.

### 116'.b — `deploy/install.sh` non-interactive (`a0085fd7`)

**Step 0 (Sanity checks)** — every `prompt_pw` call removed. `.env` presence is now a hard requirement:

```
✗ .env not found at /data/arioncomply/.env

  Ship 116' (2026-09-04) split secret provisioning from install:
  run the one-time bootstrap first, THEN install.sh:

      bash scripts/ops/init-secrets.sh    # generates or prompts
      bash deploy/install.sh              # what you're trying to run

  See docs/deployments/PLAYBOOK.md for the full fresh-install
  flow. To bring your own passwords use --prompt on init-secrets.sh.
```

Beyond presence, every required secret is validated (partial `.env` also fails loud). Only `OPENAI_API_KEY` is optional.

**Step 6 (.env writer)** — fresh-install branch removed (init-secrets.sh owns that path now). Kept the update-mode `ARION_OWNER_PW` backfill for pre-Ship-111 boxes whose `.env` predates that canonical key.

### 116'.c — PLAYBOOK.md + retrospective (this)

Fresh-install section in `docs/deployments/PLAYBOOK.md` rewritten:

- Old: 2 steps (clone → interactive install.sh)
- New: 3 steps (clone → init-secrets.sh → install.sh non-interactive)

Section numbering shifted (post-install verification is step 4, browser access step 5, register deployment step 6).

`install.sh` phase table updated: step 0 says "HARD-REQUIRES .env"; step 6 says "update-mode backfill only".

`CLAUDE.md` operational playbook section's two-code-block cheatsheet updated to show the Ship 116' two-step fresh install.

## Lessons codified

### Lesson 207 — Interactive is a first-class scope, not an afterthought

Ship 111'.a's `.env` loader + prompt_pw fallback was clever engineering — read from `.env` if present, prompt if not. But the presence of prompts in `install.sh` meant install.sh could NEVER be part of a one-liner. Splitting them cleanly by intent (init = interactive; install = mechanical) removes that constraint entirely. **When "sometimes interactive, sometimes not" is easier than always-one-or-the-other, ask whether the two use-cases deserve separate scripts.**

### Lesson 208 — Auto-generate + print-once is safer than prompt

The old flow expected operators to invent 3 secure passwords. Even well-intentioned operators reuse a family password or pick shorter-than-ideal. Auto-generate + print-once + chmod 600 gets stronger passwords by default, forces the operator to capture them into their password manager (the print-once moment), and leaves no plaintext trail except in the manager. **Default to strong-random for secrets that don't need to be memorable.**

### Lesson 209 — Refuse to overwrite bootstrap outputs

`init-secrets.sh` refuses to overwrite an existing `.env`. Rotation is a different flow. Combining "bootstrap" and "rotate" into one script is a footgun — someone runs init-secrets.sh a second time expecting it to be idempotent, and it silently generates new passwords, breaking every service that had memorized the old ones. Explicit refusal + clear error message directing to the correct rotation path is worth 2 lines of code.

### Lesson 210 — Hard-error with the fix baked into the message

When install.sh fails on missing `.env`, the error message includes the exact command to fix it (`bash scripts/ops/init-secrets.sh`) plus a link to the playbook. No hunting through documentation. **Every fail() call in a bootstrap script should tell the operator what to do next.**

## Related arcs

- [[ship-111-prime-arc-retrospective-2026-09-04]] — `.env`-loader-with-fallback pattern that this arc supersedes
- [[ship-113-prime-arc-retrospective-2026-09-04]] — per-arc script convention (`ship-N-poc-update.sh`) that this arc extends
- [[ship-115-prime-arc-retrospective]] — not yet retro'd; this arc's PLAYBOOK.md updates flow through the Ship 115' playbook shape
- [[feedback-poc-context-low-security-friction]] — arionlabs-dr-01 is self-owned; auto-generated password printed to stdout is acceptable in this context

## Deferred to Ship 117'+

1. **Extend init-secrets.sh for other providers** — currently hardcoded to OpenAI. When Anthropic-key-only or local-LLM-only deployments become common, add `--anthropic-key` / `--local-llm-endpoint` flags.
2. **Rotation script** — `scripts/ops/rotate-secret.sh <KEY_NAME>` for the "rotate a single password without touching the others" case. Currently: edit .env directly + restart. That's fine for now; extract when a customer requests rotation.
3. **`.env` schema validator** — a `--check-only` mode on install.sh that just validates .env shape without doing anything. Useful pre-flight before an update. Skip for now.

## PoC deployment plan for Ship 116'

Ship 116' is code + docs only. Deploy pattern (uses Ship 113'.d convention):

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash scripts/ops/ship-116-poc-update.sh
'
```

Since Ship 116' has no schema migration + no runtime code changes (install.sh + init-secrets.sh + docs only), the per-arc script mostly just needs to:

1. Verify the pulled `install.sh` + `init-secrets.sh` are syntactically valid
2. Verify the `.deployment_log.jsonl` gets a new line (install.sh runs to prove non-interactive path)
3. Restart API (harmless — no code change but keeps deploy log entries consistent)
