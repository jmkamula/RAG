---
name: ship-29-prime-a-consolidate-generators-design-2026-07-24
description: "Ship 29'.a — design memo for consolidating topic-anchor injection into gen_leaf_scan_catalog.py; retires the specialized generate_27701_fingerprints.py; eliminates the multi-generator drift risk that bit Ship 28'.b"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 29'.a — opens Ship 29 arc (generator consolidation).
Direct follow-on to Ship 28's mid-arc regression, where a
bulk-regen pass using `gen_leaf_scan_catalog.py` (general)
silently reverted Ship 17'.b/c's topic-anchor injection from
`generate_27701_fingerprints.py` (specialized). Ship 29
consolidates the two generators so future bulk-regens can't
hit this class of drift.

## What lives where today

**`scripts/gen_leaf_scan_catalog.py`** (general, per-leaf CLI):
- Emits fingerprint YAMLs for a single control-ref or leaf-id
- Multi-source keyword generation (id-tokens + description
  phrases + role-prefix hints + evidence-type scaffolds)
- Ship 28'.b: adds redundant-singleton suppression
- No topic-anchor injection

**`scripts/generate_27701_fingerprints.py`** (specialized,
bulk by standard × family):
- Emits fingerprint YAMLs for a standard × family combo
- Multi-source keyword generation (subset of what
  gen_leaf_scan_catalog does)
- Ship 17'.b/c: topic-anchor injection from `RequirementNode.title`
- Batch renaming: `--standard ISO27001:2022` etc.
- Ship 28'.b restoration: re-run to restore anchors after
  bulk-regen hit

**The drift risk**: any bulk-regen that doesn't run the
specialized generator AFTER the general one will regress
topic-anchor injection on 27701 program_review + applicable_
scope + ISO27001 program_review + GDPR program_review +
applicable_scope (6 family × standard combos).

## The consolidation

Move topic-anchor injection from specialized into general;
delete the specialized generator (or turn into a thin shim
during migration).

### 1. Port topic-anchor helpers

Copy from `generate_27701_fingerprints.py` into
`gen_leaf_scan_catalog.py`:
- `_TITLE_META_NOISE` set (9 tokens)
- `_topic_anchor_tokens(title, max_tokens=2)` extractor
- `_augment_with_anchor(kw_set, anchors)` per-set injection

### 2. Extend `_fetch_leaves` Cypher to include RequirementNode.title

Current query:
```cypher
MATCH (er:EvidenceRequirement {id: $leaf_id})
OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
RETURN er.id, er.control_ref, er.standard_id, er.evidence_type,
       er.title AS title,
       collect(...) AS items
```

Extended:
```cypher
MATCH (er:EvidenceRequirement {id: $leaf_id})
OPTIONAL MATCH (rn:RequirementNode {
    ref: er.control_ref, standard_id: er.standard_id})
OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
RETURN er.id, er.control_ref, er.standard_id, er.evidence_type,
       er.title AS title,
       rn.title AS control_title,          -- NEW: for anchor injection
       collect(...) AS items
```

### 3. Wire anchor injection into `_starter_excerpt_keywords`

The specialized generator applied anchors per keyword set. Ship
29 does the same in the consolidated generator:

```python
# After building `suggestions` and applying redundant-singleton
# suppression (Ship 28'.b), inject topic anchors.
anchors = _topic_anchor_tokens(control_title)
if anchors:
    suggestions = [
        _augment_with_anchor(kw, anchors) for kw in suggestions
    ]
```

Placement: AFTER the singleton suppression, BEFORE the `[:8]`
cap. This way an anchor never causes a multi-token entry to be
downgraded to a "singleton-covered" entry.

### 4. Naming clarification (user question 2026-07-24)

Both scripts write to `db/must_fingerprints/*.yaml` and get
loaded by `rag/intake/leaf_driven_scan.py`. Same directory,
same schema, same consumer. Two names for one artefact
class:
- "**fingerprint**" = the domain concept (a YAML with keyword-
  set match patterns per MUST item)
- "**leaf scan**" = the consumer subsystem name

Naming is historical, not semantic. Consolidation is the
right move; keeping two generators is the drift risk itself.

### 5. Retirement of specialized generator

**Delete** `generate_27701_fingerprints.py`. Ship 17'.b/c's
functionality (topic-anchor injection + bulk flags) gets
absorbed into the consolidated generator via:
- ported topic-anchor logic (§1 above)
- new CLI flags on the general generator (§6 below)

Ship 28'.b's `scripts/regenerate_leaf_scan_singleton_fix.py`
also becomes redundant (its `--all-auto-generated` behavior
is now a flag on the main generator). Delete both.

### 6. New CLI flags on `gen_leaf_scan_catalog.py`

Existing:
- `--leaf req:X:Y` — one specific leaf
- `--control A.5.15` — one control's leaves
- `--write` — write to disk vs stdout
- `--force` — overwrite existing files

New (absorbed from specialized generator + regen script):
- `--standard ISO27001:2022` — all leaves in a standard
- `--family SUBSTR` — filter by leaf_id substring
  (e.g. `program_review`, `applicable_scope`)
- `--all-auto-generated` — walk `db/must_fingerprints/`,
  regenerate every file whose header has
  `# Auto-generated` marker (Ship 17'.b's discipline)
- `--dry-run` — report what would change without writing

### 5. Regenerate all 352 auto-generated files

Same discipline as Ship 28'.b — respect `_is_auto_generated`
header guard. Verify via `audit_fingerprints.py`:
- single_token count: should stay at 0 for auto-generated files
- Cross-leaf collisions for program_review families: should
  match Ship 17'.b/c's post-anchor-injection numbers (44 →
  10 gate triggers; specific values verifiable)

## Design decisions locked in 29'.a

1. **Delete, don't deprecate** — `generate_27701_
   fingerprints.py` becomes redundant; keeping it adds
   permanent drift risk.

2. **Anchor injection applies to ALL files, not just 27701**
   — the general generator was already treating some file
   families different from others (register scaffolds via
   `_ROLE_PREFIX_HINTS`). Adding topic anchors to every leaf
   is the same discipline extended to a broader surface.

3. **Anchor source is `RequirementNode.title`** — same as
   Ship 17'.b/c. RN.title is the canonical control name; ER
   title is per-leaf (often less distinctive).

4. **Anchor injection AFTER singleton suppression** —
   redundant-singleton fix (Ship 28'.b) runs first; anchor
   injection acts on the surviving multi-token sets.

5. **Bulk regen expected to produce more changes than
   Ship 28'.b** — every auto-generated file gets anchor
   injection now, not just the 6 family × standard combos
   Ship 17'.b/c covered. Expected diff: ~352 files with
   at least one anchor-augmented keyword set.

## What Ship 29 does NOT do

- **Change the redundant-singleton suppression** — Ship
  28'.b's fix stays as-is
- **Touch hand-authored files** — `_is_auto_generated` guard
  preserved
- **Modify runtime extraction gates** — Ship 16'.b + 6'.b
  gates unchanged
- **Change fingerprint file format** — same YAML shape

## Sub-arc plan

### 29'.b — Implement + regen + retire

- Port `_TITLE_META_NOISE`, `_topic_anchor_tokens`,
  `_augment_with_anchor` into `gen_leaf_scan_catalog.py`
- Extend `_fetch_leaves` Cypher to fetch `rn.title`
- Wire anchor injection into `_starter_excerpt_keywords`
- Regenerate all 352 auto-generated files
- Delete `scripts/generate_27701_fingerprints.py`
- Verify via `audit_fingerprints.py`:
  * single_token count stays near 0 in auto-gen
  * program_review family collisions match Ship 17'.b/c
    post-anchor-injection (~10 leaf collisions per anchor
    class, not 148+)

### 29'.c — Eval + arc retrospective

Full eval regression check. Retro codifies the
consolidation discipline.

## Ship 29 progress

| Sub-arc | Status |
|---|---|
| **29'.a Design memo (this)** | **✓** |
| 29'.b Consolidate + regen + retire | next |
| 29'.c Eval + retrospective | pending |

## Related

- [[ship-28-prime-arc-retrospective-2026-07-24]] — the arc
  whose mid-arc regression motivates this consolidation
- Ship 17'.b/c — the specialized generator work Ship 29
  absorbs into the general path
- Ship 28'.b — the redundant-singleton suppression Ship 29
  preserves
