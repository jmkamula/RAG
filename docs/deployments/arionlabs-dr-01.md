# arionlabs-dr-01 — PoC deployment log

**Target:** first on-prem customer PoC / DR box
**IP:** 10.0.1.85 (private LAN)
**SSH:** `arionops@10.0.1.85` (key: `~/.ssh/arion_operator_ed25519`)

## Deployment record

| Date | Actor | Git SHA landed | Migrations applied | Outcome | Notes |
|---|---|---|---|---|---|
| 2026-09-01 | operator | ~ Ship 102'.f | full schema_baseline via Ship 102'.a | GREEN | Fresh install via Ship 102' golden-image cutover. See [[ship-102-prime-arc-retrospective-2026-09-01]] §102'.f. |
| 2026-09-01 | operator | Ship 103'.a | (no new) | GREEN | Git LFS setup — Chroma golden tar (141 MiB) fetched via `git lfs pull`. See [[ship-103-prime-arc-retrospective-2026-09-01]]. |
| 2026-09-02 | operator | c005bf81 (Ship 104'.f) | schema_v104-v109 | GREEN | Self-serve tenant onboarding — Quickstart flow verified. Tenant "Arion Networks s.r.o." provisioned. See [[ship-104-prime-arc-retrospective-2026-09-02]]. |
| 2026-09-04 | operator | 09a5532e (Ship 110'.f + ops scripts) | — | RED | First update attempt — `sudo bash install.sh` blocked by "run as regular user with sudo" sanity check. Reverted approach. |
| 2026-09-04 | operator | 09a5532e | — | RED | Second attempt — `bash install.sh` (no sudo) blocked at prompt_pw for ARION_OWNER_PW. Root cause: install.sh didn't read .env. Fix scoped as Ship 111'. |
| 2026-09-04 | operator | b77da436 (Ship 111'.b) | schema_v110, v111, v112 | GREEN | Ship 111'.a canonical env names in place + one-time backfill of ARION_OWNER_PW into `.env`. Ship 110' fully live. `install.sh` output: `loaded existing secrets from .env (update mode — missing values will be prompted)`. |
| 2026-09-04 | operator | b9e6a1d4 (Ship 111'.e) | (no new) | GREEN | Ship 111'.c backfill delivered — `client_facts` row inserted for `Arion Networks s.r.o.`. FIRST `.deployment_log.jsonl` line landed. Surfaced country-format bug: tenant had `country="Czechia"` (free-text display name) instead of `"CZ"` ISO code, silently skipping eu_data_subjects derivation. |
| 2026-09-04 | operator | (Path B — direct SQL) | — | GREEN | Ad-hoc SQL fix for the country-format bug on this tenant. UPDATE `tenants.country` + `client_facts.country` to `"CZ"`, add `eu_data_subjects=TRUE` with derived marker in `fact_source`. Manual applicability sweep triggered — 14 A.7.% N/A confirmed. Ship 112' opened to fix the root cause. |
| 2026-09-04 | operator | 55ee72e9 (Ship 112'.c) | (no new) | GREEN | Ship 112' country normalization + Quickstart dropdown live. `.deployment_log.jsonl` now has 2 entries, both GREEN. API up in 15s after restart. Verifies with any new Quickstart tenant that country is stored as ISO code from either free-text (via 112'.a) or dropdown (via 112'.b). |
| 2026-09-04 | operator | d3892488 (Ship 113' + ops script) | `schema_v113_client_facts_regions_and_size_bucket` | GREEN | Ship 113' de-jargonized Profile scoping + region multi-select + sector controlled vocab + 3-bucket size live. First deployment via `scripts/ops/ship-113-poc-update.sh` (per-arc committed script). All 5 new columns verified present, schema tracker updated. `.deployment_log.jsonl` now has 3 GREEN entries. API up in 18s. Arion Networks s.r.o. client_facts region cols all FALSE default (Path B set eu=TRUE previously but wasn't captured in current session — customer can re-set via the new Profile region multi-select or via a fresh Path B if wanted). Sector still `IT Consulting` (legacy free-text from Ship 104' Quickstart — will re-select from dropdown when they visit the new Profile). |
| 2026-09-04 | operator | 2bb7609f (Ship 114'.d) | `schema_v114_sector_backfill_and_check` | GREEN | Ship 114' shipped cleanly. schema_v114 backfilled Arion `IT Consulting → ict_services` + added CHECK constraint. Region backfill normalized `country: Czechia → CZ` + set `eu_data_subjects=TRUE` derived from country. Applicability derivation fired → 14 A.7.% controls N/A via `cloud_only_no_physical` rule. `.deployment_log.jsonl` now has 4 GREEN entries. Final Arion state: `country=CZ, eu=t, sector=ict_services, sector_declared=t, eu_declared=t`. Two loose ends from Ship 113' fully closed same-day. |
| 2026-09-05 | operator | eed7cee1 (Ship 116'.c) | none | GREEN | Ship 116' deployed cleanly. `install.sh` proceeded through all 9 phases with zero prompts (proves the non-interactive path). Ship 111'.a's ARION_OWNER_PW stash carried forward — hard-required-env loader passed. `.env` unchanged. `.deployment_log.jsonl` gained a 5th GREEN entry (`migrations_applied: []` since Ship 116' is code + docs only). Fresh installs going forward use `init-secrets.sh` first; arionlabs-dr-01 is already past that step (installed pre-Ship-116). |
| 2026-09-05 | operator | ae7e0c18 (Ship 118'.c) | `schema_v115_applicability_and_scoping_history` | GREEN | Ship 118' point-in-time posture reconstruction deployed cleanly. Both audit tables (`applicability_status_log`, `client_facts_log`) created + verified. `.deployment_log.jsonl` at 6 GREEN entries. API up in 18s. Also carries Ship 117' architecture doc rewrite. **Note**: audit tables start empty on this box because the ship script's optional derive-applicability sweep was skipped (no `ARION_DEV_API_KEY` in .env on this deploy — the sweep would have populated the first log rows automatically). They will populate on the next fact PUT via Profile UI, or on the next automatic derivation trigger. Non-blocking; snapshot endpoint responds correctly with empty-log gracefully via `coverage: full` for dates ≥ 2026-09-05. |
| 2026-09-05 | operator | e6602bf6 (Ship 118'.d hotfix, third try) | none | GREEN | Ship 118'.d closes the audit-log-kickstart loose end. Three sequential fixes needed on this box: (1) b5ca8834 added `scripts/dev/trigger_applicability_sweep.py` direct-DB utility; (2) 922e2625 fixed the ship script's `-x` check (Python files pulled via git aren't executable) + `$API_KEY` unbound-var reference; (3) e6602bf6 removed all bash `source .env` calls — customer .env from pre-Ship-116 install has a bash-unsafe char on line 64. Root fix: Python utilities load .env via python-dotenv, bash never touches it. Deploy this time: **`applicability_status_log +28 rows`** for Arion (14 clears + 14 sets from `cloud_only_no_physical` rule firing on ISO27001 A.7.% controls). Snapshot smoke test succeeded — Arion has 126 controls (ISO27001-only enrolment), all `Not assessed`. `client_facts_log` remains 0 until customer visits Profile UI. `.deployment_log.jsonl` now has 8 GREEN entries. |
| 2026-09-05 | operator | 52e46bb5 (Ship 119'.d) | `schema_v116_audit_ledger_download_tokens` | GREEN | Ship 119' Auditor's Ledger deployed cleanly across 4 sub-arcs (119'.a PII redactor + user pseudonymisation; 119'.b `build_audit_ledger()` + admin HTML endpoint; 119'.c one-time-download URL delivery + schema_v116; 119'.d Profile → Auditor packages UI). schema_v116 applied. `audit_ledger_download_token` table created. Grants shown: SELECT/INSERT/UPDATE + **stray DELETE (drift)** — flagged mid-deploy, triaged as Ship 120'. PII redactor tests 25/25 pass. Endpoint smoke tests green. UI verified end-to-end via SSH tunnel: Profile → Auditor packages → Generate → tick acknowledgement → one-time URL → private-window download works with no api key. `.deployment_log.jsonl` at 9 entries. |
| 2026-09-05 | operator | c5e0de7b (Ship 120') | none (baseline_grants.sql fix) | GREEN | Ship 120' audit-table DELETE-drift closed. Pure `deploy/baseline_grants.sql` fix — no schema_v117. Post-blanket-GRANT `DO $$` block added; re-REVOKEs the intended shape for 9 audit tables. Live grant matrix on this box after deploy matches intended exactly: `audit_ledger_download_token` = INSERT+SELECT+UPDATE (DELETE gone), `posture_status_log` = INSERT+SELECT (UPDATE+DELETE gone), 5 diagnostic logs = INSERT+SELECT+DELETE (UPDATE gone), `applicability_status_log` + `client_facts_log` = INSERT+SELECT (unchanged). `tests/test_audit_table_grants.py` 4/4 pass. Soft-warn surfaced 8 unclassified `_log` tables for future arc. Root cause was documented in the baseline_grants.sql comment as intentional ordering — Lesson 222 codified: ordering-intent-in-a-comment is not enforcement without a test. `.deployment_log.jsonl` at 10 GREEN entries. |

## Context

- **VM specs**: Intel i5-6500T, 16 GB RAM, Ubuntu 24.04.
- **Ownership**: Self-owned PoC box (per [[feedback-poc-context-low-security-friction]]) — operator = tenant. Low-friction on credential-leak flagging.
- **Credentials vault**: operator's password manager. ARION_OWNER_PW is also stored in `/data/arioncomply/.env` on the box since Ship 111'.a.
- **Network**: :22 open to operator IP only; :8080 tunneled via SSH (`ssh -L 8080:127.0.0.1:8080`).
- **Data mode**: Ship 102'.f wiped 3 stores + reloaded from golden images. Content is authoritative — any Neo4j baseline reload wipes tenant graph data.

## Ship history on this box

### Pre-111 baseline (git c005bf81)

- Ship 102': 3-store golden-image cutover.
- Ship 103': Git LFS distribution.
- Ship 104': Self-serve Quickstart tenant provisioning (Arion Networks s.r.o.).
- Ship 106'-109': shipped locally, deployment status unclear pre-Ship-111 tracking. Post-mortem: 106' + 107' + 108'a + 108'b + 109' were all landed at some point since API restart mtime = 2026-09-03 11:41:33 UTC (Ship 110'.a-e window).

### Ship 110' — client_facts SSoT + fact-driven applicability (git 3fd7424d)

- schema_v112 applied 2026-09-04.
- 6 sub-arcs — see [[ship-110-prime-arc-retrospective-2026-09-03]].
- Verification: `schema_v112_client_facts_scoping_consolidation` in `schema_migrations`. New Profile "About your organisation" section renders.

### Ship 111' — canonical env-var scheme + update-flow fix (git 3c90f7c2)

- Ship 111'.a: install.sh canonicalized env names (`OPENAI_KEY→OPENAI_API_KEY`, `NEO4J_PW→NEO4J_PASSWORD`), added update-mode `.env` loader, extended step 6 writer to stash ARION_OWNER_PW.
- Ship 111'.b: runtime code migrated off `POSTGRES_PASSWORD` (5 sites in `rag/`). Grep guard added.
- Ship 111'.c: backfill script for pre-Ship-110'.b tenants. **Deployment pending on this box.**
- Ship 111'.d: this deployment log + PoC-side `.deployment_log.jsonl` writer in install.sh.

## Known state notes

- **`Arion Networks s.r.o.` tenant** (created 2026-09-02 via Quickstart): pre-Ship-110'.b tenant. Has NO `client_facts` row until Ship 111'.c backfill runs.
- **`applicability_reason` column** exists on `posture_controls` (Ship 110'.a) but has NO rows populated until the tenant answers at least one scoping question (drives Ship 110'.d derivation).
- **Applicability derivation** will fire and mark controls N/A ONLY after tenant provides declared facts via Profile — no automatic mass N/A on first login.

## Watch-list for next deployment

- Verify Ship 111'.c backfill inserts one client_facts row for Arion Networks s.r.o. (probably declared: country + has_physical_premises; derived: eu_data_subjects OR uk_data_subjects depending on their country choice).
- Confirm PoC-side `.deployment_log.jsonl` starts being appended (Ship 111'.d).
- On next update, verify `install.sh` update-mode loader shows all 4 secrets loaded (line: `loaded existing secrets from .env`).
