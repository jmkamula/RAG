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
| 2026-09-04 | operator | 3c90f7c2 (Ship 111'.c) | (no new) | pending | client_facts backfill for the pre-Ship-110'.b Arion Networks s.r.o. tenant. |

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
