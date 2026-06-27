---
name: template-xlsx-roundtrip-hardening-2026-06-26
description: "SHIPPED 2026-06-26: defensive hardening for xlsx round-trip. Filename-fallback identification (recovers leaf_id from filename when _arion_meta deleted by reverse-lookup against templates table) + column-count validation (rejects width mismatch on both paths, no silent misbinding). Closes two of three real-world tenant-tampering failure modes. Verified on 3-case smoke (normal / meta-deleted / width-mismatch)."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

Two defensive layers added to `_read_templated_xlsx_meta` in
`rag/intake/readers.py`:

### Filename-fallback identification

When `_arion_meta` is missing (tenant deleted the hidden sheet —
intentional or accidental), recover leaf_id from the filename:

- `_filename_to_leaf_id(filename)` strips `.xlsx`/`.xlsm` + common
  tenant-added suffixes (`(1)`, `(2)`, ` - copy`, `_filled`,
  `_edited`, `_v2`), then reverse-looks-up against the `templates`
  table for a leaf_id whose canonical download filename matches.
- `_derive_template_columns(leaf_id)` reads the template body from
  the `templates` table and extracts column + doc_field ordinals
  via the same helpers `xlsx_renderer.py` uses at download time —
  single source of truth, no schema duplication.
- Source telemetry: `"meta"` vs `"filename_fallback"` distinguishable
  in trace + extraction_metrics.

Path is cold for happy-path uploads (most have `_arion_meta`); lazy
imports + lazy connections keep it cheap.

### Column-count validation

After reading meta (or recovering via fallback), check Register
sheet header width against canonical `column_count`. Mismatch →
return None + warning log → file falls through to generic workbook
lane (zero findings — safe default — no misbinding).

Applies to BOTH paths uniformly: the column metadata is canonical
either from `_arion_meta` or from the template body lookup; if the
visible Register doesn't match it, the binding would corrupt.
Better to reject + tell the tenant than to silently misbind.

## Non-obvious decisions

### Reverse-lookup, not pattern-parsing

`leaf_id → filename` was lossy: `req:A.5.9:asset_inventory` →
`A_5_9_asset_inventory.xlsx`. The forward transform replaces `:` and
`.` with `_` — but `_` is already a separator in the slug, so we
can't parse the filename back unambiguously.

Reverse-lookup is unambiguous: iterate over `templates.leaf_id`,
compute the expected filename for each, find the match. Linear in
template count (~645) but only fires when meta is missing.

### Conservative on column-count mismatch (reject, don't try to align)

Could be tempting to try repair ("3 cells in the header but meta says
6 — maybe they hid columns?"). Rejected: better to bind 0 cells
than to bind 6 cells to the wrong MUSTs. Auditor cares about
correctness, not coverage.

### Filename-fallback doesn't need explicit tenant_id check

`_arion_meta.tenant_id` was the source of truth in the canonical
path. With fallback there's no source of truth for `tenant_id` (the
field is `""`). The upload is still scoped by auth — the
X-API-Key resolves to a tenant_id and RLS prevents any cross-tenant
impact. Filename-fallback can't be exploited to write into another
tenant's scope.

Could a malicious tenant craft a filename like
`A_5_9_asset_inventory.xlsx` with random content to mark themselves
Comply on A.5.9? Yes — but they can already do that via form
inputs (`POST /api/v1/dashboard/control/A.5.9/template`) or by
hand-editing the markdown. Not a new attack surface.

### Suffix stripping is heuristic + conservative

`_filled`, `(1)`, `_copy`, `_edited`, `_v2` cover the common Excel
auto-suffixes. False negatives (failed fallback) are safe (file
falls through). False positives (wrong leaf binding) are the
worry — column-count validation is the structural backstop.

## Failure modes closed vs still open

Closed:
- `_arion_meta` deleted → filename-fallback recovers
- Column added or deleted → column-count validation catches
- Column reordered → still binds by ordinal (was already safe)

Still open:
- Tenant pastes whole rows from another sheet → treated as data
  rows, auto-approved. Future: "preview before commit" UX.
- Tenant edits `meta.leaf_id` to claim a wrong leaf → their own
  scope (RLS); auditor would catch it on review. Not security.
- Filename without extension → `_filename_to_leaf_id` strips
  `.xlsx`/`.xlsm` so missing-extension upload falls through. Rare;
  defer.

## Verified

3-case smoke (`/tmp/build_three_cases.py` → `/tmp/A_5_9_asset_inventory*`):

| Case | Setup | Path | Findings | Behaviour |
|---|---|---|---|---|
| 1 | Normal fill | `_arion_meta` | 6 | Standard binding ✓ |
| 2 | Meta deleted, filename intact | filename-fallback | 6 | Recovered via filename → templates lookup; INFO log emitted ✓ |
| 3 | Meta intact, Register width=5 (col deleted) | rejected | 0 | Width mismatch caught; fell through to generic lane ✓ |

Eval pending; chat path untouched.

## Related

- [[template-xlsx-roundtrip-phase-b-2026-06-26]] — the round-trip
  this hardens. That entry's failure-mode table now has 2 of 3
  worst-case scenarios closed.
- [[template-native-formats-xlsx-2026-06-26]] — the download side
  that produces `_arion_meta` and the canonical filename.
- [[templated-lane-discipline-2026-06-25]] — the auto-approve trust
  model this builds on.
- [[feedback-validate-the-denominator]] — same conservatism instinct:
  better to surface a clear gap (zero findings + warning) than to
  silently produce wrong data.
