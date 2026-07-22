---
name: ship-14-prime-e-risk-chat-2026-07-22
description: "Ship 14'.e — Risk chat surfaces: posture_risk question_type + short-circuit + CaseFile.risks + RISKS digest slot + preservation-check + nav badge"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 14'.e (2026-07-22) — fifth sub-arc of Ship 14. Wires the
risk register into the chat pipeline per the Ship 14'.a
addendum case-file architecture constraint. Delivers the
compact chat surface + preservation-check discipline + nav
badge. **Cascade events + notification producers deferred to
Ship 14'.f** (mid-arc rescope — retro becomes 14'.g).

## What ships

### 1. New `posture_risk` question_type

- Added to `QuestionType` enum in `rag/classifier.py`
- Added to `qtype_map` in `_check_explicit` (Signal C /
  CLEAR_INTENT_PHRASES intake fallback path)
- Wired into `_signals_lock_question_type` mechanism —
  automatic since Signal C's `question_type` field is
  hard-locked in the aggregator

### 2. Signal C CLEAR_INTENT_PHRASES at weight 1.00

Ten regex patterns added covering:
- "top risks" / "highest risks" / "our risks"
- "overdue risks" / "risks needing review"
- "residual risks" / "risks above threshold"
- "risk register" (chat query, distinct from intake DocType)
- "show me risks" / "list risks"

All map to `posture_risk` with empty `seed_refs` (risk
register is tenant-wide; refs come from linked_controls per
row, not from CLEAR_INTENT).

### 3. Deterministic short-circuit in `arion_graph.py`

`_is_risk_query()` + `_answer_risk_query()` mirror the
existing `_is_cascade_followups_query()` / `_answer_cascade_followups()`
pattern:

- Called in `retrieve_node` BEFORE any LLM classifier runs
- Uses `fetch_risks_for_casefile()` + `fetch_risk_summary()`
  from `rag/risk/queries.py`
- Query-mode inference: overdue vs residual vs top (default)
  based on query phrasing
- Renders top-N (up to 5) as compact prose with:
  * external_ref + risk_score/25 + residual/25
  * threat text (100c cap)
  * treatment_option + status
  * linked controls side-by-side (program → extension →
    obligation → guidance rank order; role model discipline)
- Grounded citation footer: `ISO 27005:2022 §8.6.1
  (treatment plan) + §7 (assessment)`
- Returns `question_type="posture_risk"` in the envelope
- Passed through `polish_short_circuit_answer()` (Ship 1.14)
  which preserves refs + bullets via drop-guards

### 4. CaseFile.risks field + RISKS digest section

Case-file discipline (Ship 2'):

- New `risks: list = field(default_factory=list)` on CaseFile
  — ground truth for the digest
- Populated in `_casefile_flow` when `cf.question_type ==
  "posture_risk"` — ONLY fires on risk queries, no per-turn
  DB hit on other queries
- New `_render_risks()` in `rag/casefile/digest.py`:
  * Fixed-slot, empty-omitting per Ship 2' discipline
  * ≤300-token budget for 8 rows (per addendum)
  * Header adapts: `RISKS (showing N of M open):` or `RISKS:`
  * Two lines per risk: `[option, status] threat` and
    `score X/25  residual Y/25  linked: refs`
  * Linked controls sorted by role rank (framework role
    model discipline)
- Included in `build_prompt_digest` output ordering — sits
  between DOCUMENTS and SESSION sections

### 5. Preservation-check on risk external_refs

- New `required_risk_refs: list[str]` on PreservationSpec
- `extract_preservation_spec()` populates it from
  `cf.risks[*].external_ref`
- `check_and_repair()` scans answer_text for each ref
  (case-insensitive substring match)
- Missing refs land in a new APPEND-ONLY footer:
  `↳ Risk register: R-042, R-017, …`
- Emits `RepairEvent(kind="missing_risk_ref")` per miss
- Never rewrites LLM prose per Ship 2' + Ship 1.14 discipline

### 6. `fetch_risks_for_casefile()` helper

- New in `rag/risk/queries.py` + exported from `rag/risk/__init__.py`
- Opens its own psycopg2 conn (case-file path is DB-agnostic)
- Enforces RLS via `SET LOCAL app.tenant_id`
- Returns compact dict-based view (id / external_ref /
  threat / vulnerability / risk_score / treatment_option /
  treatment_status / residual_risk_level / review_date /
  linked_controls)
- Silent-fail on error (returns []) — case-file path must
  never block on risk fetch
- Fetches top-N by risk_score DESC across ALL active rows
  (not filtered by status — see design note in code)

### 7. Nav badge in `static/arioncomply.html`

- New `refreshRiskBadge()` fetches
  `/api/v1/tenant/risks/summary`
- Badge shows `(overdue + above_threshold)` count
- Red background when any `above_threshold > 0`, orange
  otherwise
- Called on `connect()` alongside `refreshInboxBadge()`

## Verification

- API restarts cleanly (all 8 module edits syntax-checked)
- Live chat test: `"what are our top risks?"` returns
  `question_type=posture_risk` + 5-risk prose with mixed
  program (5.15) + extension (A.7.2.8) refs side-by-side in
  the linked-controls chip — framework role model discipline
  visible end-to-end
- Grounded citation surfaces: "grounded in ISO 27005:2022
  §8.6.1 (treatment plan) + §7 (assessment)"

## Ship 14'.a addendum — reviewer discipline answers

**1. Role split?**

Yes — linked-controls in both the short-circuit prose AND
the digest RISKS section render side-by-side, sorted by role
rank (program → extension → obligation → guidance). Live
smoke test showed `[linked: 5.15, A.7.2.8]` for a risk that
carries both ISO 27001 program + ISO 27701 extension refs
in `control_refs`. No primary/xfw split anywhere.

**2. Parallel CaseFile view?**

No — `risks` is a new field on the SAME CaseFile dataclass.
`_render_risks()` reads from `cf.risks`, populated once at
CaseFile construction. No parallel data view; ground truth
stays single.

**3. Deterministic routing?**

Yes — `_is_risk_query()` regex match in the retrieve_node
short-circuit before any LLM classifier runs. Signal C
provides the fallback path with `question_type` locked at
weight 1.00 (matches Ship 1 curator-lexicon discipline).
The LLM never invents `posture_risk` intent.

**4. Guidance-normative discipline?**

Yes — the RISKS digest section renders DATA (rows tenants
have filled in). No new MUSTs from guidance content. The
grounded citation in the answer footer is prose attribution,
not a compliance obligation.

## What did NOT ship

**Deferred to Ship 14'.f (cascade events sub-arc):**

- 4 new cascade event types (`risk_added`,
  `risk_treatment_overdue`, `residual_above_threshold`,
  `risk_review_due`)
- Notification producers wired to writes on the risks table
- Corresponding schema migration (probably schema_v88)

Rationale: sub-arc scope was already substantial with the
chat + preservation + digest work. Cascade taxonomy addition
+ producers deserves its own focused sub-arc.

**Deferred to Ship 14'.g (eval + retro):**

- 2-3 eval cases locking posture_risk routing
- Arc retrospective

## Impact on baseline

Eval confirmed: **228/229 PASS + 1 WARN + 0 FAIL** — baseline
unchanged. Only WARN is the pre-existing #200 gap_analysis vs
posture_check mismatch. Zero regressions from:
- New POSTURE_RISK enum value + Signal C entries
- CaseFile.risks field + conditional populate in `_casefile_flow`
- _render_risks() digest section (empty-omitting; only fires
  when cf.risks is populated)
- Preservation-check + repair extension (required_risk_refs
  only populated on POSTURE_RISK queries)
- Short-circuit in retrieve_node (guarded by _is_risk_query
  regex match)

## Ship 14 progress (revised mid-arc)

| Sub-arc | Status |
|---|---|
| 14'.a Design + role-model + case-file addendum | ✓ |
| 14'.b schema_v87 + xlsx template + upload path | ✓ |
| 14'.c API surface (internal + external) | ✓ |
| 14'.d Dashboard cards + heatmap + drill-in | ✓ |
| **14'.e Chat surfaces + preservation + nav badge** | **✓ (this doc)** |
| 14'.f Cascade events + notification producers | next |
| 14'.g Eval + retro | pending |

## Related

- [[ship-14-prime-a-risk-register-design-2026-07-22]] —
  the design memo whose case-file addendum this sub-arc
  respects
- [[ship-2-prime-casefile-arc-2026-07-15]] — the case-file
  architecture (CaseFile ground truth + fixed-slot digest +
  preservation-check + APPEND-ONLY repair) this sub-arc
  extends
- [[ship-1-consensus-arc-2026-07-15]] — Signal C curator-
  lexicon at weight 1.00 discipline
- [[framework-role-model-arc]] — Phase 4b dashboard headers
  pattern that role-band chip in linked_controls follows
- Ship 14'.f: cascade events + producers (next)
