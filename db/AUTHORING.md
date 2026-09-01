# db/AUTHORING.md — where the golden images come from

Ship 102' consolidated ArionComply's three backing stores (Postgres, Neo4j, ChromaDB) into single per-store golden images that a customer install replays. This doc explains **what edits which golden**, so contributors don't accidentally desync source from artifact.

## The philosophy

**Authoring sources → golden images.** Authoring sources stay structured, reviewable, git-diffable. Golden images are build artifacts, regenerated when the authoring sources change. Never edit a golden image by hand.

The pre-commit hook (`scripts/git-hooks/pre-commit`) enforces this: when a staged diff touches an authoring source, it runs the affected build script and stages the regenerated golden in the same commit. Failure aborts the commit.

Enable per-clone:

```
git config core.hooksPath scripts/git-hooks
```

Escape hatches (standard git):
- `git commit --no-verify` — bypass all hooks
- `SKIP_GOLDEN_REBUILD=1 git commit ...` — bypass only the golden rebuild

## The three stores

### Postgres — `db/baseline/schema_baseline.sql` + `seed_curator_data.sql`

| Authoring source | What it drives | Rebuild cost |
|---|---|---|
| `db/schema_v*.sql` | Individual migration files applied to dev DB. Baseline is a pg_dump snapshot of the fully-migrated dev DB. | ~5s |
| `deploy/postgres_preamble.sql` | Roles + databases + extensions bootstrap. | ~5s |
| `deploy/baseline_grants.sql` | Ownership + grants applied after baseline. | ~5s |

**Build script:** `scripts/build_pg_baseline.sh`
**Output:** three files under `db/baseline/`:
- `schema_baseline.sql` — DDL for compliance DB (via `pg_dump --schema-only --no-owner --no-privileges`)
- `schema_sessions_baseline.sql` — DDL for sessions DB
- `seed_curator_data.sql` — catalog data for 10 pure-catalog tables + `retention_policies` cross-tenant defaults

**Workflow for a new schema migration:**
1. Write `db/schema_v110_your_change.sql`
2. Apply to dev DB: `sudo -u postgres psql -d arioncomply_compliance -f db/schema_v110_your_change.sql`
3. `git add db/schema_v110_your_change.sql`
4. `git commit -m "..."` — pre-commit hook regenerates the three golden files from the dev DB (which now has v110 applied) and stages them.

If you forget step 2, the pre-commit hook regenerates baseline WITHOUT v110's effects. You'll notice because customer boxes won't get the change. Apply + re-commit.

### Neo4j — `db/baseline/neo4j_baseline.json`

| Authoring source | What it drives | Rebuild cost |
|---|---|---|
| `load_neo4j.py` | RequirementNode + basic edges (from `iso_nodes_phase1.json` + `gdpr_nodes_phase2.json`). | ~2 min against live dev host |
| `scripts/seed_27701_requirement_nodes.py` | ISO 27701 RequirementNodes (source is copyrighted, seeded from Python constants). | included in above |
| `load_graph_relationships.py` | PART_OF hierarchy + BLOCKS_WHEN + ESCALATES_TO. | included in above |
| `enrichment/relationships/relationship_catalog.py` | 500+ cross-framework typed edges (IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE / DEMONSTRATES). | included in above |
| `enrichment/documents/document_requirements.py` | Catalog of EvidenceRequirements + ChecklistItems. | included in above |

**Build script:** `scripts/build_neo4j_baseline.sh` — exports the entire live Neo4j to JSON via per-label KEY_MAP (business keys, not internal Neo4j ids). All 10 labels' key fields are verified during the export.

**Loader:** `db/baseline/load_neo4j_baseline.py` — single-file replacement for the old 5-loader chain. Reads the JSON, MERGE-loads nodes then edges in two batched phases. Idempotent.

**Workflow for a Neo4j content change:**
1. Edit the authoring source (`enrichment/relationships/relationship_catalog.py`, curator Python files, etc.)
2. Apply to dev host — usually the source Python is a loader, so run it:
   ```
   PYTHONPATH=. python3 enrichment/relationships/load_to_neo4j.py
   ```
3. `git add` your source change
4. `git commit` — pre-commit hook regenerates `neo4j_baseline.json` and stages it.

### Chroma — `db/baseline/chroma_prebuilt.tar.gz` (local only)

| Authoring source | What it drives | Rebuild cost |
|---|---|---|
| Neo4j graph (as reflected in `neo4j_baseline.json`) | 5 collections rebuildable from Neo4j via `scripts/reindex_all.py`. | ~90s + ~$2 OpenAI credits |
| `private/iso27003_2017.txt`, `iso27004_2016.txt`, `iso27005_2022.txt` (gitignored) | 3 collections built from copyrighted ISO guidance PDFs via `scripts/index_iso_guidance_to_chroma.py`. | ~60s + $ per collection |
| `private/edpb/*.pdf` (gitignored) | 1 collection built from copyrighted EDPB / WP29 PDFs via `scripts/index_edpb_to_chroma.py`. | ~30s + $ |
| `rag/embedding_config.py` | Embedding model choice (text-embedding-3-large). Change → full rebuild of all 9 collections. | ~4-5 min + $10 |

**Build script:** `scripts/build_chroma_baseline.sh` — tar+gzips the live `chroma_db/` directory (all 9 collections' current state). Does NOT run the reindex scripts — assumes they've been run against the dev host.

**Output:** `db/baseline/chroma_prebuilt.tar.gz` (~141 MiB, tracked via **Git LFS** — see setup below).

**Chroma is NOT in the pre-commit auto-rebuild loop.** Reasons:
- OpenAI cost — small commits shouldn't burn $ every time.
- Requires `private/*.txt` + `private/edpb/*.pdf` present (dev host only; not on contributor laptops).
- Produces a 141 MiB artifact that's gitignored anyway.

Run manually before a release:

```
bash scripts/build_chroma_baseline.sh
```

The pre-commit hook WARNS if a Chroma-affecting file changes (`scripts/index_*.py`, `rag/embedding_config.py`, or `neo4j_baseline.json`) so you know a manual rebuild is warranted.

## Git LFS setup — required for any clone that runs install.sh

The Chroma golden (`chroma_prebuilt.tar.gz`, ~141 MiB) and its `.meta.json` sidecar are tracked via Git LFS (per `.gitattributes`). GitHub caps regular git files at 100 MiB, so LFS is required.

**One-time setup per clone** (dev host + customer boxes):

```bash
sudo apt install git-lfs
git lfs install
```

After that, `git clone` and `git pull` transparently fetch the real file bytes from GitHub's LFS storage. Without LFS installed, `git pull` writes a small pointer file (~130 bytes) instead of the real tar; `install.sh` step 7 detects this via file size and fails loud with recovery instructions.

**Verify LFS is working:**

```bash
ls -lh db/baseline/chroma_prebuilt.tar.gz
# Expected: 141M (not ~130 bytes)
```

**Publishing new goldens** — no special commands. `git commit && git push` uploads the LFS-tracked bytes to GitHub's LFS backend automatically.

**Free-tier limits** — 1 GB storage + 1 GB bandwidth/month included in your GitHub account. ~7 customer installs/month at the free tier. Beyond that: `$5/month` data packs.

## Summary — one line per rule

- **Never edit files under `db/baseline/` directly.** They're build artifacts.
- **Every Postgres schema change ships as a new `schema_v*.sql`** that you apply to the dev DB before committing.
- **Every Neo4j curator change gets loaded into the dev host** before committing.
- **Chroma rebuilds are manual** — do them before a release cut.
- **`git lfs install` is required on every clone** — otherwise the Chroma tar arrives as a pointer file.
