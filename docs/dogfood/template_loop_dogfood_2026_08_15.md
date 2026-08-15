# Template loop dogfood — internal review notes

_2026-08-15. Tenant: Arion Networks. Leaves walked: `req:A.5.16:identity_revocation_record` (NC 0/7), `req:A.5.15:access_control_policy` (Comply 3/3). Observational — no mutations to tenant state._

Walking the templates arc end-to-end after the Task #577 close-out. Trace each stage of what a tenant would do when a control card shows NC/OFI, note where the loop delivers value and where it snags.

---

## Loop stages

### Stage 1 — Tenant clicks the A.5.16 leaf on Topics

**Backend fires**: `GET /api/v1/advisory/leaf/req:A.5.16:identity_revocation_record/detail`

Returns:
- Posture: **NC** (0/7 covered)
- Leaf title: *"Per-Identity Revocation Record"*
- 4 prerequisites (each with `ref`, `title`, `rationale`, `good_enough`)
- 7 MUSTs (each with `id`, `text`, `satisfied`, `guidance` array)
- 32 writing-tip bullets across all MUSTs

Data is all there. Zero misses.

### Stage 2 — SPA renders the leaf-detail panel

**Sections shown** (post Task #577):
- *Before you start* — 4 prereqs, each with why + good_enough
- *What's covered / what's missing* — 7 unmet MUSTs, each collapsible `▸ Show writing tips (N)`
- *Actions* — Download MD/DOCX/XLSX + Ask AI

**"How to close this gap" retired** — the guidance now lives on the MUST rows themselves.

### Stage 3 — Tenant downloads Markdown template

**Backend fires**: `GET /api/v1/templates/req:A.5.16:identity_revocation_record/download?format=md`

Content-Disposition: `attachment; filename="A_5_16_identity_revocation_record.md"`

- 14,260 chars / 244 lines
- 7 `◆ Required element` per-MUST callouts
- 9 `Best practice` blocks with state markers (`✓` / `◐` / `— still needed:`)
- 1 `EDIT-ZONE-START` — because this leaf is a **register-shape template** (columns per MUST, one row per revocation)

The MUST-level state marker is `— still needed:` on all 7 (correct — nothing evidenced).

### Stage 4 — Template's data-entry shape

For record-shape leaves:
```
<!-- TABLE-COLUMNS leaf:req:A.5.16:identity_revocation_record -->
<!-- column: item:A.5.16:rev_identity_ref -->
<!-- column: item:A.5.16:rev_trigger_type -->
<!-- column: item:A.5.16:rev_effective_date -->
<!-- column: item:A.5.16:rev_actual_timestamp -->
<!-- column: item:A.5.16:rev_sla_met -->
<!-- column: item:A.5.16:rev_dual_signoff -->
<!-- column: item:A.5.16:rev_residual_cleanup -->
<!-- /TABLE-COLUMNS -->

<!-- EDIT-ZONE-START leaf:req:A.5.16:identity_revocation_record -->
| Rev Identity Ref | Rev Trigger Type | Rev Effective Date | … |
|---|---|---|---|
|         |         |         |         |
|         |         |         |         |
|         |         |         |         |
<!-- EDIT-ZONE-END leaf:… -->
```

Tenant fills the register. Distinct shape from policy templates (per-MUST prose sections).

### Stage 5 — Extraction path on re-upload

`POST /api/v1/documents/upload` with the filled `.md`:

1. **Dedup gate** — SHA-256 checked against prior uploads; duplicate bytes → 409 immediately.
2. **Reader** parses the doc, finds `<<MUST item:A.5.16:X>>` + TABLE-COLUMNS markers, binds each column value to the checklist_item_id.
3. **Writer** inserts `document_findings` rows per MUST, status=`present`, `inference_source='templated'`.
4. **Templated → auto-approved** at write time (no Stage-1 HITL review — tenant is the source of truth for their own template fill).
5. **P0 trigger** refreshes `posture_must_verdicts` for the affected MUSTs.
6. **Engine** recomputes `posture_controls.finding` — if all 7 satisfied → **flips to Comply**.

Every layer of that path exists and is wired to the SSoT built over Ship 583-71'.

---

## Cross-check with A.5.15 (Comply state)

Same loop on a leaf with partial evidence. Template render for `req:A.5.15:access_control_policy`:

Block 1 (`item:A.5.15:logical_rules`, MUST-level ✓):
```
**Best practice ✓ — covered:**
- ☑ Document all systems, applications, and network segments…
- ☑ State the specific rules for granting, changing, and revoking access…
- ☐ Assign responsibility for approving access requests to a named individual…
- ☐ Cross-reference the policy with supporting procedures or workflows…
- ☐ Record the latest approval of the access control policy with the approver's name, signature, and approval date.
```

This is exactly the auditor-actionable signal the arc was aiming at:
- MUST level: ✓ (something evidenced).
- Bullet level: 2 of 5 auditor cues addressed; the other 3 (**named individual approving**, **cross-reference to procedures**, **signed approval date**) still need work.

Tenant knows exactly where to focus. Rationale + `good_enough` on prereqs; per-bullet keyword-overlap on best-practice items; MUST-level tick from SSoT.

---

## Wins

1. **Every stage has real data**. The advisory returns rich structured content; template download reflects it; extraction closes the loop. Nothing is stubbed.
2. **Per-bullet marks work for the "Comply" case** (Arion A.5.15). Distinguishes what's already there from what still needs work — actionable per-cue.
3. **Prerequisites carry acceptance criterion** (`good_enough`). Tenant knows how to know they're done with each prereq.
4. **Template auto-approve on `templated` source** removes a big HITL bottleneck. Tenant's own template fill is trusted.
5. **Register shape (TABLE-COLUMNS)** is a genuinely different UX for record-type leaves — the extractor binds per-column, one row per record. Right shape for what auditors expect (per-instance evidence).

## Friction observed

### 1. Per-bullet ☐ on 0/7 NC leaves adds visual clutter
On A.5.16 (0/7 NC), every guidance bullet renders `☐`. That's honest but redundant — the MUST-level "— still needed:" already tells the tenant nothing's covered yet. The 32 `☐` glyphs across the leaf make the doc feel heavier without adding new signal.

**Suggested fix**: when the MUST-level state is `— still needed:` (finding=NC AND no evidence at all), suppress per-bullet marks entirely; render flat bullets. Keep marks only when there's *some* evidence, where the ☑/☐ distinction is genuinely informative.

### 2. Register-shape templates lack per-MUST evidence prefill
Policy templates (A.5.15) prefill each MUST's edit zone with prior approved evidence — the tenant sees what's already known and refines. Register templates (A.5.16) have one big empty table — even if Arion has *some* prior revocation records anywhere in the corpus, they don't flow into the table's initial rows.

**Suggested fix**: for register-shape templates, prefill a first row with an example synthesized from the tenant's most-recent identity-lifecycle evidence, marked clearly as *"— example from your prior evidence, replace with real data"*. Non-load-bearing (tenant will delete/replace), but shows the tenant *what a well-filled row looks like*.

### 3. Advisory endpoint path is `/advisory/leaf/…/detail` not `/topics/leaf/…/advisory`
Task #577's original description referenced `/api/v1/topics/leaf/{leaf_id}/advisory` — the actual live endpoint is `/api/v1/advisory/leaf/{leaf_id}/detail`. Task text was stale from before an endpoint rename. Fine, just a note.

### 4. Records fanout under a single control_ref
A.5.16 has ~30 MUSTs across ~4 leaves (identity register, revocation record, procedure, etc.). Arion's evidence covers 8 MUSTs (all on the identity_register leaf). The revocation_record leaf is 0/7. The SPA UX lets the tenant drill in per leaf, which is right — but a tenant looking at the A.5.16 control-level card might see "8 of 30 covered ≈ 27%" and think they're one-third done, when actually one whole leaf is completely untouched.

**Not a Task #577 issue** — this is a downstream question for the topic dashboard: is the per-control aggregation of "8 of 30 MUSTs" meaningful, or does the tenant think about A.5.16 leaf-by-leaf? Something to revisit if we ever surface per-control coverage percentages at a higher level.

### 5. Extraction latency isn't visible in the loop UX
Stage 5 runs in the background. `POST /documents/upload` returns immediately with an `upload_id`. Tenant has to poll `GET /documents/{id}/status` to know when the posture flipped. Nothing in the SPA today automates that — after upload, the tenant is left refreshing the topic view manually.

**Suggested fix**: after upload, the SPA polls status for ~60s and shows a "extraction running…" state; on completion refreshes the leaf-detail card. Non-blocking (tenant can navigate away), just visible.

### 6. docx renderer isn't in the per-bullet parity yet
Ship 586 tick indicator and Task #577's per-bullet ☑/☐ both landed in the Markdown renderer only. `_render_guidance_block` in `docx_renderer.py` still uses the flat Ship 56'.a shape. Any tenant downloading the DOCX gets the older experience.

**Suggested fix**: parallel port to `docx_renderer.py::_render_guidance_block` when we next touch that file. Retro flagged this as follow-on.

---

## Overall verdict

**The template loop delivers.** Every stage from advisory → download → fill → upload → posture flip is real, wired to the SSoT, and produces auditor-testable output. Task #577 was the last visibility gap — tenant now sees the same 5-bullet auditor cues the curator authored, with per-bullet marks that tell them where evidence lands vs where it doesn't.

The frictions above are follow-on tuning, not gaps in the loop itself. Priority order (by tenant impact):

1. **#1 — per-bullet ☐ suppression on pure-NC leaves.** Reduces clutter without losing signal. Small renderer edit.
2. **#5 — extraction latency UX.** Nobody wants to refresh manually. Small SPA edit + poll pattern.
3. **#6 — docx parity.** Tenants who download DOCX shouldn't get an older experience. Curator arc.
4. **#2 — register template row prefill.** Bigger arc — needs a "pick an example" heuristic per record-shape MUST.
5. **#4 — control-level coverage aggregation** — separate arc when we surface per-control percentages elsewhere.

None block the templates arc closer. All would strengthen the tenant-facing experience further.
