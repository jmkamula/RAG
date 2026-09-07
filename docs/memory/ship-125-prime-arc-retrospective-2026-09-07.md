---
name: ship-125-prime-arc-retrospective-2026-09-07
description: Ship 125' arc — dep-upgrade backlog from Ship 124'.c pip-audit findings (python-multipart + langgraph-checkpoint-postgres + chromadb CVE analysis)
metadata:
  type: project
---

# Ship 125' — dep-upgrade backlog (8 CVEs from Ship 124'.c)

**Date:** 2026-09-07 (same day as Ship 124')
**Sub-arcs:** 125'.a python-multipart → 125'.b langgraph-checkpoint-postgres → 125'.c chromadb analysis → 125'.d retro + arc close
**Trigger:** Ship 124'.c's pip-audit surfaced 8 CVEs across 3 packages. Ship 125' closes them — 4 by upgrade, 4 by structural-non-applicability analysis.

## Motivation

Ship 124'.a shipped the scanner + Ship 124'.e added `--ignore-vuln` entries with Ship 125' backlog references so CI wouldn't stay red. Those entries are dishonest by design — they suppress real findings pending fix. Every day they stay in place, `security_scan.sh` gives green output while the CVEs persist.

Ship 125' closes each CVE either by upgrade (drop the ignore) or by documented analysis (keep the ignore + attach a per-CVE rationale explaining why it doesn't apply to our deployment).

## Delivery summary

### 125'.a — python-multipart 0.0.27 → 0.0.31

3 CVEs cleared: PYSEC-2026-3037, PYSEC-2026-3036, PYSEC-2026-3040. Trivial pin bump — FastAPI 0.140.0 accepts 0.0.31 cleanly (no import errors on API restart).

**Verification:**
- pip-audit: 8 → 5 remaining CVEs (all python-multipart CVEs cleared)
- POST /api/v1/documents/upload smoke test: HTTP 200, upload_id returned, status=queued (multipart form parsing works)
- Eval suite: 237/238 PASS + 1 known WARN + 0 FAIL — identical to Ship 124' baseline
- Removed 3 `--ignore-vuln` entries from `scripts/ci/security_scan.sh`
- Latent bug caught: `uploads/` directory (created on first upload) wasn't gitignored. Added to `.gitignore`.

### 125'.b — langgraph-checkpoint-postgres 3.0.5 → 3.1.2

1 CVE cleared: PYSEC-2026-3635. Used 3.1.2 (patch above 3.1.1 named by pip-audit — one extra bug-fix release for free).

**Verification:**
- pip-audit: 5 → 4 remaining CVEs (LangGraph CVE cleared)
- Sync chat smoke test after API restart: returned coherent A.5.15 answer (~120 chars preview) via `PostgresSaver` checkpointer
- Eval suite: 237/238 PASS + 1 known WARN + 0 FAIL — identical baseline, no session-persistence regression
- Removed 1 `--ignore-vuln` entry

### 125'.c — chromadb 1.5.9 CVE analysis (no upgrade)

4 CVEs remain: PYSEC-2026-311 + CVE-2026-45830/45831/45833. **No fix version exists upstream** — chromadb 1.5.9 is the latest release; the CVEs are open on the current shipping code. Rather than defer indefinitely (or downgrade + lose features), we did the analysis:

Each CVE requires an attack surface we don't expose. Full analysis in [[ship-125-prime-c-chromadb-analysis-2026-09-07]]. Structural conditions all verified live on the dev VM at the time of writing:

| Condition | Verified | Verification command |
|---|---|---|
| Chroma binds `127.0.0.1` only | ✓ | `ss -tlnp \| grep 8000` shows `127.0.0.1:8000` |
| No `trust_remote_code=true` anywhere | ✓ | `grep -rn "trust_remote_code" rag scripts` returns only comments |
| No Chroma tenancy args | ✓ | `grep tenant=/database= must_embedding_lookup.py digest.py` empty |
| No `SimpleRBACAuthorizationProvider` | ✓ | `systemctl cat arioncomply-chroma \| grep -iE "auth\|rbac"` empty |

The `--ignore-vuln` entries stay, with per-CVE rationale + re-review triggers (upstream fix / bind change / tenancy adoption / auth provider enabled). Zero code change; pure documented risk decision.

### 125'.d — retro + arc close

Ship 125' arc retro (this doc), MEMORY.md + CLAUDE.md updates. No PoC deploy — the .b + .a upgrades will land on next Ship-N-poc-update.sh script's `install.sh` re-run (pip install honors the updated requirements.txt).

Or specifically: **125' does need a PoC upgrade to land the pip installs**. Adding to Ship 125'.d scope.

## Lessons codified

### Lesson 246 — Not-applicable CVEs deserve documentation-as-code

Ship 125'.c had four CVEs with no upstream fix available. Two lazy paths were possible: (a) keep `--ignore-vuln` entries with generic "Ship 125'.c chromadb — Ship 125'" comments, or (b) drop the scanner entirely for chromadb. Neither preserves the reasoning.

The right shape: an analysis doc (`ship-125-prime-c-chromadb-analysis-2026-09-07.md`) that lays out each CVE's preconditions + our current deployment's non-satisfaction of each, plus per-CVE `--ignore-vuln` comments that reference the doc. When someone six months from now hits `pip-audit` output showing "4 ignored," they can trace back to the doc + verify the structural conditions haven't drifted. Non-applicability decisions age better than "we know" decisions.

The doc also lists explicit re-review triggers — if Chroma bind changes, or `trust_remote_code` gets set, or tenancy features are adopted, or an auth provider is enabled, the ignore decisions become invalid. Automated verification of those triggers (grep guard) is deferred but easy to add later.

### Lesson 247 — Small dep-upgrade arcs bisect cleanly

Each sub-arc did ONE dep upgrade, restarted the API, ran the eval suite. Total eval time: ~52 min for two upgrades + verification. That's slow but perfectly bisectable — if 125'.b's eval had regressed (LangGraph checkpoint changes might break session persistence), we'd know exactly which upgrade caused it. The alternative — bundle both upgrades in one eval — would save ~26 min but require another 52 min to bisect if anything broke.

For dep upgrades where regression risk is real, small sub-arcs pay for themselves. For safer upgrades (patch releases with clear changelogs) we could bundle. Ship 125'.a's python-multipart 0.0.27 → 0.0.31 was low-risk (no API changes in the changelog); Ship 125'.b's LangGraph 3.0.5 → 3.1.2 was medium-risk (session persistence is critical to chat). Bisectability was worth the wait.

### Lesson 248 — pip-audit's blank "Fix Versions" is a design-question signal

For python-multipart + langgraph-checkpoint-postgres, pip-audit listed a specific fix version. For chromadb, the Fix Versions column was blank — meaning no upstream fix exists. That's not a "keep waiting" signal; it's a design-question signal: **is the vulnerability real for our deployment?** We had to answer that question anyway before deciding whether to keep the ignore. Blank fix versions upgrade the analysis from "can we bump the pin" to "does the vulnerability's attack surface exist in our runtime."

## Related arcs

- [[ship-124-prime-arc-retrospective-2026-09-07]] — parent arc that surfaced the 8 CVEs via first scanner run
- [[ship-125-prime-c-chromadb-analysis-2026-09-07]] — detailed chromadb CVE-by-CVE analysis
- [[ship-122-prime-arc-retrospective-2026-09-05]] — earlier Chroma tenant-scoping analysis (Chroma holds catalog only, no tenant PII) — a load-bearing input for Ship 125'.c

## Deferred to Ship 126'+

- **Ship 126'** — the 3 HIGH application-layer gaps from Ship 124' agent findings that are still open: PII in `ai_call_log._preview()` + `chat_consensus_log.query` + `chat_casefile_log.query`; LLM prompt delimiter hardening; SPA localStorage `innerHTML` rehydration. Plus the 2 secret-in-tree items surfaced by Ship 124'.f (`rag/orchestrator.py` docstring credentials + `db/setup_local.sh:70` real dev password).
- **Chromadb config drift guard**: automated verification of the 4 structural conditions in `scripts/ci/check_forbidden_patterns.sh` (grep for `trust_remote_code`, chromadb bind, tenancy args, RBAC provider). Small arc; not urgent.
- **Chromadb 2.x** when upstream ships the CVE fix — will need impact assessment on our 9 collections + `rag/embedding_config.py`.

## PoC deployment plan

`scripts/ops/ship-125-poc-update.sh` follows Ship 118/119/120/121/123 convention:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash scripts/ops/ship-125-poc-update.sh
'
```

Expected: install.sh re-run picks up the new pins (python-multipart 0.0.31 + langgraph-checkpoint-postgres 3.1.2) via `pip install -r deploy/requirements.txt`. Chromadb unchanged (still 1.5.9 with documented ignore). API restart. Sync chat smoke test + file upload smoke test.

**On the PoC after deploy**: `pip-audit -r deploy/requirements.txt --no-deps` should show 4 remaining CVEs, all chromadb, all documented in the analysis doc.
