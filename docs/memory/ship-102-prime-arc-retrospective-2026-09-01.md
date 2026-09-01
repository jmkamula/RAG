---
name: ship-102-prime-arc-retrospective-2026-09-01
description: Ship 102' arc — consolidated Postgres+Neo4j+Chroma into single per-store golden images with pre-commit trigger discipline and safe-cutover install.sh. Retired the incremental loader chain (schema_v*.sql migrations + 5 Neo4j loaders + reindex_all step) on the customer install path. Verified end-to-end on arionlabs-dr-01 fresh cutover.
metadata:
  type: project
---

# Ship 102' — golden image consolidation across 3 stores (2026-09-01)

## Framing

Before Ship 102', a customer install ran through:

- Postgres: `schema_baseline.sql` (frozen ~ v89) + optionally 113 `schema_v*.sql` incrementals in numeric order. Ship 101'.b tried to auto-apply them and hit `CREATE POLICY` collisions on v3.
- Neo4j: five loaders in dependency order — `load_neo4j.py` → `seed_27701_requirement_nodes.py` → `enrichment/relationships/load_to_neo4j.py` → `load_graph_relationships.py` → `enrichment/documents/load_to_neo4j.py`. First fresh customer install revealed that install.sh only ran the last one; 4 were silently missing.
- Chroma: rebuilt at install-time via `reindex_all.py`. Costs ~$2 OpenAI per install; couldn't rebuild the 4 collections whose source content lived in `private/` (copyrighted PDFs, gitignored).

Every "3-store install" had latent drift because each store's install path was independent, incrementals-driven, and unverified as a unit. Ship 101'.b closed acute Neo4j gaps; Ship 102' closes the class of problem.

## The codified pattern

**Authoring source → build script → golden image → install consumer.**

Three golden images per store, plus a pre-commit hook that regenerates them from the authoring sources whenever those change. install.sh consumes the goldens; the incremental loader paths remain as fallback.

```
Authoring source                      Build script                             Golden image                            install.sh
─────────────────                     ─────────────                            ─────────────                           ──────────
db/schema_v*.sql          ─────►      scripts/build_pg_baseline.sh    ─────►   db/baseline/schema_baseline.sql         psql -f
deploy/postgres_preamble.sql                                                    db/baseline/schema_sessions_baseline.sql  psql -f
deploy/baseline_grants.sql                                                     db/baseline/seed_curator_data.sql       psql -f

enrichment/**                                                                 db/baseline/neo4j_baseline.json         python3 load_neo4j_baseline.py
iso_nodes_phase1.json                 scripts/build_neo4j_baseline.sh ─────►
gdpr_nodes_phase2.json
load_neo4j.py + load_graph_relationships.py + seed_27701...

Live Chroma (populated by                                                     db/baseline/chroma_prebuilt.tar.gz       tar -xzf
reindex_all.py + index_*.py           scripts/build_chroma_baseline.sh ─────►
scripts against private/ PDFs)
```

## What shipped

| Sub-arc | SHA | Deliverable |
|---|---|---|
| **102'.a** | `236173a0` | Postgres golden. Regenerated `schema_baseline.sql` (~730 new lines from v90-v109 that never reached customer boxes before) + `seed_curator_data.sql` grew from 6 tables (4 empty) to 10 tables with 1,152 catalog rows. Biggest single gap closed: the 844 template scaffolds. |
| **102'.b** | `fe607bb4` | Neo4j golden. `neo4j_baseline.json` 16 MiB export using per-label `KEY_MAP` for stable business-key identity (verified: all 10 labels have unique keys). `load_neo4j_baseline.py` — single-file replacement for the 5-loader chain. Two-phase MERGE (nodes first, then rels), grouped by (label, key-shape) so each Cypher uses static labels. |
| **102'.c** | `80dafdd0` | Chroma golden build script. Tar+gzip of `chroma_db/` contents. All 9 collections verified via chromadb.PersistentClient roundtrip. 141 MiB output — didn't fit git 100 MB per-file limit; deferred distribution to Ship 103'. |
| **102'.d** | `9e1bd7bd` | Pre-commit hook + `db/AUTHORING.md`. Smart per-source triggers: PG + Neo4j auto-rebuild on relevant source changes, Chroma warn-only (OpenAI $ + private/ PDFs + 141 MiB artifact). Docs cover authoring workflows + escape hatches. |
| **102'.e** | `7d7b2224` | install.sh safe cutover. Consumes goldens as primary path, keeps 5-loader chain + schema_v migrations as fallback. Zero deletions — no risk of "cutover broke and we lost the working code." |
| **102'.f** | `98c09111` | Customer-box verification. Wiped Postgres + Neo4j + Chroma on arionlabs-dr-01, `git pull` + `git lfs pull` (via Ship 103'.a's LFS setup) + rerun install.sh. All three golden paths fired first-try. Data-parity probes (`scripts/dev/probe_neo4j.py` + `probe_chroma.py`) confirm byte-identical to source. |

## Codified patterns worth remembering

**Lesson 164: pg_dump beats replaying incrementals.** A baseline that captures current state via `pg_dump --schema-only --no-owner --no-privileges` is atomic and idempotent; replaying 113 `schema_v*.sql` on top of that baseline is neither (POLICY / VIEW / DOMAIN DDL has no `IF NOT EXISTS` guard in Postgres, so it errors on the second apply). Rule: for any schema-migration story on a fresh box, prefer a regenerable pg_dump baseline + a `schema_migrations` tracker over "apply all incrementals in order."

**Lesson 165: business-key export beats internal-id export.** Neo4j internal node ids are unstable across DB resets. When exporting a graph for reload, use a per-label KEY_MAP of business-key properties (e.g., `RequirementNode.id`, `Template.(leaf_id, template_version)`) instead. Verified during Ship 102'.b audit that all 10 label classes have such keys. The loader MERGEs by these keys, which makes both first-load and idempotent replay work correctly.

**Lesson 166: byte-identical verification is the definitive test.** For any "does this loader produce the same state as the source" question: dump the source state → wipe → run the loader → re-export → diff. Ship 102'.b applied this: 8148 nodes / 14378 rels roundtripped with ZERO property mismatches. Every other test (idempotent replay, spot-check queries) is a proxy for this one.

**Lesson 167: safe cutover keeps both paths alive.** Ship 102'.e adds golden-consumption logic to install.sh but doesn't delete the legacy paths. Zero risk of "cutover broke and we lost the working code." Deletion happens in Ship 104' once cutover has been proven on multiple installs. This mirrors the Ship 35' consensus-extraction pattern (default-OFF flag until proven, then default-ON) applied to install-time behavior.

**Lesson 168: warn-only pre-commit triggers for expensive rebuilds.** Not every source change should force a rebuild. Chroma rebuild costs OpenAI $ + requires `private/` PDFs that only the dev host has. Pre-commit WARNS on Chroma-affecting changes, requires the operator to manually run `bash scripts/build_chroma_baseline.sh` before release. Post-hoc-visible discipline is the right shape here — auto-invisible-hooks would either burn money or fail silently.

**Lesson 169: never edit `db/baseline/*` by hand.** Golden images are BUILD ARTIFACTS. Any manual edit gets clobbered by the next pre-commit trigger. `db/AUTHORING.md` codifies this at the top; contributor discipline enforced by trigger regexes that catch direct golden edits.

## Deferred to Ship 104' arc

- **Retire the 5-loader Neo4j chain** — `load_neo4j.py`, `load_graph_relationships.py`, `scripts/seed_27701_requirement_nodes.py`, `enrichment/relationships/load_to_neo4j.py`, `enrichment/documents/load_to_neo4j.py`. Once 102'.f-style cutover has run cleanly on ≥2 more customer boxes without needing the fallback path.
- **Retire the `schema_v*.sql` files** — they're now captured in the baseline. Move to `db/history/` for provenance or delete outright.
- **Rebuild cadence** — currently manual. Consider: bi-weekly automated pipeline that regenerates all three goldens against a canonical clean-state Postgres, commits + pushes if there are drifts.
- **CI enforcement of pre-commit** — the hook is opt-in (`git config core.hooksPath scripts/git-hooks`). CI check that rejects a PR touching authoring sources without matching golden updates would harden this.
- **Chroma rebuild without private/** — could produce a "5-collection" golden that boxes without ISO/EDPB PDFs can still ship. Useful for open-source distribution of a partial catalog.

## Related

- [[ship-103-prime-arc-retrospective-2026-09-01]] — LFS distribution arc (paired with 102'.c / 102'.f)
- [[ship-101-prime-a-provider-agnostic-prep]] — provider-agnostic pattern that this arc built on
- `db/AUTHORING.md` — canonical documentation of authoring workflows shipped in 102'.d
