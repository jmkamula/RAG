---
name: ship-103-prime-arc-retrospective-2026-09-01
description: Ship 103'.a — Git LFS distribution for the 141 MiB Chroma golden tar. Chosen over Docker Hub / GitHub Releases / SCP because LFS keeps golden version atomic with git commit SHA and needs zero install.sh fetch logic beyond a defensive pointer-file sanity check. Verified in Ship 102'.f customer-box cutover.
metadata:
  type: project
---

# Ship 103' — Git LFS distribution for large-binary goldens (2026-09-01)

## Framing

Ship 102'.c produced a working Chroma golden — a 141 MiB tar+gzip of `chroma_db/` covering all 9 collections (5 rebuildable from Neo4j + 4 whose sources are copyrighted PDFs in gitignored `private/`). Regular git rejects files >100 MiB per GitHub's hard limit. Ship 102'.e made install.sh consume the tar when present but left the "how does it get onto the customer box" question open.

Ship 103'.a answers that question.

## The choice — LFS vs 4 alternatives

Considered:

| Option | Verdict | Reason |
|---|---|---|
| **Git LFS** | **CHOSEN** | Zero install.sh fetch logic. Golden version atomic with git commit SHA. Same GitHub URL + login for both source and blobs. Standard tooling (`git-lfs` in Ubuntu apt). |
| Docker Hub + skopeo | Runner-up | Would work; free tier is more generous (unlimited public pulls); jmkamula/arioncomply-goldens image cleanly namespaces the artifacts. But decouples golden from git commit (image tag ≠ SHA), and adds a second distribution channel to reason about. |
| GitHub Releases | Not chosen | Requires an explicit release step (`gh release create`) — adds workflow friction. Golden falls out of `git pull`. |
| SCP / rsync manual | Not chosen | Doesn't scale beyond the first customer install. No versioning. |
| Split tar into <100 MB chunks | Not chosen | Hacky. Bloats git history per rebuild. Harder to reason about. |

**Why LFS won:** the project's source-of-truth is git. Every commit SHA has one set of goldens by construction (the LFS pointers in the tree reference specific LFS SHAs). No possibility for "the docker image is v1.5 but the code is at v1.6" drift. Free tier (1 GB storage + 1 GB bandwidth / month = ~7 fresh customer installs / month) is generous for the target use case.

## What shipped

**103'.a** (`8f57810f`)

- **`.gitattributes`** — new. Tracks `db/baseline/chroma_prebuilt.tar.gz` and `db/baseline/*.meta.json` as LFS. `git-lfs` filter transforms them on add/commit.
- **`db/baseline/chroma_prebuilt.tar.gz + .meta.json`** — moved from local-only (Ship 102'.c gitignore) to LFS-tracked in the git tree. The tree stores 3-line pointers (version, oid sha256, size); GitHub's LFS backend stores the 141 MiB blob.
- **`.gitignore`** — the entries that were keeping the tar local got commented out. Left as reference so future readers understand the pre-LFS state.
- **`deploy/install.sh` step 7** — **pointer-file sanity check**. If `chroma_prebuilt.tar.gz` exists but is under 1 MB, treat it as an LFS pointer that wasn't hydrated, `fail` with the exact recovery commands:

  ```
  sudo apt install git-lfs
  git lfs install
  git -C /data/arioncomply lfs pull
  ```

  Cheap defensive check that turns a mysterious "install broke halfway" into a clear "install LFS first."
- **`db/AUTHORING.md`** — new "Git LFS setup" section documenting the one-time `apt install git-lfs && git lfs install` step per clone. Documents free-tier math for future capacity planning.
- **`scripts/git-hooks/{post-checkout,post-commit,post-merge,pre-push}`** — LFS boilerplate hooks installed by `git lfs install`. Committed alongside the pre-commit hook so fresh clones with `core.hooksPath` already set don't have to re-run `git lfs install --force`.

Then Ship 102'.f (`98c09111` — probes, plus the customer-box run) verified the flow works end-to-end:

- Customer box: `sudo apt install git-lfs && git lfs install` → `git lfs pull` fetched the 141 MB tar via LFS.
- SHA-256 on customer box exactly matches dev-host: `4823f7289af865367d90ad91d84d75f4c920efeff6094d97636d5abc346c2fd5`.
- install.sh step 7 extracted the tar into `chroma_db/`; all 9 collections + doc counts came up correct (Chroma probe: `PARITY — all 9 collections present with expected counts`).

## Codified patterns

**Lesson 170: LFS is the natural fit for git-provenanced large-binary artifacts.** When the artifact is DERIVED from the source repo (Chroma tar ≡ live chroma_db at a specific dev-host state ≡ pre-commit-triggered from Neo4j changes), the artifact SHOULD be versioned atomically with the source. LFS does that by construction; every other distribution mechanism requires manual discipline to keep artifact and code aligned.

**Lesson 171: pointer-file sanity check as fail-loud recovery pattern.** When a large binary artifact is delivered via LFS pointer + hydration, the pointer file (~130 bytes) will look "present" to naive existence checks but produce garbage when extracted. Detect this early with a size threshold check (`stat -c%s < 1_000_000` when the real file should be 141 MiB). Fail loud with the exact recovery commands. Turns a 20-minute "why is Chroma corrupt" debug into a 30-second "oh, LFS wasn't initialized."

**Lesson 172: same-URL distribution beats multi-channel.** Docker Hub was a legitimate alternative (jmkamula org already exists, free tier unlimited pulls, standard tool). It lost because it introduces a second distribution channel — customers would need to know both `github.com/jmkamula/RAG` and `hub.docker.com/r/jmkamula/arioncomply-goldens` were parts of the same project. Same-URL distribution (LFS at `github.com/jmkamula/RAG`) removes that cognitive load and consolidates auth to one login.

**Lesson 173: bandwidth math is the real free-tier constraint.** LFS free tier storage math (1 GB) is very generous — we're at ~14% with one 141 MiB tar. But bandwidth (1 GB / month = ~7 fresh installs) is tighter. For a compliance product with occasional customer engagements, likely fine. For higher-volume distribution, the $5/month data pack (50 GB bandwidth) is trivial. Docker Hub's unlimited-pulls model wins on bandwidth if that ever becomes the binding constraint.

## Free-tier math (for future planning)

Per fresh customer install:
- LFS bandwidth used: 141 MB (Chroma tar) + tiny (meta json)
- LFS storage delta: 0 (existing blob reused)

Per golden rebuild that changes the tar (Ship 102'.c build script re-runs):
- LFS storage delta: ~141 MB (new blob) — old blob eventually GC'd but stays counted for some window
- LFS bandwidth: ~141 MB (upload from dev host)

At current cadence (arc-driven rebuilds, ~monthly), storage usage stays under 500 MB. Bandwidth ~1 GB / month across dev push + customer pulls. Fits free tier comfortably.

## Deferred

- **Docker Hub as backup distribution channel** — could be added if bandwidth ever binds. Small work (Dockerfile.goldens + publish script + install.sh fallback fetch). Not needed today.
- **LFS pruning cadence** — old golden blobs still count against storage until GC'd. Currently manual (`git lfs prune`). Consider running periodically on dev host.
- **Customer-box `git lfs install` in install.sh** — install.sh currently detects the pointer + fails with instructions. Could go further and auto-`apt install git-lfs && git lfs install && git lfs pull` if not present. Trades user intent for install robustness. Design decision deferred.

## Related

- [[ship-102-prime-arc-retrospective-2026-09-01]] — the 3-store golden-image consolidation this arc distributes
- `db/AUTHORING.md` — the LFS setup section documents the one-time customer setup step
- `scripts/dev/probe_chroma.py` — the parity check that confirmed LFS delivery works on the customer box
