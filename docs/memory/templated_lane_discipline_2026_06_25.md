---
name: templated-lane-discipline-2026-06-25
description: "SHIPPED 2026-06-25: two-part discipline for the templated intake lane. (1) Auto-approve templated rows at write — bypass Stage-1 HITL since tenant authored the marker-bearing doc. Authored_by=uploading-user uuid; /api/v1/stage1/auto-approved visibility panel preserves audit. (2) Edit-zone markers (<!-- EDIT-ZONE-START/END item:X -->) wrap the tenant-edit zone at render time; extractor binds only zone content. Fixes circular-counting bug where re-upload of unedited template was binding guidance prose + prefilled prior evidence as new authorship."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## Context — why two changes at once

The templated intake lane was shipping with two latent issues that
surfaced during the closed-loop test on Arion:

1. **HITL friction**: Every templated row landed `pending` and went
   through Stage-1 review. Tenants were being asked to approve
   evidence they themselves authored — HITL theatre, not signal.

2. **Circular counting**: Re-uploading an unedited (or prefill-only)
   template produced findings for every section. The fast-path
   treated v2 guidance prose + prefilled prior evidence as new
   tenant authorship. Wizard's per-MUST completion % inflated;
   A.5.15 jumped from 4/6 → 6/6 on a re-upload that contained
   nothing new.

Both fixed in this session: commits `bd8f2a9` (auto-approve) and
`20f6811` (edit-zone markers).

## Decision 1 — auto-approve templated at write

HITL Stage-1 is a gate for INFERENCE uncertainty:

| Source | Why HITL exists |
|---|---|
| `extracted` (LLM) | LLM can hallucinate / paraphrase / mis-bind |
| `workbook` | Deterministic parse, but fingerprint matches need eyes |
| `xfw_bridge` | Cross-framework inference — Neo4j edge isn't tenant action |
| `leaf_scan` | Heuristic back-bind |
| **`templated`** | **Tenant edited a marker-bearing doc and uploaded — no inference** |

The tenant has triple-authored intent for every `templated` row:
downloaded the template, wrote under explicit `<<MUST item:X>>`
markers, uploaded the result. A Stage-1 prompt asking "did our
system correctly bind this?" is asking the tenant to confirm a
fact they themselves authored.

### Implementation

`rag/intake/posture_writer._write_document_findings`: when
`inference_source='templated'`, write with:
```sql
review_status = 'approved'
confirmed_by  = <uploading user's UUID>  -- from key_info.user_id
confirmed_at  = now()
```

User ID plumbed: `api_server._run_pipeline` (both upload + admin/reextract
call sites) → `doc_pipeline.run` → `posture_writer.write_findings` →
`_write_document_findings`. New `user_id` / `uploaded_by` params at
each layer.

### Visibility — `/api/v1/stage1/auto-approved`

New endpoint surfaces recently auto-approved templated findings:
```
GET /api/v1/stage1/auto-approved?days=N&limit=M
```
Returns: `{tenant_id, days, count, findings: [{id, checklist_item_id,
control_ref, status, confidence, excerpt_preview, authored_by,
confirmed_at, source_filename}]}`.

Tenant can audit + revert without it blocking posture. The "auto-approved
but visible" pattern is option D from the discussion (vs B "always
approved silently", vs C "always pending"; preserved visibility
without latency).

## Decision 2 — edit-zone markers fix circular counting

### The bug shape

For a v2 hand-refined template like A.5.15 access_control_policy,
the rendered output of one MUST section looks like:

```
<<MUST item:A.5.15:rbac>>
_Default model — RBAC unless explicitly excepted._

State RBAC as the default + the explicit exceptions...

**✓ Good**: "RBAC is the default access model..."

**From Access Control Policy.docx (leaf_scan, 2026-06-14):**

Access to information systems must be granted...

<!-- prefilled from N sources -->
```

The fast-path's old logic stripped `_Why:` lines + `<<TEXT>>`
placeholders, then treated whatever remained as evidence.
Everything else (`State RBAC as...`, `✓ Good: ...`, prefill blocks)
was counted as tenant authorship — even when the tenant uploaded
the file unchanged.

### The fix — explicit edit-zone markers

Render endpoint wraps every placeholder/prefill substitution with:
```
<!-- EDIT-ZONE-START item:X -->
{<<TEXT>> placeholder OR composed prefill block}
<!-- EDIT-ZONE-END item:X -->
```

Wrapping ALWAYS happens (even when `?empty=true`) — markers are the
contract between render and extract, not just a prefill artifact.

Extractor runs in two modes:

- **Mode A — edit-zone-driven** (when zones present in upload):
  parse zone interior per MUST. Per-zone authorship check:
  - empty / whitespace → skip
  - just `<<TEXT>>` / `<<NAME>>` placeholder → skip
  - prefill block ending with `<!-- prefilled from N -->` + nothing
    substantive after → skip (pure scaffolding)
  - otherwise → bind

- **Mode B — legacy full-section scan** (when no zones found):
  preserved for uploads of templates rendered before this fix.
  Less precise but won't break older roundtrips.

### Smoke verification on Arion

| Upload | Findings | Notes |
|---|---|---|
| Unchanged template re-uploaded (12 zones) | **0** | All zones detected as pure scaffolding |
| Same template with 1 zone edited (`rbac` filled with new content) | **1 templated finding** (rbac) + 2 xfw_bridge proposals | Exact target — no spillover |

Pipeline times: 2.1s (unchanged), 1.8s (edited) — no LLM calls.

## Data cleanup — 10 circular-counted rows reverted

Today's earlier smoke tests (commits before the edit-zone fix) had
written 18 circular templated rows across `loop_acp_filled.md` and
`auto_approve_smoke.md`. Of those, 4 were real tenant authorship
(logical_rules + need_to_know from loop_acp; authorisation +
segregation_link from auto_approve_smoke). 10 were prefill-only
scaffolding artefacts.

Soft-deleted the 10 with `rejection_reason='circular-counting-revert:
templated fast-path bound prefill-only sections before edit-zone
fix (2026-06-25)'`. Kept the 4 real edits.

Post-revert A.5.15 state is honest:
- 6/6 effective MUSTs satisfied (1 N/A: physical_rules)
- Each via real authorship across the cumulative smoke testing
- Wizard anchors: 2/20 (A.5.15 legitimately complete)

## Pattern — round-trip integrity

When a system render/edit/upload loops the same artefact, the
upload-side must distinguish:
- **Scaffolding** (guidance prose, headings, prefilled prior
  evidence, format markers): NOT new authorship
- **Tenant edit zone content**: IS new authorship

The cleanest contract is **explicit zone markers in the render
output**, not heuristic detection at upload time. The render
endpoint owns "where can the tenant edit"; the extractor honours
those boundaries.

This is the same shape as the workbook intake's
`<<MUST item:X>>` markers (per `[[curation-document-templates-idea]]`):
explicit structural contract between producer and consumer.

## Eval

198/199 after both shipments (only #16 LLM-stochastic). No
posture regression.

## What's NOT done

- **Legacy circular rows on other tenants**: this cleanup was
  Arion-specific. Other tenants who round-tripped a templated
  upload pre-fix would have the same artefacts. Future cleanup
  script should sweep all templated rows landed before the
  `20f6811` commit timestamp + check zone-marker absence.
- **Form lane**: `form` source is conceptually similar to
  `templated` (direct tenant authorship). Could also auto-approve;
  deferred until form usage is observed.
- **Edit-zone validation on upload**: extractor doesn't currently
  check that the upload's zone markers MATCH the rendered template
  for that tenant. A malicious tenant could craft markers manually.
  Risk is low (deterministic bind to MUSTs that exist; tenant
  authoring intent is implicit). Not worth shipping a hash-validate
  step yet.

## Related

- [[templates-v1-foundation-2026-06-24]] — the storage architecture
  the loop builds on
- [[tenant-journey-wizard-2026-06-24]] — surfaces the round-trip
  output (per-MUST completion %)
- [[doc-curation-engine-v1]] — Direction C extractor (per-MUST
  binding) — templated is the deterministic counterpart
