---
name: ship-29-prime-arc-retrospective-2026-07-24
description: "Ship 29' arc closer — consolidated fingerprint generators. Two scripts writing to db/must_fingerprints/ merged into one (gen_leaf_scan_catalog.py) with rich CLI (--standard, --family, --all-auto-generated). 395 auto-gen files regen'd with anchor injection; 201 hand-authored preserved. Eval 231/232 baseline held. Codifies: multi-path-to-same-destination is drift-by-construction — collapse the paths, don't add discipline."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 29' arc retrospective — 3 sub-arcs delivered in one session
(2026-07-24) closing the multi-generator drift risk Ship 28'.b's
mid-arc regression made concrete.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 29'.a | Design memo + shape clarification (user Q: naming) | 4188186 (memo) + ff1fed9 (git-add) |
| 29'.b | Port anchor helpers + rich CLI + 395-file regen + 2-script retirement | ff1fed9 |
| **29'.c** | **Eval + retrospective (this doc)** | pending |

## The consolidation in one paragraph

Two scripts both wrote to `db/must_fingerprints/*.yaml` and both fed
`rag/intake/leaf_driven_scan.py`. Naming was historical, not
semantic — "fingerprint" was the domain concept, "leaf scan" was
the consumer subsystem name. Ship 17'.b/c had added topic-anchor
injection only to the specialized generator (`generate_27701_
fingerprints.py`); the general generator (`gen_leaf_scan_catalog.py`)
lacked it. Ship 28'.b's bulk-regen used the general generator and
silently reverted anchor injection on 27701 files, requiring a
mid-arc restoration. Ship 29 consolidates: ported the anchor
helpers into the general generator, absorbed the specialized
generator's `--family` / `--standard` interface as new CLI flags,
absorbed Ship 28'.b's ad-hoc bulk-regen script as
`--all-auto-generated`, deleted both.

## Numbers

**Bulk regen:**
| Metric | Value |
|---|---|
| Total files in `db/must_fingerprints/` | 598 |
| Auto-generated (regeneratable) | 397 |
| Hand-authored (guarded) | 201 |
| Files rewritten by Ship 29'.b | 395 |
| Files byte-identical (no rewrite) | 2 |
| Files with hand-auth-guard triggered | 201 (all skipped) |

**Anchor distinctiveness verification** (sampled):
| Leaf | Anchor from RN.title |
|---|---|
| req:A.7.2.1:program_review | `identify` |
| req:A.7.2.4:program_review | `obtain` |
| req:A.7.4.4:program_review | `pii` |

**Cross-leaf collision at motivating pattern:**
- `[review, date, planned, interval]` — Ship 17'.b's original
  motivating example. 48 leaves pre-anchor, 0 leaves post-Ship-29.

**Singleton audit:**
- Auto-gen singleton entries: 0 (unchanged from Ship 28'.b baseline)
- Hand-authored singletons: 195 (unchanged — hand-auth guard held)

**Eval:**
- **231/232 PASS + 1 WARN (#200) + 0 FAIL** — identical to Ship 28'.b
- Ship 29 changed only catalog data + generator surface; no runtime
  code paths altered

## What Ship 29 did NOT do

- **Change fingerprint file format** — same YAML shape
- **Touch runtime gates** — Ship 16'.b + Ship 11'.b + Ship 16'.c
  unchanged
- **Modify hand-authored files** — 201 guarded, 0 touched
- **Re-audit fingerprint quality** — Ship 27's `audit_finding_quality.py`
  stays authoritative
- **Update the "Auto-generated skeleton — review and tighten before
  commit" header prose** — user considered but explicitly kept scope
  focused on consolidation

## Codified lessons

### 1. Multi-path-to-same-destination is drift-by-construction

Two scripts writing to `db/must_fingerprints/` was justified at the
time — the specialized generator was quick to spin up for 27701
gap-close, the general generator was already the per-leaf CLI. Both
worked. The invariant broke when a bulk-regen chose one path and
silently reverted the other's per-file work.

**Rule**: when two code paths share a mutation surface, they'll
drift on any bulk operation that doesn't route by ownership. Fixing
this with routing discipline is fragile — the discipline gets
forgotten. Consolidation is the durable fix; the code path IS the
routing.

This is a stronger statement than "avoid multiple generators."
The general form: **if a bulk operation is possible on your output
surface, all paths that write to that surface must be equivalent
or one path must be deleted.**

### 2. Naming clarity emerges from usage confusion

User pushback ("i'm confused, where do we deploy leaf_scan and
where do we deploy fingerprints") surfaced that BOTH generators
produce the SAME artefact class — "fingerprint" is the domain
concept, "leaf scan" is the consumer subsystem name. Once that
was written down, the consolidation shape became obvious ("one
generator + rich CLI"). Before that, the shape decision drifted
between three plausible options (delete, deprecation shim, or
retain both with shared module).

**Rule**: when a user's clarifying question exposes that YOU also
don't fully understand the naming, treat that as evidence the
naming itself is wrong. Document the actual semantic before
proposing structure changes.

### 3. Bulk-mode should be a first-class CLI mode

Ship 28'.b spun up an ad-hoc `regenerate_leaf_scan_singleton_fix.py`
script because the main generator didn't support "walk the catalog
dir." Every arc that needs bulk regen will produce one of these
scripts unless the main tool has the mode built in. Ship 29
absorbs it as `--all-auto-generated`.

**Rule**: recurring ad-hoc scripts that share input/output with a
main tool are a signal the main tool needs a mode, not a signal
that ad-hoc scripts are fine.

### 4. Post-Ship-28 concreteness was load-bearing

Without Ship 28'.b's mid-arc regression, "consolidate two
generators" would have been abstract nice-to-have prioritization.
The mid-arc regression made the drift risk concrete and immediate
— consolidation happened next-day. General lesson: **incident data
motivates consolidation better than architectural prose does.**

Ship 28'.b retrospective explicitly named this as a follow-on
candidate ("Consolidate topic-anchor injection into
`gen_leaf_scan_catalog.py`"); Ship 29 opened the same day. Fast
follow-through on incident-motivated cleanup keeps the "why"
alive; delayed follow-through lets the "why" fade.

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 29'.a | Design memo — root cause, consolidation shape, retirement plan | Shape revised mid-arc after user pushback on retirement rationale; landed at "one generator + rich CLI" |
| 29'.b | Port anchor helpers, extend Cypher, add CLI flags, regen 395 files, delete 2 scripts | Auto-gen singleton = 0; hand-auth guard held; anchor distinctiveness verified per-leaf |
| **29'.c** | **Eval + retro (this)** | **Baseline held 231/232; arc closed** |

## Deferred / follow-on candidates from Ship 29

- **Curator arc for the 195 hand-authored singletons** — remain
  since Ship 28; each is a curator decision that could be replaced
  with multi-token variants OR added to `_NEVER_EMIT_SINGLETON`.
  Not a bulk operation.
- **Re-extract Ship 10 5-doc corpus** to measure post-Ship-29
  grounding_method distribution shift — Ship 27's audit tool
  remains ready; Ship 29 broadened anchor coverage from ~6 combos
  to 395 files so extraction match rates should shift.
- **Refresh the "Auto-generated skeleton — review and tighten
  before commit" header prose** — after Ship 29, these files are
  the production state, not a review checkpoint. User raised this
  as possible in-scope; explicitly deferred to keep Ship 29 focused.
- **CI grep guard for `generate_27701_fingerprints`** — retired
  script name might be re-invented; a grep in CI could catch
  accidental reintroduction. Low priority; single occurrence pattern.

## Related

- [[ship-28-prime-arc-retrospective-2026-07-24]] — the mid-arc
  regression that made Ship 29 concrete
- [[ship-17-prime-arc-retrospective-2026-07-23]] — the specialized
  generator work Ship 29 absorbed into the general path
- [[ship-27-prime-arc-retrospective-2026-07-24]] — grounding_method
  quality signal; Ship 29 kept the deterministic-first invariant
- [[ship-16-prime-arc-retrospective-2026-07-22]] — the two-layer
  runtime gate Ship 29 preserved untouched
