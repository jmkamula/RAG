---
name: ship-17-prime-c-regenerate-remaining-2026-07-23
description: "Ship 17'.c — generalized generator to any standard; regenerated ISO 27001 + GDPR auto-gen families; Ship 16'.b gate triggers 19→10 (77% total Ship 17 reduction)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 17'.c — extended the regenerator to multi-standard,
regenerated ISO 27001 + GDPR auto-gen `program_review` +
`applicable_scope` families. Third sub-arc of Ship 17.

## Generator changes

- **`fetch_leaves(driver, standard_id)`** — parameterised
  version of `fetch_27701_leaves`. Backward-compat alias
  `fetch_27701_leaves(driver)` retained for existing callers.
- **`--standard` CLI flag** (default `ISO27701:2019`) — service
  any enrolled standard from a single generator. Ship 17'.b's
  `--family` + `--force` flags remain compatible.
- `_yaml_content()` call site now passes `args.standard` instead
  of the hardcoded `"ISO27701:2019"`.

## Regenerated files

| Standard | Family | Written | Hand-guarded |
|---|---|---|---|
| ISO27001:2022 | program_review | 65 | 25 (hand-authored, skipped) |
| ISO27001:2022 | applicable_scope | 0 | — (no ISO 27001 leaves match this family in Neo4j) |
| GDPR:2016/679 | program_review | 28 | 14 |
| GDPR:2016/679 | applicable_scope | 16 | 6 |
| **Total this arc** | **109** | **45** |

Combined Ship 17'.b + 17'.c: **207 files regenerated**, **65
hand-authored files skipped** by the auto-generated guard —
zero curator work lost.

## Verification — Ship 16'.b gate triggers

Full trajectory across Ship 17:

| Milestone | Would-trigger-gate | Δ |
|---|---|---|
| Pre-Ship-17 (Ship 16'.b baseline) | 44 | — |
| Post-Ship-17'.b (27701) | 19 | −25 (57%) |
| **Post-Ship-17'.c (27001 + GDPR)** | **10** | **−9 (17% more)** |

**Ship 17 total: 44 → 10 gate triggers, 77% reduction.**

## What the remaining 10 collisions ARE

All 10 remaining gate triggers are **register-shape templates**
— tokens intentionally added by `gen_leaf_scan_catalog.py`'s
`_EVIDENCE_TYPE_SYNONYMS` to match per-row / per-entry content
across ALL register leaves:

| Token set | Leaves | Provenance |
|---|---|---|
| `[per, row]` | 10 | register-shape template |
| `[each, row]` | 10 | register-shape template |
| `[named, owner]` | 9 | statement_of_applicability template |
| `[column, containing]` | 8 | register-shape template |
| `[each, entry]` | 7 | register-shape template |
| `[date, review]` | 6 | mixed — some hand-authored |
| `[identifier, request, row, unique]` | 6 | consent/DSAR register template |
| `[identifier, row, subject]` | 6 | consent/DSAR register template |

These are DELIBERATE cross-register templates. Filtering them
would defeat their purpose (recognizing per-row register
content). Ship 16'.b's runtime gate catches these matches with
`dropped_low_specificity` telemetry — belt and suspenders
working as designed.

## What did NOT ship

- **Regenerate register-shape templates** — would break their
  intended cross-register matching. Would need a broader
  redesign (per-register-family sub-templates) that's out of
  scope.
- **Regenerate `_review_record` / `_procedure` / other
  auto-gen families** — these are less collision-prone than
  program_review / applicable_scope; not surfaced in the top-10
  gate triggers. Deferred; the audit script can be re-run per
  need.
- **Retire Ship 16'.b runtime gate** — kept as belt and
  suspenders. Post-Ship-17 it fires far less often but still
  catches the intentional register templates + any future
  auto-gen additions.

## Ship 17 progress

| Sub-arc | Status |
|---|---|
| 17'.a Regeneration strategy + generator audit | ✓ |
| 17'.b Fix generator + regenerate worst-offender families | ✓ |
| **17'.c Regenerate remaining families + verify against gates** | **✓ (this doc)** |
| 17'.d Measurement + arc retrospective | next |

## Related

- [[ship-17-prime-a-regeneration-design-2026-07-23]] — design
  memo
- [[ship-17-prime-b-regenerate-worst-families-2026-07-23]] —
  27701 regeneration (Layer 1 of the fix)
- [[ship-16-prime-b-specificity-gate-2026-07-22]] — runtime
  gate whose trigger count Ship 17 reduced 77%
- Ship 17'.d: measurement (re-extraction on Ship 10 5-doc set
  + bridge-side dry-run) + arc retrospective
