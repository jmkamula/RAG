---
name: ship-20-prime-d-family-c-2026-07-23
description: "Ship 20'.d — Family C intro + N related cards (capped 15) wired to 3 list-shaped short-circuits; empty-intro-scan bug fix in build_short_circuit_structured"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 20'.d — third delivery sub-arc of Ship 20. 3 list-shaped
short-circuit sites now emit intro + N related cards (capped
15) with each card carrying full Neo4j title + posture verdict
+ leaves checklist. Commit `14e747e`.

## Sites migrated

- **stage1_review** (line 2308)
  * `list_queue` action → intro + top-15 refs from
    `_s1_listing[:15]`
  * `list_one` / `approve` / `reject` → Family B shape (1 card)
- **stage2_approval** (line 2376) — same shape as Stage-1
- **posture_enumeration_deterministic** (line 2678) — intro
  carries enumeration prose + top-15 refs from `_det_refs`

All sites preserve `attach_templates=False`, `attach_advisory=
False`. `answer_text` unchanged.

## Bug fix: empty-intro-scan in build_short_circuit_structured

First Ship 20'.d smoke test on `show pending findings` returned
**34 related cards despite the coded 15-cap**. Root cause:
`build_related_cards()` calls `collect_all_refs(structured)`
which scans `intro.text + actions[].body` for refs. The
Stage-1 `render_stage1_answer` prose mentions all 42 pending
controls by ref in the prose. Scan picked all up, unioned with
caller's `extra_refs` (15), produced 34 unique cards after
Neo4j filtering.

Fix: pass EMPTY `intro.text` to `build_related_cards` during
augmentation; restore the real intro after. Short-circuits are
authoritative about which refs to surface — the caller has
already decided (via `primary_ref` + `extra_refs`). LLM path is
different: LLM prose IS the source of cited refs, so it stays
scanned.

One-line change in `build_short_circuit_structured`; preserves
LLM path behaviour.

## Verified end-to-end

- `show pending findings` → intro (3705 chars of Stage-1 render
  prose) + exactly 15 related cards (top by pending count), each
  with Neo4j title + posture verdict + leaves checklist.
- `show me the timeline for A.5.18` → intro + 1 card (Family B
  path unaffected by the fix).
- `what engine verdicts need review?` → 0 cards (empty listing
  on this tenant — correct).

## Codified pattern: architectural asymmetry via empty-input

LLM path: prose is authoritative for refs (LLM chose them via
JSON output). `collect_all_refs` scanning intro is by-design.

Short-circuit path: prose is descriptive of a caller-provided
ref set. Passing empty intro during scan encodes this
asymmetry cleanly in one line, without adding a parameter or
branching on caller identity.

## Ship 20 progress

| Sub-arc | Status |
|---|---|
| 20'.a Design memo | ✓ (9846eb6) |
| 20'.b Family A | ✓ (96031b8) |
| 20'.c Family B | ✓ (db9554f) |
| **20'.d Family C (this)** | **✓ (14e747e)** |
| 20'.e Eval + retro | next |

## Related

- [[ship-20-prime-a-short-circuit-design-2026-07-23]] — design
- [[ship-20-prime-b-family-a-2026-07-23]] — Family A
- [[ship-20-prime-c-family-b-2026-07-23]] — Family B (contains
  the CaseFileShim + fetch_control_metadata + builder used here)
