# ArionComply — Claude Code Guide

## Project
Compliance RAG platform on Azure VM (172.211.244.144).
Stack: FastAPI + LangGraph + Neo4j + ChromaDB + PostgreSQL + GPT-4o.

## Product direction (2026-06-27)

**ArionComply is a compliance program ledger, NOT a generic
evidence repository.** Our role: track WHERE evidence lives +
freshness + ownership + auditor-readable provenance. The tenant
keeps evidence sovereignty in the systems that already hold their
data (Odoo HR, Okta IAM, ServiceNow CMDB, etc.).

Two coexisting evidence modes per (tenant, leaf):

- **Stored mode** — small/startup tenants without external systems
  of record. Evidence authored + held in-product via templates /
  forms / `tabular_evidence_rows`. The templating arc serves this.
- **Cited mode** — larger tenants where evidence lives in source
  systems. ArionComply tracks the cite metadata + verification
  cadence + auditor gates (periodic samples, verification
  attestations with `changes_detected`, process documentation).

Both modes contribute to the same leaf at per-MUST granularity;
engine takes the union.

See [[product-principle-evidence-stored-vs-cited]] for the full
principle + [[product-concept-evidence-cascade-2026-06-27]] for
the strategic evidence-cascade layer (event-driven implications:
"new employee" → training/access/NDA artefacts needed).

For cite-mode specifically: **the system exposes + tracks; the
tenant attests.** No silent machine attestations, no URL parsers
that auto-write `external_evidence_verification_log`. Every
`verified_by` is a real user at the moment of a tenant decision.
See [[product-principle-cite-expose-and-track]] for the full rule
set + what it rules out + what it allows (candidate generation).

## Before touching module X, read arc Y

Before starting work in these areas, load the referenced arc doc
into context. This is a codified discipline against re-inventing
patterns that a later arc has superseded. Grep `docs/memory/` for
the exact filename.

| Touching this... | Read this first |
|---|---|
| Multi-framework classification / posture propagation / cross-framework "bridges" | [[framework-role-model-arc]] — programs / extensions / obligations. Do NOT split by "primary/xfw"; the layer split is deprecated. |
| `rag/casefile/`, `rag/llm_answer.py::_casefile_flow`, prompt digest, preservation check | [[ship-2-prime-casefile-arc-2026-07-15]], [[ship-2-prime-i-id-discipline-and-digest-fix-2026-07-16]] |
| Chat intent classification / routing | [[ship-1-consensus-arc-2026-07-15]] — 7-signal consensus + bounded gatekeeper. Curator-lexicon is top-tier weight (1.00) — add DOCUMENT_TOPIC_MAP entries rather than prompt-tuning. |
| Any field named `X_id` / `X_ref` / `X_slug` — plus any Postgres `%s::uuid` cast | [[ship-2-prime-i-id-discipline-and-digest-fix-2026-07-16]] — naming rule; use `rag/id_types.TenantUUID / NodeId / ControlRef / LeafId` (validate at construction). |
| Curation / DerivedSpec / multi-leaf specs | [[curation-phase-b-retrospective]] |
| Cascade events + implications | [[cascade-arc-retrospective-2026-06-30]] |
| De-jargonize / tenant-facing prose | [[dejargonize-ux-pass-2026-07-01]] |

## Legacy — do not extend (retire-by tracking)

These patterns are superseded and being retired. Do NOT add new
call sites; migrate existing sites opportunistically when touched.
When a retire-by date passes, delete the legacy path.

- **primary_nodes / xfw_nodes layer split** — RETIRED 2026-07-16 in
  Ship 2'.n. `rank_and_answer` legacy body (~912 LOC), inline
  `_infer_primary_std`, and `_pick_primary_std` all deleted. The
  case-file flow (structured by role per framework-role-model-arc)
  is the only path. Do NOT re-introduce a layer split.
- **`state["tenant_id"]` as display name** — fixed Ship 2'.i via
  `arion_state.py:89`. Any read site expecting a display name is
  now broken; migrate to `state["tenant_display_name"]`.
- **`_is_uuid_shape()` band-aid** — replaced by
  `rag/id_types.is_uuid`. Do not add new call sites.
- **`node_id.split(":")`** — RETIRED 2026-07-16 in Ship 2'.m
  (commit 6b47f66). All 21 live sites migrated to
  `rag.id_types.ref_of()` / `standard_of()` helpers. For NEW code
  use `NodeId(value)` directly to get strict validation +
  `.standard_id`, `.version`, `.ref` accessors. Do not re-introduce
  inline splits.
- **AnswerPayload dispatcher (Ship 2.0 / Ship 2.1)** — reverted
  2026-07-15 (commit f246df3). Do NOT re-add per-taxonomy
  dispatch tables; use soft-branching in
  `rag/casefile/digest.py::_plan_for` if intent-aware section
  budgets are needed.
- **`CASEFILE_ENABLED` env flag** — RETIRED 2026-07-16 in Ship 2'.n.
  The case-file flow is the only path; no flag gate remains. Do NOT
  re-introduce feature flags without an explicit retire-by date.
- **`USE_LEGACY_CLASSIFIER` kill-switch** — RETIRED 2026-07-17 in
  Ship 2'.o. `consensus_layer_enabled()` deleted; consensus always
  runs. The intra-consensus fallback to the LLM classifier on
  `insufficient` verdict is design-intended, NOT an escape hatch —
  it stays. Do NOT re-introduce runtime toggles for the consensus
  layer.

### Build sequence

| Layer | Status |
|---|---|
| Templating arc (storage mode) — 20 v2 anchors + native formats (md/xlsx/docx) + xlsx round-trip + tenant profile + evidence-class UI | SHIPPED |
| Stage-1 queue hygiene + A.6.7 promotion (catalog now 100% multi-leaf) | SHIPPED |
| Cite-mode v1 — schema_v50 + tenant_external_system + external_evidence_source + verification_log + engine union + APIs + UI + freshness card | SHIPPED |
| Relationship catalog — 505 typed edges across 11 edge types (S4 286 xfw + S5 54 GDPR + S6 160 ISO + S2b 5 BLOCKS_WHEN); load_graph_relationships.py cross-framework deprecated | SHIPPED |
| Cascade vocabulary — 53 events (11 existing + 42 operational) + 6 meta-cascade edge types | SHIPPED |
| Cascade engine v1 — all 10 meditation patterns (P1..P10) + 23 API endpoints + 7 UI surfaces (KPIs/drill-in/timeline/overrides/bulk/notifications/event detail) | SHIPPED |
| xfw_proposer uses catalog rationale on bridge proposals (S7) | SHIPPED |
| De-jargonize UX pass across every tenant-facing surface (Evidence Package + dashboard + chat + templates + intake + notifications + profile + cascade + docs + queue + heatmap + streaming + inbox + admin + onboarding + session + errors) | SHIPPED |
| Tier-4 starter kit — structured templates_block in chat + Get Started sidebar mode (fresh-tenant foundation sequence with phase strip / next-action card / 20-anchor list / cite nudge) | SHIPPED |
| ISO 27701 Phase 0+1 — tenant enrolment + code-path pre-wiring verified | SHIPPED |
| ISO 27701 Phase 2 Batch 1 — §A.7.2 controller + §B.8.2 processor (14 anchors × 4 leaves = 56 EvidenceRequirements + 34 GDPR/27001 bridge edges + iso27701_2019 Chroma collection + Arion posture seed) | SHIPPED |
| ISO 27701 Phase 2 Batch 2 — §A.7.3 subject rights + §A.7.4 PbD + §B.8.3-4 mirrors (23 anchors × 4 = 92 leaves + 48 bridges + posture seed) | SHIPPED |
| ISO 27701 Phase 2 Batch 3 — §A.7.5 + §B.8.5 transfers (12 anchors × 4 = 48 leaves + 30 bridges + posture seed) — PHASE 2 CURATION COMPLETE 49 controls / 196 leaves / 112 bridges | SHIPPED |
| ISO 27701 Phase 3 — queryable-standards gate flip + LLM scope block (prompt + citation format + Arion primary-framework rewrite) + 3 classifier short-circuits + 6 anchor interleave (_ANCHOR_LEAVES 20→26) + 3 eval cases (#201-203) | SHIPPED |
| ISO 27701 Phase 4 — 196 template scaffolds + 98 doc_mappings + 49 workbook_mappings (147 mappings covering 75% of leaves; remainder falls through to LLM extractor). ISO 27701 ARC FULLY COMPLETE across Phases 0-4 | SHIPPED |
| Outbound notification delivery (email/Slack) — SMTP + Slack webhook workers in `rag/notifications/deliver.py`; wired to `notification_delivery` sweep work_type. Producers exist for cascade events (`rag/cascade/notify.py`); other producers land per feature. | SHIPPED code, wire per producer |
| UPDATES_FACT recompute — `rag/facts/recompute.py`; wired to `fact_recompute` sweep work_type reading `fact_source_config`. | SHIPPED |
| Periodic sweep scheduler — `rag/scheduler/tick.py` (Wave 3b, 2026-07-13). Ship 3'.a (2026-07-17) productionizes via `ops/systemd/arioncomply-sweep.timer` (30-min cadence). See "Periodic sweep scheduler" section below. | SHIPPED |
| Notification producers COMPLETE — cascade events (built-in) + `freshness_expiry` (Ship 3'.b) + `nc_surfaced` / `upload_processed` (Ship 3'.c) + `stage2_proposal_ready` / `upload_failed` (Ship 3'.e) + `overdue_followups` sweep backstop (Ship 3'.f) + `cite_verification_overdue` (Ship 3'.g) + `posture_flip_to_comply` (write-path, severity `low`) + `api_key_expiring` (sweep, 30d/7d/1d escalating buckets, Ship 3'.i). 13 kinds in `tenant_notification_kind_check`. | SHIPPED |
| Inbox per-kind rendering (Ships 3'.h + 3'.i) — humanized labels for all 13 kinds + Tabler icons + one-click "Open X" deep-link buttons (`_notifOpen()` mark-read + `setMode()` jumps tenant to the target surface: dashboard drill-in / queue / docs / cascade timeline / profile for api keys). HTML/JS-only; no server code touched. | SHIPPED |
| Delivery worker integration tests (Ship 3'.j) — tests/test_notification_delivery.py exercises deliver_all end-to-end via monkey-patched SMTP + Slack + throwaway test tenant. 7 tests: happy paths / severity gate / dedup / retry / dry-run / give-up boundary. schema_v75 grants DELETE on tenant_notification + notification_delivery_attempt (fixture cleanup + future retention sweep). | SHIPPED |
| Notification retention sweep (Ship 3'.k) — `sweep_notification_retention` with 3 delete rules (dismissed 30d / read 90d / max_age 365d) + attempt aging 90d. schema_v77 adds `notification_retention` work_type. 7 integration tests. Closes the unbounded-inbox gap; notification arc truly complete. | SHIPPED |
| External API foundation (Ship 4'.a) — `/api/external/v1/*` namespace with scoped keys (fine-grained `external:*`) + fixed-window rate limit (60/min, X-RateLimit-* headers + Retry-After on 429) + structured error contract. schema_v78 + `rag/external/` module. First endpoint: GET /status. 7 integration tests. Opens Ship 4 external-RAG-API arc. | SHIPPED |
| External /query endpoint (Ship 4'.b) — POST /api/external/v1/query returns structured RAG answer JSON (answer + question_type + typed citations + session_id + request_id + latency_ms + needs_clarification). Reuses arion_graph pipeline; scope external:query. 13 external API tests total. Citation.posture is best-effort in this arc. | SHIPPED |
| Audit-log classification correction (Ship 4'.b addendum, schema_v79) — reclassified 5 tables from "append-only audit" to "diagnostic": ai_call_log, chat_casefile_log, chat_consensus_log, fact_recompute_log, intake_trace_log now have DELETE grants (retention-eligible) + ai_call_log UPDATE revoked. Only posture_status_log stays compliance-load-bearing (INSERT/SELECT only + tenant FK hardened from CASCADE to NO ACTION). Unblocks future diagnostic-log retention sweep + GDPR erasure design. | SHIPPED |
| External /posture family (Ship 4'.c) — 3 read endpoints under scope external:posture:read: GET /frameworks (enrolled + counts), GET /posture (flat list, filters standard_id / finding[] / changed_since, pagination, summary-across-filtered-set), GET /posture/{ref} (drill-in with REQUIRED standard_id, structured 404 on miss). 22/22 external API tests. | SHIPPED |
| External /notifications feed (Ship 4'.d) — 2 read endpoints under scope external:notifications:read: GET /notifications (list + since/kind[]/severity[]/unread_only filters + pagination + summary total/unread/urgent) and GET /notifications/{id} (single by UUID, 404 structured on miss, 400 on malformed UUID). 33/33 external API tests. | SHIPPED |
| External /documents + /evidence (Ship 4'.e) — write side + evidence read. POST /documents (multipart upload → intake pipeline background task, scope external:evidence:write, dedup returns canonical_upload_id) + GET /documents/{id} (status polling) + GET /evidence?control_ref=X&standard_id=Y (returns document_findings, JOINs both document_uploads + client_documents so filenames resolve either way). 42/42 external API tests. | SHIPPED |
| External /cascade + /bridges (Ship 4'.f) — GET /cascade/timeline (implications + followups feed, kind[]/control_ref/since_days filters, summary with overdue count) + GET /cascade/implications/{id} + GET /bridges (Neo4j RequirementNode graph, outbound + inbound IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE edges). Scopes external:cascade:read + external:xfw:read. 53/53 external API tests. | SHIPPED |
| External docs + Python SDK + key management (Ship 4'.g) — (1) filtered OpenAPI at /api/external/v1/{docs,redoc,openapi.json} — Swagger + ReDoc + JSON, external endpoints only. (2) `sdk/python/arioncomply/` — httpx+Pydantic Client covering all 14 endpoints with typed response models + exception hierarchy + PyPI-ready pyproject.toml + README. (3) POST/GET/DELETE /api/v1/tenant/api-keys + Profile UI with scope-picker checkbox tree + copy-once reveal panel. 59/59 external API tests. | SHIPPED |
| Ship 4' arc closed (Ship 4'.h) — retrospective at [[ship-4-prime-arc-retrospective-2026-07-18]]. 7 delivery sub-arcs + closer over ~24h; 14 endpoints, 8 `external:*` scopes, 59 integration tests, schemas v78+v79, Python SDK, filtered OpenAPI. Deferred: write-side notifications/posture, webhook subscriptions, key rotation, SDK async+codegen+PyPI publish. | SHIPPED |
| LLM audit + embedding consolidation (Ship 5'.a + 5'.b) — audit inventoried 10 LLM call sites + 5 Chroma collections, 9 findings prioritized. Consolidation moved all 4 Chroma collections onto text-embedding-3-large (was: 3 on -large, 1 on -small). New rag/embedding_config.py (single source of truth) + scripts/reindex_all.py (one-shot rebuild). Naming-aware embed fn everywhere → defensive rebuild covers all collections. Ship 5'.c-f follows for temperature fix, dead code cleanup, retrospective. | SHIPPED |
| Temperature + tier2 migration (Ship 5'.c) — closes Ship 5'.a HIGH findings. Extractor pass1+pass2 + enricher use explicit `temperature=0.0` for structured JSON extraction (was inheriting 0.4 default). tier2_generator migrated off direct OpenAI SDK to `rag.llm_client.call` with new `enrichment_tier2` purpose label; deleted dead `_get_client()`. | SHIPPED |
| Dead code + llm_models module (Ship 5'.d) — deleted 3 dead pathways (classifier._get_openai, llm_answer._get_client, llm_answer.py.old.py). New `rag/llm_models.py` with 7 env-overridable named constants (MODEL_CHAT_ANSWER, MODEL_CHAT_VERIFY, MODEL_CLASSIFIER, MODEL_CONSENSUS_GK, MODEL_EXTRACTOR, MODEL_ENRICHER, MODEL_ENRICHMENT_T2). Every hardcoded model string across the codebase migrated to the shared module. | SHIPPED |
| ai_call_log purpose allowlist fix (Ship 5'.e, schema_v80) — added `consensus_gatekeeper` + `enrichment_tier2` to CHECK constraint. Recovers 5-15% of previously-missing LLM-call telemetry (Ship 1 gatekeeper calls + tier2 enrichment) that had been silent-failing on the constraint. | SHIPPED |
| Ship 5' arc closed (Ship 5'.f) — retrospective at [[ship-5-prime-arc-retrospective-2026-07-18]]. 6 sub-arcs across ~½ day. All 9 audit findings closed. Two new config modules: `rag/embedding_config.py` (embedding constants) + `rag/llm_models.py` (LLM model constants). All 4 Chroma collections uniformly on text-embedding-3-large. `llm_client.call` is now the only LLM path (no bypasses). Every hardcoded model string in code migrated to the config module. Deferred: CI grep checks, async SDK, retry-on-429. | SHIPPED |
| LLM role audit (Ship 6'.a) — role + hallucination-risk classification of all 10 LLM sites through a compliance-stakes lens. Determinative / Navigational / Compositional / Diagnostic. Inventoried 13 cross-cutting safeguards + confirmed every compliance-load-bearing decision is deterministic (engine, posture writes, cascade, notifications). LLMs draft/route/summarize; never decide. 5 priorities for Ship 6'.b+. See [[ship-6-prime-a-llm-role-audit-2026-07-18]]. | SHIPPED |
| Grounding provenance (Ship 6'.b, schema_v81) — new `document_findings.grounding_method` column (CHECK-allowlist of 8 values: extractor_verbatim / workbook / template / fingerprint / leaf_scan / manual / form / unknown). Writer wired at both INSERT sites; backfilled 3839 rows from `inference_source`. `tests/test_extractor_grounding.py` adds 8 assertions locking the `_evidence_grounded()` substring-verification gate (verbatim match, fabricated dropped, punctuation drift, min-length, markdown source, empty-doc leniency). Corrects Ship 6'.a framing — the extractor LLM path is bounded by a strict verifier gate at BOTH call sites; Ship 6'.b delivers auditor visibility into which safeguard fired. | SHIPPED |
| Preservation-check retrospective (Ship 6'.c) — data-driven analysis of `chat_casefile_log` (1417 turns, 0 errors). 87.7% of turns fire ≥1 repair event; 94% of events are ref-adjacent (`missing_draft_near_ref` 37% / `missing_ref` 33% / `missing_verdict_near_ref` 24%); `document_inventory` + `cross_framework` at 100% repair rate. Latency cost ~3ms/turn (0.1%). Verdict: repair pass is a feature — APPEND-ONLY guarantees audit completeness without capping LLM prose. 4 follow-up experiments deferred. See [[ship-6-prime-c-preservation-retrospective-2026-07-19]]. | SHIPPED |
| Passive claim-scan observability (Ship 6'.d, schema_v82) — new `chat_casefile_log.{answer_text, claim_events, claim_events_count}` columns (8000-char answer cap, jsonb event list). New `rag/casefile/claim_scan.py` with 3 regex patterns (direct: `REF requires X`, prepositional: `under REF X`, generic: `the standard requires X`) + per-event `ref_in_digest` + `standard_in_scope` signals. APPEND-ONLY passive: never rewrites answer text, never blocks response. 41-assertion test suite. Foundation for Ship 6'.e+ observability + optional future enforcement. | SHIPPED |
| Joined LLM decision-trail (Ship 6'.e, schema_v83) — new `chat_llm_decision_trail` view JOINs chat_casefile_log ⋈ chat_consensus_log ⋈ ai_call_log on `request_id`. Fixed the wire-up first — `log_casefile()` + `log_consensus()` now fall back to `ai_trace.current_{session,request}_id()` context vars (previously 0% populated). New `/api/v1/admin/chat/decision-trail` endpoint with filters (request_id / session_id / hours / only_repaired / only_ungrounded). One row per chat turn with every LLM decision signal + cost. | SHIPPED |
| Ship 6' arc closed (Ship 6'.f) — retrospective at [[ship-6-prime-arc-retrospective-2026-07-19]]. 5 sub-arcs across ~1.5 days. 3 schemas (v81/v82/v83), 2 modules, 49 test assertions. Codified property: no LLM site is compliance-load-bearing without a deterministic gate. APPEND-ONLY (preservation-check + claim scan) is the auditor-safety idiom. ContextVars fallback pattern for id-plumbing. Deferred: chat UI drill-in, materialized decision-trail, session-scoped claim dedup, model-tier divergence investigation, CI grep for direct-OpenAI imports. | SHIPPED |
| Output-surface audit (Ship 7'.a) — opens Ship 7. Cataloged every tenant-facing output; 8 CLEAN (chat, advisory, Evidence Package, dashboard, Stage-1 chat, template blocks, SDK errors, loading states) + 8 MIXED sites where jargon leaks (Stage-2 engine_reason, cascade slugs, external API standard_id, notification action verbs, legacy gap_description prose, cascade rationale, error UUIDs, EP obligation text). Proposes framework-aware output gateway: per-framework JSON vocabulary in `rag/output/vocab/`, composable transforms with surface hints (not one monolithic humanize()), gateway_guard warn-only linter. `polish()` LLM humanization deferred to 7'.d with evaluation checkpoint — may not be needed if deterministic pass proves sufficient. See [[ship-7-prime-a-output-audit-2026-07-19]]. | SHIPPED |
| Output gateway skeleton + 2 pilots (Ship 7'.b) — framework-aware gateway built. `rag/output/vocab/` holds per-framework JSON (ISO 27001 / ISO 27701 / GDPR — adding SOC 2 / NIS2 later is one file). `rag/output/transforms.py` = 5 idempotent transforms. `rag/output/gateway.py` = `humanize(text, surface=...)` + `gateway_guard()` warn-only linter with 6 default surface chains. Pilot 1: external API `PostureControl.standard_display` field added (non-breaking additive). Pilot 2: notification producers in `rag/scheduler/tick.py` route through gateway (retires inline `.replace('_', ' ')`). 45 test assertions. Invariants proven: framework enrolment = one file, per-surface behavior without switch statements, opt-in never middleware. | SHIPPED |
| MIXED-site migration (Ship 7'.c) — remaining 4 site groups migrated. Cascade endpoint: 4 non-breaking `*_display` fields on CascadeEvent + ImplicationDetail + rationale scrubbed. Posture endpoint: gap_description + action_required + engine reason (semantic + gateway) scrubbed. api_server error UUIDs: 2 specific offenders route through `error_detail` surface. Evidence Package obligation_text + leaf.description scrubbed via new `evidence_prose` surface (registered this arc). 51 tests. Ship 7'.d becomes evaluation checkpoint for polish() need. | SHIPPED |
| Evaluation checkpoint + markdown-escape fix (Ship 7'.d) — sampled real outputs from all 4 migrated surfaces. Evidence Package + posture (human-authored) + notification bodies read naturally after deterministic gateway. Only real gap: extractor-produced gap_description had `\-`, `\(`, `\.` backslash escapes surviving. Fix: new `strip_markdown_escapes` transform added to stage2_reason / evidence_prose / cascade_rationale chains. **polish() SKIPPED** — deterministic layer sufficient. Ship 7'.e is moot; next is 7'.f arc retrospective. 57 tests. | SHIPPED |
| Ship 7' arc closed (Ship 7'.f) — retrospective at [[ship-7-prime-arc-retrospective-2026-07-19]]. 4 sub-arcs + skipped + closer, all in one day (shortest since Ship 5'). Framework-aware output gateway: `rag/output/vocab/*.json` per-framework vocabulary + 6 composable transforms + surface hints + gateway_guard. 57 test assertions. Codified properties: vocabulary-as-data (framework = 1 file), opt-in never middleware, non-breaking additive migration (`*_display` companions), idempotent composable transforms. Empirical evaluation checkpoint (7'.d) validated skipping polish() and surfaced markdown-escape leak audit missed. Deferred: chat prose gateway migration, CI grep guards, SDK typed `*_display` fields. | SHIPPED |
| ISO 27701 gap-close (Ship 8'.a + 8'.b) — `scripts/backfill_markdown_escapes.py` cleans backslash-escape artifacts in stored `posture_controls.gap_description` + `.action_required` + `document_findings.excerpt` (18 + 1110 rows on demo tenant; idempotent, applied via Python `strip_markdown_escapes` for scrub-semantic parity with the gateway). Then 12 new eval cases (#204-215) locking Phase 2 Batches 1/2/3 controller anchors + first B.8 processor coverage + A.7 ambiguity. Suite 208 → 220; iso27701 tag 3 → 15. Baseline floor: **217/220**. Verified false alarm: Arion is legitimately controller + processor per client_facts, so B.8 NC postures are correct — no seed fix needed. See [[ship-8-prime-a-markdown-backfill-2026-07-20]] + [[ship-8-prime-b-iso27701-eval-expansion-2026-07-20]]. | SHIPPED |
| Ship 8' arc closed (Ship 8'.c) — retrospective at [[ship-8-prime-arc-retrospective-2026-07-20]]. 2 sub-arcs delivered + 1 dropped as false alarm, all in one day. Lesson locked in: verify data-driven hypotheses against data BEFORE building. B.8 posture-seed "fix" would have been a wasted sub-arc; 4 queries against client_facts + gap_descriptions disproved the audit narrative. Deferred for future arcs: program_review mapping void (49 leaves), B.8.3-5 eval mirrors, bridge-fanout assertions, 27701 SoA scaffold, 27701 demo documents. | SHIPPED |
| ISO 27701 close (Ship 9'.a + 9'.b + 9'.c) — 9'.a: 6 new eval cases (#216-221) for B.8.3-5 processor mirrors. 9'.b: SoA template extended with 700-word PIMS section (49 anchors + role-based applicability + example rows). 9'.c: `generate_doc_mappings.py` extended with `_is_review_doc()`; **189 new mappings** (49 27701 program_reviews + 140 bonus ISO 27001 ISMS/Annex A review leaves). ISO 27701 coverage: **75% → 100%**, zero fall-through. Suite: 220 → 226 cases. Baseline floor: **223/226**. See [[ship-9-prime-a-b-c-iso27701-close-2026-07-20]]. | SHIPPED |
| Ship 9' arc closed (Ship 9'.e) — retrospective at [[ship-9-prime-arc-retrospective-2026-07-20]]. 3 sub-arcs delivered + 1 skipped (9'.d demo docs — deferred to real customer engagements) + closer, all in one day. ISO 27701 arc TRULY complete now. Codified: framework-aware generator scales linearly (extension for `program_review` targeted 49 delivered 189); template hardening is curator task not code; coverage percentages should track per framework; eval doesn't need per-anchor completeness. Deferred: bridge-fanout assertions, per-tenant SoA rendering (relevant when we add more frameworks), test coverage for bonus ISO 27001 review mappings. | SHIPPED |
| Extractor quality arc (Ship 11'.a → 11'.f) — 5 sub-arcs + closer across 2026-07-20→21. Layer-3 bridge source-quality gate (11'.b, `xfw_proposer.py::_bridge_worthy_check`), MUST-aware content-shape filter (11'.c, `extractor.py::_looks_like_field_or_header`, wired to critic + LLM pass-1 + fingerprint paths), post-critic embedding-cosine semantic-fit gate (11'.d/redesign, `critic_verifier.py::_semantic_fit_ok`). Real re-extraction: 5 Ship 10 docs produce 102 pending vs Ship 10's 97 — FLAT despite Ship 9 adding 189 mappings + 51 leaves in between (filters absorbed 130% coverage growth). But the same 4 Ship-10-reject bridge fanouts re-appear; post-LLM gates can't fix upstream fingerprint breadth. **Real Pattern 2 fix belongs in a curator arc: fingerprint token audit, bridge condition tightening, per-anchor evidence-shape schema.** Case-file discipline restored (11'.d prompt bloat reverted). See [[ship-11-prime-arc-retrospective-2026-07-21]]. | SHIPPED |
| ISO 27001:2013→2022 renumbering in source JSONs — closed in Ship 3'.l (2026-07-17). Fixed 16 substitutions in gdpr_nodes_phase2.json (A.9.1/A.9.3 → 9.1/9.3 ISMS clauses per rationale text) + 1 in compliance_requirements_register.yaml (A.18.1 → 9.2). Neo4j reloaded; framework_scope_guard still catches 2013 leaks defensively but source data is now clean. | SHIPPED |
| Remove scope filter on must_semantic_topk (Ship 39'.a → 39'.c) — 3 sub-arcs, one session 2026-07-25. Layer 3 fix per Ship 38'.c diagnosis. Removed `ctrl_to_leaves` scope filter from `must_semantic_topk`; orchestrator now widens `scoped_leaf_ids` with must_semantic's leaves before other signals run. Restores critic-verifier's `_build_extend_pool` discovery breadth. **Result**: 35 → 46 accepts (+31%); DPIA 4 → 11, DQA 6 → 10. Below 80-150 target. **Direct extract() test proves fix works when Phase 3 filter bypassed**: DPIA gives 17 findings incl. 10 Art.35. **Layer 0 diagnosed**: `doc_pipeline._filter_demonstrated_obligations` (Phase 3, 2026-07-05) removes cross-framework obligations from `controls` list BEFORE extract() runs — misaligned with consensus's discovery-broad intent. Ship 40 opens with 3 options: (A) conditional bypass for consensus flag, (B) accept Phase 3 + trust DEMONSTRATES posture overlay, (C) design review. Codified: (1) filters at N layers compose multiplicatively — walk ENTIRE call chain when diagnosing recall bottleneck; (2) production ≠ direct test when framework role model involved. See [[ship-39-prime-arc-retrospective-2026-07-25]]. | SHIPPED |
| Relax invariant + curator gap-fix (Ship 38'.a → 38'.c) — 3 sub-arcs, one session 2026-07-25. Two-pronged remedy per Ship 37 HITL. Delivered: (1) invariant escape clause config + code (no-excerpt candidates with score ≥1.5 AND corrob ≥3 → arbiter instead of drop); (2) 5 curator fingerprint YAML fixes with verified doc-prose keyword matches. Re-measure: 33→35 accepts (only DQA benefited; target was 60-100). Escape clause never fired. **Surfaced 4-layer bottleneck stack**: (1) xfw_proposer edge coverage (SUPPORTS ok, IMPLEMENTS/DEMONSTRATES to GDPR NOT walked); (2) doc_mappings target_leaves scope narrowing; (3) my scope filter on must_semantic_topk (chat-consensus discipline mis-applied to extraction); (4) fingerprint catalog gap (Ship 38'.b partially fixed). Production exposure clarified: DPIA loses 78% primarily due to layers 1-3, not invariant. Ship 39 direction locked: remove scope filter on must_semantic_topk (restores critic-verifier's discovery breadth). Codified: (1) signal filter discipline is domain-specific — chat filters to query, extraction should NOT filter signals to doc scope; (2) curator fixes don't help if scope narrowing precedes them. See [[ship-38-prime-arc-retrospective-2026-07-25]]. | SHIPPED |
| Recall HITL on invariant drops (Ship 37'.a → 37'.c) — 3 sub-arcs, one session 2026-07-25. Sampled 25 no-excerpt above-floor candidates that Ship 36's invariant dropped; classified 13 correctly-dropped / 6 should-have-accepted / 6 uncertain (52% strict, 76% conservative). Lands in **60-80% RELAX zone** per 37'.a thresholds. All 6 should-have-accepted are `proc_*` procedure-shape MUSTs on docs where the MUST is the primary subject (DQA/DPIA/Processor Ops docs). **Diagnosis**: fingerprint catalog gap on procedure-shape MUSTs — `proc_*` keywords match artefact-nouns; procedural docs use verb-driven prose. Not a fundamental invariant flaw. Config toggle added: `ExtractionConsensusConfig.no_excerpt_auto_drop` (default True preserves Ship 35 shape) enables running consensus without the invariant for HITL sampling. Ship 38 direction locked per user "relax + fix gap + test": (1) relax invariant with score+corroborators threshold to catch high-confidence primary-subject cases, (2) curator arc on ~200 `proc_*` fingerprint YAMLs adding verb-pattern keywords, (3) re-measure. **Codified**: (1) sample size + uncertain band matter for verdict thresholds — middle-band signals need n=50+; (2) invariants + catalog gaps interact — right fix touches both. See [[ship-37-prime-arc-retrospective-2026-07-25]]. | SHIPPED |
| First cutover test on Arion demo (Ship 36'.a → 36'.c) — 3 sub-arcs, one session 2026-07-25. `USE_CONSENSUS_EXTRACTION=1` flipped on demo tenant; all 5 Ship-10-baseline docs re-extracted via real `/api/v1/admin/uploads/{id}/reextract`; 5 `intake_consensus_log` rows landed; writer accepted consensus-emitted findings via `inference_source='fingerprint_match'` compat; xfw_proposer downstream ran; chat spot-check clean. **Surprise numbers**: 33 total accepts across 5 docs (DQA 4 / DPIA 4 / RoPA 5 / Consent 6 / Processor Ops 14). vs Ship 32 Path A 272 = **88% reduction**. Arbiter zone → 0 (no LLM arbiter calls needed). Root cause: no-excerpt-auto-drop invariant is more aggressive than Ship 35'.a design predicted; previously-accepted scope-signal-only candidates (e.g. `doc_mappings_target 0.60 + explicit_ref 1.00`) now drop for lack of fingerprint excerpt. Semantically correct (auditor needs evidence text) but aggressive. Eval 231/232 baseline held (chat pipeline unaffected — different subsystem). **Codified**: (1) shadow measurement predicts partial reality — first real cutover tests are irreplaceable; (2) invariants added post-measurement need their own measurement — Ship 34'.c HITL sampled arbiter zone but not accepted zone. **Ship 37 opens as recall HITL** to sample the 502 dropped candidates and decide whether the aggressive shape is production-appropriate. See [[ship-36-prime-arc-retrospective-2026-07-25]]. | SHIPPED (flag=1 on demo) |
| Consensus cutover behind env flag (Ship 35'.a → 35'.c) — 3 sub-arcs, one session 2026-07-25. Makes Ship 33's consensus extraction module tenant-reachable. **USE_CONSENSUS_EXTRACTION env flag in `rag/intake/extractor.py`** — when ON, `_extract_via_consensus` REPLACES fingerprint + critic-verifier + concat entirely; default OFF (zero behavior change on default installs). Also ships **no-excerpt-auto-drop aggregator invariant** per Ship 34'.c finding (candidates with no fingerprint_excerpt drop deterministically before arbiter zone; ~5x LLM cost reduction on arbiter pass). Trade-off accepted: full replacement loses LLM discovery pass (~30-50% of findings on procedural docs came from body-text candidates no deterministic signal surfaces); bounded to opted-in tenants by default-OFF. Retirement of old code paths deferred 4-6 weeks. Rollback: unset env var + API restart. **Codified**: (1) OpenAI quota budgeting is real engineering concern — stacked measurement + eval jobs consumed the account quota mid-session; (2) default-OFF cutover flags enable ship-then-validate (mirror of Ship 1 chat consensus's default-ON-with-kill-switch; opposite polarity because extraction cutover has larger blast radius). See [[ship-35-prime-arc-retrospective-2026-07-25]]. | SHIPPED (default OFF) |
| Consensus validation + telemetry (Ship 34'.a → 34'.c) — 3 sub-arcs, one session 2026-07-25. Prerequisite arc that gated Ship 35 cutover of the Ship 33 consensus extraction module. Delivered: schema_v89 `intake_consensus_log` (per-doc verdicts + LLM movement + signals + latency + cost; retention_class='diagnostic'); `rag/intake/consensus_extraction/log.py` writer (silent-fail); measurement script two-pass enhancement (aggregator-only then arbiter-enabled — diff identifies LLM verdicts); 94 arbiter-zone candidates captured to JSON. **HITL validation: 20 of 20 stratified sampled rejects → correct-reject (100%)**. Two failure modes cleanly caught: no-excerpt candidates (17/20) and Ship 32 poster-child TOC-line multi-attribution (3/20). Cutover APPROVED. Codified 2 lessons: **HITL bounds where telemetry can't** (extreme rates need human sampling before trusting); **signals without evidence should exit early** (scope-signals ≠ evidence-signals; scope alone should not authorize LLM review). Follow-on tuning insight for Ship 35+: 85% of arbiter zone is no-excerpt single-signal candidates that should auto-drop pre-LLM. See [[ship-34-prime-arc-retrospective-2026-07-25]]. | SHIPPED |
| Extraction consensus refactor (Ship 33'.a → 33'.c) — 3 sub-arcs + design pivot, one session 2026-07-25. Redirected mid-flight from 40-LOC semantic-fit gate patch to full consensus refactor after user framing: "automated evidence collection is a key feature trending heavily — get this right for documents." Built `rag/intake/consensus_extraction/` (~1250 LOC across 15 files, mirroring Ship 1 chat-consensus shape): types + config + aggregator + orchestrator + 8 signals (fingerprint_keyword, doc_mappings_target, must_semantic_topk, explicit_ref, per_protocol_scope, semantic_fit_gate, content_shape_penalty, evidence_uniqueness) + LLM batched gatekeeper. **Path A→B on 5-doc corpus**: 272 → 197 findings (28% reduction); **Processor Ops 149→35 (77% reduction — Ship 32 multi-attribution primary case addressed)**. LLM arbiter: 93 of 94 borderline candidates → drop, 1 → accept. Codified 4 lessons: per-candidate signals don't solve cross-candidate problems; correlated signals don't corroborate; wiring bugs invisible without measurement; LLM arbiter high-precision on borderline. Deferred to follow-on arc: write-path cutover (env flag + retire concat), intake_consensus_log schema, threshold tuning automation, HITL review of the 93 rejects. See [[ship-33-prime-arc-retrospective-2026-07-25]]. | SHIPPED (shadow mode) |
| 5-doc re-extraction measurement (Ship 32'.a → 32'.c) — 3 sub-arcs, one session 2026-07-25. First forward-motion arc after 4 maintenance arcs (28→31). Re-extracted the 5 Ship-10-baseline procedural docs. **Numbers**: 265 findings (vs Ship 10 97, Ship 11'.e ~198), 100% deterministic grounding_method (above Ship 27's 89.2%). **Precision finding**: Processor Ops surged 30 → 143 (121 fingerprint_match); spot-check revealed 9% `evidence_text` uniqueness — 103/121 findings share evidence with ≥5 others; ONE bullet-list line produces 43 findings across 43 MUSTs. **Root cause**: sentence-level multi-MUST attribution. Ship 29's anchor injection made anchors per-leaf-distinctive (Ship 17'.b's motivating collision 48→0 leaves), but common non-anchor words in one sentence intersect with many controls' full token sets simultaneously. Ship 16'.b runtime gate checks same-token-set-across-leaves; doesn't catch different-sets-on-same-sentence. Codified: measurement arcs earn their keep (catalog metrics ≠ extraction reality); gates cover their design space, not the whole space (Ship 29 moved the failure mode outside 16'.b/11'.c/11'.d design). **Ship 33 opens for the fix** (per-evidence-text cap OR anchor-set overlap check). See [[ship-32-prime-arc-retrospective-2026-07-25]]. | SHIPPED |
| Loader SELECT audit (Ship 31'.a → 31'.c) — 3 sub-arcs, one session 2026-07-25. Direct follow-on to Ship 30's discovery. Audit expanded across load-bearing tables (`posture_controls`, `client_facts`, `posture_assertions`, `client_documents`, `document_uploads`). **2 new bugs fixed** in `posture_loader.py`: (1) `_fetch_not_assessed_obligation_rows` at line 466 was missing `confirmation_status` (same shape as Ship 30 — DEMONSTRATES-materialized obligations wrongly emit `[DRAFT]`); (2) `load_client_facts` at line 882 was missing 8 semantic fields including `uk_data_subjects` (which is True on Arion → UK-scoped obligations were wrongly treated as inapplicable). Both fixes: expand SELECT column list + expand `defaults` dict. **Regression guard**: new `tests/test_loader_select_columns.py` — static grep-shape check asserting specific loader function bodies contain required semantic column identifiers. Codified: (1) loader whitelist ≠ schema truth — same PR that adds a semantic column must extend loader SELECTs or add to `_ASSERTIONS`; (2) whitelist SELECT is load-bearing, `SELECT *` is defensive — choose per site; (3) user pushback expands audit scope productively — original posture_controls-only scope would have missed the client_facts bug. See [[ship-31-prime-arc-retrospective-2026-07-25]]. | SHIPPED |
| Demo tenant queue hygiene (Ship 30'.a → 30'.c) — 3 sub-arcs, one session 2026-07-25. Triggered by user report ("42 items I didn't upload; chat says DRAFT"). Investigation revealed (a) 102 pending findings from Ship 11'.e measurement run left orphan on `client_documents` IDs (not `document_uploads`), (b) 394 dormant `is_active=FALSE + review_status='pending'` rows from prior sweeps, (c) **cross-tenant bug**: `rag/posture_loader.py::load_posture` SELECT never fetched `confirmation_status` — every rec had it as None, `CaseFile.needs_draft_tag()` returned True universally, EVERY assessed posture across ALL tenants was emitting `[NC-DRAFT]` in chat since load_posture was written. Ship 30'.b delivered: (1) soft-delete 102 + archive 394, (2) flip A.7.4.6 + B.8.4.1 ISO 27701 postures `draft` → `document_confirmed`, (3) add `confirmation_status` to the SELECT (fixes DRAFT surfacing on every tenant), (4) add non-DRAFT example to `LLM_OUTPUT_RULES` + "use digest verdict tag verbatim" rule, (5) new `scripts/dev/demo_tenant_cleanup.py::cleanup_measurement_residue()` helper + retrofit `critic_verifier_ab.py` + `measure_ship11_reextraction.py` (docstring lied about being dry-run — corrected) to call it in `try/finally`. **Codified**: multi-path-to-same-write-surface is drift-by-construction (parallels Ship 29); the fix is a shared exit contract, not consolidation. Eval 231/232 baseline held (a first-eval FAIL was Postgres pool poisoning from external `AdminShutdown`, not a code regression). See [[ship-30-prime-arc-retrospective-2026-07-25]]. | SHIPPED |
| Generator consolidation (Ship 29'.a → 29'.c) — 3 sub-arcs, one session 2026-07-24. Consolidated `generate_27701_fingerprints.py` (Ship 17'.b/c specialized) into `gen_leaf_scan_catalog.py` (general per-leaf CLI). Ported `_TITLE_META_NOISE` + `_title_anchor_tokens` + `_augment_with_anchor`; extended `_fetch_leaves` with 4 modes (leaf/control/standard/leaf_ids) all including `RequirementNode.title`; anchor injection wired AFTER Ship 28'.b singleton suppression + BEFORE `[:8]` cap. New CLI flags: `--standard`, `--family`, `--all-auto-generated`, `--dry-run`. Regenerated **395 of 397** auto-gen files (201 hand-authored guard-preserved); anchor coverage broadened from Ship 17's 6 family × standard combos to all auto-gen files. Ship 17'.b motivating collision `[review, date, planned, interval]`: 48 leaves → 0. Deleted `generate_27701_fingerprints.py` + `regenerate_leaf_scan_singleton_fix.py`. **Codified: multi-path-to-same-destination is drift-by-construction; consolidation is the durable fix, discipline is fragile.** Eval 231/232 baseline held. See [[ship-29-prime-arc-retrospective-2026-07-24]]. | SHIPPED |

## Key memory entries

Future sessions should read these before product work:

- [[cascade-arc-retrospective-2026-06-30]] — full cascade arc summary; supersedes the
  individual `cascade_*` and `relationship-model-*` memos as the entry point
- [[dejargonize-ux-pass-2026-07-01]] — the natural-language UX pattern now in
  force across every tenant-facing surface; conventions for helpers +
  vocabulary future work must preserve
- [[tier4-starter-kit-arc-2026-07-02]] — structured templates_block in chat +
  Get Started sidebar mode; the "starter kit" surface for fresh tenants.
  Establishes the pattern: emit structured payload → render as UI card, don't
  inject text into answer_text.
- [[product-principle-evidence-stored-vs-cited]] — the cite/store coexistence model
- [[product-principle-cite-expose-and-track]] — cite-mode: expose + track,
  tenant attests. No silent machine attestations. Codified 2026-08-21 in Ship 92'.f.
- [[templates-v2-anchors-complete-2026-06-25]] — the 20 v2 anchor templates
- [[template-tenant-profile-2026-06-26]] — placeholder substitution
- [[evidence-class-breakdown-backend-2026-06-26]] — the dashboard drill-in surface
- [[stage1-queue-sweep-2026-06-27]] + [[feedback-validate-set-membership]] — recent ops/lessons
- [[curation-a67-remote-working-promotion-2026-06-27]] — the catalog's last single-leaf hole closed

## Tenant-facing language conventions (dejargonize pass 2026-07-01)

Every tenant-facing surface now reads as natural compliance
language rather than system slugs. When adding or editing text
that a tenant might see, preserve these conventions:

- **No `snake_case` slugs in visible text.** `evidence_type='review_record'`
  renders as "review record" (or Title Case in headers). Helpers
  in `rag/posture/advisory.py`: `_humanize_evidence_type()`,
  `_humanize_leaf_label()`. Client-side mirrors in
  `static/arioncomply.html`: `humanizeSource()`, `humanizeStandardId()`,
  `humanizeNotifKind()`, `humanizeSlug()`, `humanizeEngineReason()`,
  `humanizeStageName()`, `humanizeErrorType()`.
- **No raw `req:X:Y` leaf ids.** Show the control ref (e.g. `A.5.15`)
  or the leaf `title` from the catalog; keep the full id in
  `data-` attributes / HTML comments for audit provenance only.
- **No raw `ISO27001:2022` standard tags.** Use `humanizeStandardId()`
  → "ISO 27001:2022".
- **No system-internal event edge names** (`TRIGGERS_OBLIGATION`,
  `BLOCKS_WHEN`, `EXPECTS_FOLLOWUP_EVENT`) in tenant prose. Explain
  the intent instead.
- **Vocabulary:** cascade "implications" → "follow-ups"; "cascade
  events" → "recent events"; MUST/SHOULD → "required element" /
  "recommended addition"; "engine proposal" → "posture proposal";
  "extractor engine" → "extraction"; pipeline stage names
  `read/enrich/extract/write/xfw` → `read/classify/extract findings/
  post to posture/cross-framework`; `inference_source` slugs mapped
  via `_SOURCE_HUMAN` (extracted → "uploaded document", etc.).
- **Error messages:** tenant-UI-facing 4xx/5xx `HTTPException`
  details are sentences, not field-name-driven strings. Raw
  exception `str(e)` never surfaces — traceback goes to the log,
  the tenant sees a short apology. Admin/dev-facing paths
  (`/api/v1/admin/*`, `structured_events` validation) stay
  technical intentionally.
- **Deterministic backend labels first.** Where the LLM might
  echo raw slugs (chat prose polish), humanize in the prompt
  context too so the LLM never sees the debug form.

The Evidence Package rewrite (`rag/posture/evidence_package.py`)
is the canonical template — it reuses `business_description` on
RequirementNode + `EvidenceRequirement.description` rather than
hand-authoring per-node display text, which scales to arbitrary
standards without re-authoring each leaf. Apply the same
"reuse curated fields" principle for any new tenant-facing
surface.

Corresponding memory entry: [[dejargonize-ux-pass-2026-07-01]].

## VM Access
```bash
ssh -i ~/.ssh/arioncomplySK.pem arionlabs@172.211.244.144
cd /data/arioncomply
```

## Start / Stop
```bash
# Start API
PYTHONPATH=/data/arioncomply python3 api_server.py > /tmp/api.log 2>&1 &

# Stop API
kill $(lsof -ti:8080) 2>/dev/null

# Check logs
tail -f /tmp/api.log
grep -E "ERROR|WARNING" /tmp/api.log
```

## Periodic sweep scheduler

`rag/scheduler/tick.py` is a stateless one-shot: each invocation
generates a `tick_id`, runs every registered work type, writes
one `sweep_log` row per (tick, work_type), exits. Cadence lives
outside the code — systemd timer fires the tick every 30 min.

### One-time install (Ship 3'.a, 2026-07-17)

```bash
sudo /data/arioncomply/ops/install_sweep_timer.sh
```

The installer copies `ops/systemd/arioncomply-sweep.{service,timer}`
into `/etc/systemd/system/`, reloads systemd, enables + starts the
timer. Idempotent — safe to re-run.

### Manual tick (dev / debugging)

```bash
# Run every work type once
PYTHONPATH=/data/arioncomply python3 -m rag.scheduler.tick

# One specific work type
PYTHONPATH=/data/arioncomply python3 -m rag.scheduler.tick --work fact_recompute

# Dry-run (reads config, doesn't mutate client_facts)
PYTHONPATH=/data/arioncomply python3 -m rag.scheduler.tick --dry-run --json
```

### Work types (schema_v65 CHECK constraint)

- `fact_recompute` — reads `fact_source_config`, refreshes
  `client_facts` for tenants past `refresh_days`.
- `notification_delivery` — reads undelivered `tenant_notification`,
  delivers per `tenant_notification_channel` (email + Slack).
- `overdue_followups` — stub (counts cascade events past
  `followup_due_at`; delivery lands with the producer arc).
- `freshness_expiry` — stub (counts stale Comply postures; full
  freshness-downgrade lands with its own arc).

### Health check

```sql
-- Recent ticks (paste in psql -U arioncomply -d arioncomply_compliance)
SELECT tick_id, work_type, status,
       items_scanned, items_acted_on, items_error,
       (extract(epoch from (completed_at - started_at)) * 1000)::int AS ms
  FROM sweep_log
 WHERE started_at > now() - interval '2 hours'
 ORDER BY started_at DESC LIMIT 20;

-- Any failed ticks in the last day?
SELECT * FROM sweep_log
 WHERE started_at > now() - interval '1 day' AND status = 'failed';
```

### Disabling

```bash
sudo systemctl disable --now arioncomply-sweep.timer
```

## Run Evals (always run before restarting after code changes)
```bash
PYTHONPATH=/data/arioncomply python3 tests/eval_suite.py \
  --csv results/eval_$(date +%Y%m%d_%H%M).csv --pause 2 \
  2>&1 | grep -E "PASS|FAIL|RESULTS"
# Must be 223+/226 PASS before any restart (226 cases as of Ship 9'.a, 2026-07-20).
# Historically-stochastic cases have been root-caused and stabilised:
#   #1 + #5 (partial) — STABILISED 2026-06-23 via schema_v43 tenant_must_overrides
#         (cloud-only A.5.15:physical_rules marked N/A; advisory no
#         longer leaks "physical" into access-rights chat answers).
#         See [[tenant-must-overrides-v43-2026-06-23]]. #5 still has
#         residual "physical" trip from the LLM voluntarily mentioning
#         logical-vs-physical scope (rare).
#   #2  — STABILISED 2026-06-15 by dropping A.5.26 ref lock (state drift; see
#         [[feedback-eval-state-drift]]). Structural assertions (NC + min_findings)
#         only.
#   #24 + #25 (Art.32 / Art.5) — STABILISED 2026-07-14 (Ship 1.6-1.7): resolver
#         xfw decoupling + Signal C question_type lock + dedicated xfw budget
#         lane. Cross-framework bridges surface via data-driven bridge footer
#         (not question_type-gated).
#   #21 — STABILISED 2026-07-13 (9443aeb): NOT phrasing jitter — was 60s
#         LLM timeout too tight + verify+correct loop truncating at
#         max_tokens=1500. Fix: skip verify+correct for
#         implementation/gap_analysis queries + timeout_s=180. See
#         llm_answer.py:783,1533.
#   #7 (A.8.19 ChatGPT) — STABILISED 2026-07-15 (Ship 1.7d): DOCUMENT_TOPIC_MAP
#         entries for chatgpt/ai tools/llm use → A.8.19. Signal C emits at
#         curated_lexicon_weight=1.00 (bumped from 0.30). Curator learnings
#         are now top-tier signal weight — highest of any signal.
# Baseline: 225/226 PASS + 1 WARN + 0 FAIL as of Ship 9'.a (2026-07-20).
# Prior: 219/220 PASS as of Ship 8'.b. Ship 9'.a added 6 B.8.3-5
# processor-mirror cases (#216-221) — first eval coverage of B.8.3-5.
# Ship 2'.n retired the legacy rank_and_answer path; case-file flow is
# the ONLY path — no CASEFILE_ENABLED flag remains.
#   #14, #33 — STABILISED 2026-07-16 in Ship 2'.j via deterministic
#         preservation-check footer. Was: LLM stochastically dropped
#         acronym / ref from DEFINITION-query prose. Now: repair pass
#         appends missing ref/verdict/[DRAFT] as an audit footer.
#   #200 — pre-existing gap_analysis vs posture_check mismatch on
#         "NC findings on identity"; Signal C doesn't fire on this
#         phrasing. Own arc.
# Any regression below 223/226 blocks restart. Prefer root-causing new
# intermittent failures over labeling them "stochastic" — see #21 arc + Ship 1
# consensus architecture below.
# Whenever you add a user-facing feature/fix, append an EvalCase that would
# have failed pre-change and passes post-change — see the feedback-memory rule.
```

## Test Streaming
```bash
curl -s -N "http://localhost:8080/api/v1/chat/stream?question=what+are+our+NC+findings&session_id=test_1" \
  -H "X-API-Key: arion_dev_key_2026"
```

## Test Sync Chat
```bash
curl -s -X POST http://localhost:8080/api/v1/chat \
  -H "X-API-Key: arion_dev_key_2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "what are our NC findings?"}' \
  | python3 -m json.tool
```

## Operational playbook — troubleshooting deployments

For debugging any deployment (this VM or a customer install), read
[[CLAUDE_DEPLOY_GUIDE.md]] at the repo root. It's the AI-first ops
playbook: symptom → verify → fix triples, structured pointers to
every diagnostic surface, common ops queries, and the codebase
orientation index.

**If you are running the pre-POC dry-run** on a fresh Azure VM (or
similar fresh install), read [[CLAUDE_DRYRUN.md]] first — it's the
mission brief with phase-by-phase steps, state file convention,
report spec, safety guardrails, and escalation criteria. Purpose-built
for autonomous end-to-end execution. Companion documents:

- `scripts/ops/diagnose.sh` — one-command diagnostic bundle
- `docs/error_catalog.html` — stable `ARION-*` error codes
- `GET /api/v1/admin/deployment/status` — live status (admin:status scope)

Shipped in Ship 48'. See [[ship-48-prime-a-deployment-diagnostics-design-2026-07-28]].

## Key Files

### Backend / pipeline
- `api_server.py` — FastAPI server, all endpoints, auth
- `rag/arion_graph.py` — LangGraph pipeline, nodes, checkpointers
- `rag/llm_answer.py` — LLM answer generation, layered node presentation
- `rag/classifier.py` — Query classification, CLEAR_INTENT_PHRASES
- `rag/resolver.py` — Per-taxonomy data source dispatch
- `rag/graph_expander.py` — Neo4j graph traversal, xfw edge expansion

### Posture + advisory
- `rag/posture_loader.py` — load_posture, tenant context cache
- `rag/posture/advisory.py` — `build_per_must_advisory_data`, `build_evidence_class_breakdown`
- `rag/posture/fulfilment_engine.py` — per-leaf MUST satisfaction
- `rag/posture/engine_runner.py` — `evaluate_one_control`

### Intake (uploads)
- `rag/intake/readers.py` — file readers (xlsx incl. `_arion_meta` detection)
- `rag/intake/extractor.py` — LLM extraction + templated fast paths (md + xlsx)
- `rag/intake/posture_writer.py` — `write_findings` + per-tenant RLS GUC
- `rag/intake/doc_pipeline.py` — orchestrator, tenant cross-check, telemetry

### Templates / native formats
- `rag/templates/renderer.py` — markdown render with tenant_profile substitution
- `rag/templates/xlsx_renderer.py` — Excel (Register + Guidance + Document Fields + hidden _arion_meta)
- `rag/templates/docx_renderer.py` — Word (Heading/Quote/Bullet, ☐/☒, markers preserved)
- `db/templates/req__*.md` — 645+ template scaffolds (filesystem source of truth)
- `scripts/stage1_queue_sweep.py` — bulk-approve / soft-delete pending findings (uses loader's canonical catalog union)

### Catalog
- `enrichment/documents/document_requirements.py` — single source for ALL_EVIDENCE_REQUIREMENTS + ALL_DERIVED_SPECS
- `enrichment/documents/load_to_neo4j.py` — Neo4j sync + orphan sweep
- `enrichment/templates/load_to_postgres.py` — Postgres `templates` table sync

### UI
- `static/arioncomply.html` — single-page UI (Dashboard / Queue / Chat / Documents / Profile modes; streaming chat)

### Tests
- `tests/eval_suite.py` — 199-case end-to-end eval suite

## Architecture
Query → classify node → retrieve node → update_session node → END
↓                ↓
clarify node    (LLM rank_and_answer OR Postgres short-circuit)

### Chat pipeline — Ship 1 consensus architecture (2026-07-14)

The classify node runs **retrieval-first consensus** across 7
deterministic signals before falling back to the LLM classifier.
Curator-authored mappings dominate; LLM is a bounded arbiter, not
a free-form decider.

**Signal weights** (see `rag/consensus/types.py`):
- Signal B (`explicit_refs`, regex) — 1.00 — user typed a literal ref
- **Signal C (`curated_lexicon`) — 1.00 — highest tier — DOCUMENT_TOPIC_MAP +
  CLEAR_INTENT_PHRASES. "Optimal place to enhance as we learn" —
  when a curator maps a topic phrase to a ref, that mapping is
  authoritative.**
- Signal F (`framework_hint`) — 0.20 — "GDPR"/"ISO 27001" tokens
- Signal G (`session_context`) — 0.10 — deictic follow-up refs
- Signal A (`retrieval`) — cosine score in ~0.35-0.70 — ChromaDB semantic
- Signal E (`graph_tightness`) — ±0.05/0.10 — family clustering modifier
- Signal D (`posture_boost`) — 0.15 — tenant NC/OFI relevance

**Aggregator** (`rag/consensus/aggregator.py`) sums signal weights per ref.
Verdict = confident when top_score >= 0.35 AND ≥2 corroborators (with
`llm_fallback_needed=True` on insufficient).

**Gatekeeper** (`rag/consensus/gatekeeper.py`) is a **bounded LLM arbiter**:
- Approves, modifies (refs / verdict only), or rejects — **cannot invent**
- Signal C's `question_type` is HARD-LOCKED against LLM override (`_signals_lock_question_type`)
- Signal B's `framework` is HARD-LOCKED against LLM override
- Applied only when signals need arbitration; hard-anchor early-exit skips it
- Design principle: deterministic signals lead, LLM fills gaps. NEVER lets
  the LLM override a signal that already fired cleanly.

**No escape hatch** as of Ship 2'.o (2026-07-17) — consensus always
runs. The intra-consensus fallback to the LLM classifier on
`insufficient` verdict is design-intended, not a kill switch.
To roll back this arc, `git revert` the Ship 2'.o commit.

**Observability**: every consensus decision logged to `chat_consensus_log`
(schema_v67). Column `llm_fallback_used` is the tuning signal.

**When you edit routing behaviour**: prefer adding CLEAR_INTENT_PHRASES /
DOCUMENT_TOPIC_MAP entries over prompt-tuning the LLM classifier or
gatekeeper. Curator additions are top-tier signal weight; prompt
instructions to LLMs are soft signals that get ignored ~5-15% of the time.

### xfw dedicated lane — Ship 1.7 (2026-07-15)

Cross-framework nodes have their own budget separate from primary
(cited + parents + children + lateral). As tenants enrol more
frameworks (SOC2/NIS2/DORA on top of ISO 27001 + GDPR + ISO 27701),
xfw doesn't get squeezed by budget contention.

`rag/graph_expander.py`:
- `NODE_BUDGET_PRIMARY` — cited + parents + children + lateral
- `NODE_BUDGET_XFW` — dedicated xfw lane
- `_prioritise_xfw` ranks by relationship strength (IMPLEMENTS > SUPPORTS
  > ENABLES > GOVERNANCE) + direction (outbound-from-cited first) +
  anchor proximity + tenant scope applicability
- `ExpandedContext.xfw_nodes` — first-class field
- `GraphResult.xfw_nodes` — carried through resolver to rank_and_answer

**Bridge footer** (`llm_answer.py:1595+`) is **data-driven** — fires
whenever `xfw_nodes_list` is non-empty AND query has an article ref,
regardless of question_type routing. Previously gated on
CROSS_FRAMEWORK routing only; that coupling is removed.

**Scope guard** (`framework_scope_guard`) sees ALL resolver-surfaced refs
(primary + secondary + xfw), not just the LLM's LAYER 1/2 shortlist —
so it stops stripping legitimate xfw citations.

### Case-file pattern — Ship 2' (2026-07-15)

`rank_and_answer`'s only path as of Ship 2'.n (2026-07-16). Motivation:
the legacy path's prompts averaged **21,731 tokens** (14-day window,
peak 61,827), diluting the LLM's attention on ~550 tokens of actual
answer. The case-file pattern hands the LLM a compact digest and
repairs its output deterministically.

**Flow** (inside `rank_and_answer._casefile_flow`):
1. Build `CaseFile` (`rag/casefile/types.py`) wrapping the resolver's
   posture + graph_nodes + intent + tenant + session + last_entity.
2. Render `(system, user)` prompts via `build_prompt_pair(cf)` —
   ~450 + ~200 tokens on realistic queries (33× reduction).
3. LLM call — no rank rubric, direct answer. Verify+correct SKIPPED.
4. `extract_preservation_spec(cf)` builds the MUST-preserve set:
   * `required_refs` = cited refs (with data) ∪ top-3 ranked posture
   * `draft_refs` = required refs whose posture is unconfirmed
   * `verdict_by_ref` = {ref: NC|OFI|Comply}
   * `bridge_footer` = deterministic xfw bridge line
5. `check_and_repair(answer, spec, cf)` appends deterministic footers
   for any dropped refs / verdicts / [DRAFT] tags / bridge lines.
   APPEND-ONLY — never rewrites LLM prose.
6. Log to `chat_casefile_log` (schema_v68) — silent-fail.

**Digest shape** (fixed slots, empty sections omitted):
```
QUERY: ...
DEICTIC WITHOUT CONTEXT: ... (optional)
OPEN INCIDENTS: ... (optional)
POSTURE (showing N of M assessed):
- A.5.18 [NC-DRAFT] register incomplete
- ...
XFW BRIDGES:
- Art.32 ← A.5.15 [Comply], A.5.18 [NC-DRAFT]
OBLIGATIONS:
- A.5.18: Access rights shall be...
DOCUMENTS: (optional)
SESSION active: A.5.18
SCOPE: ISO 27001 + GDPR
```

**Slim system prompt** (~450 tokens vs 3,100): persona + 7 output
rules + one-line NC/OFI/Comply glossary. Drops the LAYER-1/LAYER-2
explainer + SELECTED_PRIMARY rubric + N/A-controls list (moved into
the SCOPE section per turn).

**Preservation guarantees** (repair pass appends missing elements):
1. `required_refs` — every cited ref with data must appear
2. `draft_refs` — [DRAFT] tag survives for unconfirmed postures
3. `verdict_by_ref` — NC/OFI/Comply prefix adjacent to each ref
4. `bridge_footer` — `↳ Bridges to ISO 27001 for Art.X: ...`

Missing elements get consolidated into a `↳ Compliance facts: ...`
footer — same append-only pattern as Ship 1.14's bridge footer.

**No escape hatch** — Ship 2'.n retired `CASEFILE_ENABLED` + the
legacy fallback path. If the case-file flow errors, the error
surfaces to the caller (fail-loud). To roll back this arc, `git
revert` the Ship 2'.n commit — no runtime toggle.

**Observability**: `chat_casefile_log` records `case_file_summary`,
prompt-token breakdown, `repair_events[]`, `footers_added[]`,
latency. Tuning signal: high `repair_events_count` on the same
kind indicates the digest needs to surface that element more
prominently OR the preservation trigger is too broad.

Corresponding modules:
- `rag/casefile/types.py` — CaseFile
- `rag/casefile/digest.py` — build_prompt_pair, section renderers
- `rag/casefile/preservation.py` — extract_preservation_spec
- `rag/casefile/repair.py` — check_and_repair
- `rag/casefile/log.py` — log_casefile
- `db/schema_v68_chat_casefile_log.sql`

### Answer layers
- Layer 1: Primary standard nodes (ISO 27001 with posture NC/OFI/Comply)
- Layer 2: Cross-framework nodes (GDPR xfw edges from Neo4j)
- Short-circuit: document_inventory, scope N/A → direct Postgres answer, no LLM

### Object-ID discipline (Ship 2'.i onward)

Naming rule (enforce at review time):
- Field called `X_id` → MUST be the canonical UUID.
- Display names → `X_name` (never `X_id`).
- URL-safe stable identifiers → `X_slug`.
- Composite refs → `X_ref` (bare "A.5.18") or `X_node_id` (composite
  "ISO27001:2022:A.5.18").

Prefer the typed classes in `rag/id_types.py` for new code:
- `TenantUUID(value)` — validates at construction, raises ValueError
  on slug/display-name/None inputs. Retires the `_is_uuid_shape()`
  band-aid pattern.
- `NodeId(value)` — parses composite `STANDARD:VERSION:REF`; has
  `.standard_id` / `.version` / `.ref` accessors. Retire inline
  `.split(":")` when touching a site.
- `ControlRef`, `LeafId` — regex-validated at construction.

Migration is opportunistic: use the types in NEW code, migrate old
sites when touched. Not a big-bang refactor.

Ship 2'.i cleared the load-bearing case: `arion_state.py` was setting
`state["tenant_id"] = tenant.name` (display name). Every downstream
writer that cast to `::uuid` silently dropped rows for a display-name
tenant_id inside a "best-effort" try/except. Fixed by (1) requiring
`TenantUUID`-shaped input at `make_initial_state`, (2) separating the
display name into `state["tenant_display_name"]`, (3) validating in
`_log_casefile_turn` as defence-in-depth. See
[[ship-2-prime-i-id-discipline-and-digest-fix-2026-07-16]] for the
audit that surfaced the sprawl.

Follow-up arcs (post Ship 2'.i):
- Ship 2'.j (2026-07-16) — closed 3 residual eval fails (#11, #31, #214)
  via role-model-aware digest guidance + document-content MUST
  enumeration. Baseline: 207/208.
- Ship 2'.k (2026-07-16) — FastAPI Pydantic path-param validators
  (36 endpoints) + fail-loud on log-write silent-fails. Baseline: 207/208.
- Ship 2'.l (2026-07-16) — session_id shape validation +
  build_thread_id() using full tenant UUID (was `[:8]` — 2^32
  collision surface eliminated).
- Ship 2'.m (2026-07-16) — retired 21 inline `node_id.split(":")`
  sites via `ref_of()` / `standard_of()` helpers.
- Ship 2'.n (2026-07-16) — retired the legacy `rank_and_answer` body
  (~912 LOC) + inline `_infer_primary_std` + file-scope
  `_pick_primary_std` + `CASEFILE_ENABLED` env flag. The case-file
  flow is now the only path — no gate, no fallback. Full eval:
  207/208 PASS.
- Ship 2'.o (2026-07-17) — retired `USE_LEGACY_CLASSIFIER` kill-
  switch + `consensus_layer_enabled()` config helper. Consensus
  always runs; intra-consensus fallback to LLM classifier on
  `insufficient` verdict stays (design-intended). All 227 unit
  tests pass across id_types + api_types + casefile + consensus.

### Session persistence
- Sync chat: PostgresSaver (arioncomply_sessions DB)
- Streaming: AsyncPostgresSaver (same DB)
- thread_id format: `{tenant_id[:8]}:{session_id}`

### Intake lanes
- **Templated markdown** — `<<MUST item:X>>` markers + edit zones → deterministic fast-path extraction; auto-approved
- **Templated xlsx** (round-trip) — `_arion_meta` hidden sheet → per-column + per-doc-field bindings; auto-approved; sample-stored in `tabular_evidence_rows`
- **Workbook YAML** (xlsx → workbook_persistence) — deterministic per-MUST binding via YAML matchers
- **Generic LLM extraction** — fallback for non-marker docs; goes through Stage-1 review queue

RETIRED 2026-07-04: the per-MUST **web form** lane
(`POST /api/v1/dashboard/control/{ref}/template` + textareas in
the advisory panel). Redundant with the templated download →
upload path. 5 legacy `inference_source='form'` findings retagged
to `templated`. Endpoints removed; UI textareas replaced by a
read-only "Still needed" list.

### Auto-approve discipline
`inference_source = 'templated'` → auto-approved at write
(tenant-authored, no inference uncertainty). All others land
`pending` for Stage-1 HITL. Surfaced via `/api/v1/stage1/auto-approved`.

## Databases
```bash
# Compliance data
psql -U arioncomply -h 127.0.0.1 -d arioncomply_compliance

# Session persistence
psql -U arioncomply -h 127.0.0.1 -d arioncomply_sessions

# Key tables
# arioncomply_compliance: posture_controls, api_keys, document_uploads
# arioncomply_sessions: checkpoints (LangGraph state)
```

## Neo4j
```bash
# Check node/edge counts
python3 -c "
from neo4j import GraphDatabase
import os; from dotenv import load_dotenv; load_dotenv('.env')
d = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')))
with d.session() as s:
    print('ER:', s.run('MATCH (n:EvidenceRequirement) RETURN count(n) AS c').single()['c'])
    print('ChecklistItem:', s.run('MATCH (n:ChecklistItem) RETURN count(n) AS c').single()['c'])
"
# Expected (2026-06-27, post A.6.7 promotion): 648 EvidenceRequirement
# + 4306 ChecklistItem nodes. Python catalog (the canonical union of
# ALL_EVIDENCE_REQUIREMENTS + ALL_DERIVED_SPECS.direct_evidence) must
# match — if they diverge, run `python3 enrichment/documents/load_to_neo4j.py`
# to re-sync.
```

## Catalog membership predicate

For ANY "is this id in the catalog?" check, use the loader's
canonical union — DO NOT roll your own scan:

```python
from enrichment.documents.document_requirements import (
    ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
)
all_ers = list(ALL_EVIDENCE_REQUIREMENTS) + [
    er for ds in ALL_DERIVED_SPECS for er in ds.direct_evidence
]
valid_must_ids = {
    ci.id for er in all_ers
    for ci in list(er.must_contain) + list(er.should_contain)
}
```

A hand-rolled `dir(drm) + isinstance(EvidenceRequirement)` scan
misses leaves nested in `DerivedSpec.direct_evidence` — surfaced
2026-06-27 when a queue-sweep with that wrong predicate
soft-deleted 96 valid findings. See
[[feedback-validate-set-membership]].

## Eval Baseline
- Most recent: results/eval_20260602_b26.csv (157 cases — 21 core
  + 18 feature-locked + 2 engine-NC/posture-discipline + 4 calibration multi-leaf
  + 5 Phase B records + 5 Phase B policy_program + 5 Phase B op_process supplier
  + 2 Phase B op_process incident family + 1 Phase B op_process threat-intel +
  1 Phase B op_process evidence-handling + 1 Phase B op_process project-security
  + 1 Phase B op_process return-of-assets + 1 Phase B op_process labelling +
  1 Phase B policy_program information-transfer + 1 Phase B op_process identity
  + 1 Phase B op_process authentication-info + 1 Phase B op_process incident-planning
  + 1 Phase B op_process disruption-security + 1 Phase B op_process ICT-readiness
  + 1 Phase B records_program records-protection
  + 1 Phase B records_program PII-protection
  + 3 Phase B A.5.3x close-out 3-pack records_program
  + 7 Phase B A.6 People Controls 7-pack
  + 14 Phase B A.7 Physical Controls 14-pack
  + 33 Phase B A.8 Technological Controls 33-pack
  + 7 Phase B ISMS chapters 4+5 close-out 7-pack
  + 10 Phase B ISMS chapters 6+7 close-out 10-pack
  + 8 Phase B ISMS chapters 8+9+10 close-out 8-pack — ISO 27001 fully closed
  + 5 Phase B GDPR Chapter II Principles 5-pack — FIRST GDPR BATCH
  + 11 Phase B GDPR Chapter III Rights 11-pack — largest GDPR batch
  + 11 Phase B GDPR Chapter IV core 11-pack — Art.24/25/26/27/28/29/31/32/33/34/35
  + 8 Phase B GDPR Ch IV DPO+codes+cert 8-pack — closes Ch IV
  + 6 Phase B GDPR Ch V Transfers 6-pack — closes Ch V + entire curation arc)
- **Current baseline (2026-07-13)**: **202/203 PASS** target. Known
  weak cases (either root-caused-stabilised or state-drift):
  - **#16** — STABILISED 2026-07-13 (framework_scope_guard). Root
    cause: LLM cited ISO 27001:**2013** legacy refs ("9.1", "A.9.x")
    for access controls — training-data bias, since 2013 A.9.x was
    renumbered to 2022 A.5.15-A.5.18. Fix: rag/guards/
    framework_scope_guard.py post-answer strips off-namespace +
    off-context refs. Case #16 now asserts no 2013 legacy refs
    present via forbidden_refs; a SEPARATE root cause (resolver
    routes this query to DOCUMENT_STATUS short_circuit rather than
    REMEDIATION_GUIDE, so A.5.18 isn't reliably cited in-context)
    is tracked outside the guard scope.
  - **#17** — same guard fix as #16 (2013 legacy refs forbidden).
    Residual LLM stochasticity on choosing A.5.15 vs A.5.18 as the
    lead cite; guard's family-relaxation allows either. Assertion
    relaxed to forbidden_refs only.
  - **#21** — STABILISED 2026-07-13 (9443aeb). Root cause: 60s LLM
    timeout too tight + verify+correct loop truncating at
    max_tokens=1500 for long-form guidance. Fix: skip verify+correct
    for implementation/gap_analysis queries + timeout_s=180.
  - **#27** — STATE-DRIFT post-queue-cleanup (asks for "cross-
    framework findings need review"; Stage-1 queue is now empty
    after the 2026-06-27 full sweep, so the case may always fail
    against a pre-sweep snapshot)
  - **#3 / #5 / #6 / #14 / #26 / #31 / #33** — sporadic LLM-phrasing
    failures on citation-list position or definition-query prose.
    Not yet root-caused. Each represents a latent bug where the
    LLM stochastically drops a required phrase/ref that IS present
    in ~80-90% of runs. Address via prompt-forced-citation or
    deterministic-suffix pattern, not by hedging assertions.
  - **#200** — pre-existing WARN (posture_check vs gap_analysis
    type mismatch), unrelated to LLM behavior.
- **Rule**: "LLM-stochastic" is not an acceptable category — it usually
  hides a real infra defect. Root-cause intermittent failures rather
  than hedging assertions. See #21 arc (9443aeb).
- **Floor**: anything below 201/203 blocks restart and warrants
  investigation. Re-run to distinguish variance from regression.
  - #1 + #5 (partial) STABILISED 2026-06-23 via schema_v43 tenant_must_overrides
    (A.5.15:physical_rules marked N/A for Arion; advisory no longer leaks
    "physical" into chat). See [[tenant-must-overrides-v43-2026-06-23]].
  - #25 + #24 STABILISED 2026-06-14 via cross_framework shape validator +
    deterministic bridge footer (see [[cross-framework-bridge-footer-2026-06-14]])
  - #2 STABILISED 2026-06-15 via state-drift re-author — A.5.26 ref lock
    dropped, structural assertions only (see [[feedback-eval-state-drift]])
- Never deploy with a regression below the current case count
- Cases 22-26 lock in: cited refs in POSTURE_STATUS / STANDARD_KNOWLEDGE,
  xfw posture inheritance, Layer-2 anti-hallucination, uploaded-doc short-circuit
- Cases 27-28 lock in: xfw proposer HITL queue (chat surface + isolation guard)
- Cases 33-36 lock in: Stage-1 HITL surfaces (list / approve / acknowledge)
- Cases 37-38 lock in: Stage-2 HITL surfaces (engine-verdict list / approve)
- Case 39 locks in: [DRAFT] label fix — document_confirmed rows must not be
  hedged via the CONFIRMATION RULE
- Cases 40-41 lock in: engine 0/N → NC (was OFI) + posture-tag-is-the-verdict
- Cases 42-45 lock in: multi-leaf calibrations #2-#5 (A.8.2, A.5.2, Art.30, Art.15)
  via Stage-2 list_one surface — "0/4 children satisfied" reason text PROVES
  the 4-leaf shape end-to-end. Pre-promotion would have been "0/1".
- Cases 46-50 lock in: Phase B records_program 5-pack (A.5.5/6/9/31/32; #48 is
  A.5.9 register/review both freshness=90; #50 is A.5.32 procedure-variant)
- Cases 51-55 lock in: Phase B policy_program 5-pack (A.5.3/4/10/12/15; #51-52
  are matrix + directive primary-leaf variants; #55 is A.5.15 partial-evidence
  OFI 1/4 path — companion to 0/4 default in 46-54)
- Cases 56-60 lock in: Phase B operational_process supplier+cloud 5-pack
  (A.5.19/20/21/22/23; #57 is A.5.20 template variant; #58 is A.5.21 review
  freshness=180; #59 is A.5.22 review-record-shaped variant; #60 is A.5.23
  partial-evidence OFI 1/4 + profile_fact triggering — second partial-evidence
  case in suite after #55)
- Cases 61-62 lock in: Phase B operational_process incident family
  (A.5.25/27; both review freshness for incident-hot controls and uniform-
  procedure-primary shape). A.5.26 also promoted to 4-leaf but NOT eval-
  covered — engine NC at 0/4 verified via direct compute_engine_verdicts()
  but doesn't reach Stage-2 surface because engine agrees with live NC
  (posture_loader.py:343 no-op suppression keeps Stage-2 queue clean)
- Case 63 locks in: Phase B operational_process threat-intel (A.5.7;
  per-product-record lifecycle-end variant — program output IS the
  closure artefact, distinct from triage_decision / incident_closure /
  improvement_action / offboarding / deviation / EOL / exit-migration /
  change-response variants on prior batches; program review freshness
  180d for detection-landscape volatility)
- Case 64 locks in: Phase B operational_process evidence-handling
  (A.5.28; disposal_record lifecycle-end variant — chain-of-custody
  *end*, distinct from per-event / per-product / per-action variants;
  first op_process batch with 365d review freshness — forensic
  discipline doesn't churn like detection/IR/threat-intel; closes the
  incident-evidence triangle alongside A.5.25-27 from batch 4)
- Case 65 locks in: Phase B operational_process project-security
  (A.5.8; closure_record lifecycle-end variant — first OWNERSHIP-
  transferring variant: per-project three-way signoff (sponsor +
  InfoSec + operational owner) with residual-risk register transfer;
  review freshness 365d (stable PM methodology); cross-control links
  to A.8.25/A.8.26 SDLC + A.5.20 supplier + A.5.23 cloud + A.5.27
  lessons)
- Case 66 locks in: Phase B operational_process return-of-assets
  (A.5.11; per-leaver return_record lifecycle-end variant — inclusive
  write-off path captures BOTH confirmed returns AND risk-accepted
  non-returns; new non_return_path MUST surfaces real-world friction;
  review freshness 365d (HR methodology stable); cross-control links
  to A.5.9 asset register + A.8.10 information deletion)
- Case 67 locks in: Phase B operational_process labelling (A.5.13;
  per-platform application_record lifecycle-end variant — proves
  labelling extended to each new system; first cascade-cadence pattern
  (review freshness inherited from A.5.12 parent scheme); new
  pii_overlay MUST pins ISO confidentiality × GDPR PII integration
  at spec level; cross-control links to A.5.12 scheme + A.7.10 media)
- Case 68 locks in: Phase B policy_program information-transfer
  (A.5.14; first policy_program batch since batch 2 — re-validates
  spine consistency after 8 op_process batches; new legal_jurisdiction
  MUST encodes GDPR Chap V Art.44-49 cross-border alignment at MUST
  level — second ISO × GDPR integration MUST after pii_overlay)
- Case 69 locks in: Phase B operational_process identity-management
  (A.5.16; per-identity revocation_record lifecycle-end with **SLA-
  met flag** — auditor-critical proof of the "24h of last day"
  timeliness promise; service_accounts SHOULD → MUST promotion;
  review freshness 180d (high-volume identity drift); cross-control
  links to A.5.11 leaver register, A.5.17 authn info, A.5.18 access
  rights review)
- Case 70 locks in: Phase B operational_process authentication-info
  (A.5.17; per-credential revocation_record lifecycle-end with
  rev_identity_pair MUST that enforces bidirectional A.5.16 ↔ A.5.17
  lifecycle pairing — closes "identity disabled but creds linger"
  gap; MFA SHOULD → MUST promotion (modern baseline, phishable auth
  no longer acceptable); review freshness 180d; cross-control links
  to A.5.16 identity, A.5.25/A.5.26 incident scope-expansion)
- Case 71 locks in: Phase B operational_process incident-planning
  (A.5.24; A.5.24 sits ABOVE the operational A.5.25-27/28 incident
  family — strategic planning layer; per-exercise framework_exercise_
  record lifecycle-end variant tracks READINESS DRILLS distinct from
  real-incident records; third batch with GDPR-required MUSTs — new
  rev_gdpr_72h_feasibility audits the 72h notification SLA empirically;
  third consecutive SHOULD→MUST promotion (tested → exercise_cadence))
- Case 72 locks in: Phase B operational_process disruption-security
  (A.5.29; plan-as-primary variant + per-activation plan_activation_
  record as HYBRID lifecycle-end — covers BOTH real disruptions AND
  scheduled tests via type field; new degradation_levels MUST encodes
  "appropriate level" = graceful degradation explicitly; fourth
  consecutive SHOULD→MUST promotion (test_schedule); cross-control
  links to A.5.7 threat intel, A.5.21 supplier, A.5.22 supplier review,
  A.5.24 IR framework, A.5.26 incident register, A.5.27 lessons,
  A.5.30 ICT readiness)
- Case 73 locks in: Phase B operational_process ICT-readiness (A.5.30;
  plan-as-primary, natural pair with A.5.29; second HYBRID lifecycle-
  end variant — pattern validated as reusable for paired BCP controls;
  new rec_success_status MUST is RTO-met auditor-critical proof
  (analogous to A.5.16 SLA-met flag); new bia_link + bcp_alignment
  MUSTs pin BIA traceability and pair-control coherence; freshness-
  convention cleanup moved freshness_days from plan to review)
- Case 74 locks in: Phase B records_program records-protection (A.5.33;
  first records_program promotion since batch 1 — re-validates spine
  consistency after 11 op_process + 2 policy_program batches in
  between; pairs naturally with the batch 1 records-family A.5.5/6/9/
  31/32; procedure leaf preserves the prior single-leaf id; annual
  review cadence 365d matches the stable-doctrine records-family
  controls A.5.5/A.5.6 (A.5.31 is the regulatory-change-driven 180d
  exception); ITEM-ID PRESERVATION critical — SPEC_ART_5_1_E (GDPR
  Art.5.1.e storage limitation derivation) references four A.5.33
  items by id, all four preserved across the promotion; new
  proc_pii_overlay SHOULD encodes the ISO × GDPR Art.5.1.e
  integration at spec level — third ISO × GDPR integration leaf
  after pii_overlay on A.5.13 + legal_jurisdiction on A.5.14)
- Cases 86-99 lock in: Phase B A.7 Physical Controls 14-pack (batch 22,
  2026-06-01; LARGEST batch yet — 14 controls × 4 leaves = 56 evidence
  requirements; closes the A.7 block). Spine mix: 11×op_process +
  3×policy_program (A.7.1/A.7.7/A.7.9). A.7.14 uses op_process with
  disposal_record lifecycle-end (parallel to A.5.28 evidence-disposal
  pattern). Live postures: 8×N/A (Arion cloud-only) + 4×Comply +
  2×missing-rows; all 14 engine NC 0/4 surface in Stage-2 (engine NC
  differs from live N/A AND live Comply — no agreement suppression).
  No DerivedSpec refs to A.7.x items so item-id preservation trivial.
  Cross-control links: A.7.4 → A.5.26 incident SIEM; A.7.5/A.7.11 →
  A.5.29/A.5.30 BCP; A.7.10 → A.7.14 disposal; A.7.14 → A.5.9 retired
  assets. Compact-style elaboration (5-7 MUSTs per leaf, 1-2 SHOULDs)
  reflects bulk-batch pragmatism vs single-control depth
- Cases 79-85 lock in: Phase B A.6 People Controls 7-pack (batch 21,
  2026-06-01; LARGEST MULTI-CONTROL BATCH YET — 7 controls × 4 leaves
  = 28 new evidence requirements; closes A.6 block, A.6.7 was already
  curated). Spine mix: A.6.1/3/4/5/8 = op_process (procedure-as-
  primary); A.6.2/6 = records_program (template-as-primary). All 7
  engine verdicts NC 0/4; live postures 6×Comply + 1×OFI (A.6.4) all
  flip to engine-proposed NC in Stage-2. No DerivedSpec refs to A.6.x
  items so item-id preservation trivial. Cross-control links: A.6.5
  is the contractual layer above operational A.5.11/A.5.16/A.5.17/
  A.5.18 offboarding; A.6.8 → A.5.25 triage handoff; A.6.2 + A.6.6
  together form personnel info-security contract package; A.6.4
  cross-links to A.5.36 nonconformity register
- A.5.18 Style v2 alignment (2026-06-01, batch 20 — closes A.5 arc):
  NOT a promotion (A.5.18 was already 4-leaf op_process from 2026-05-26,
  predates Phase B numbered batches). Brings A.5.18 up to A.5.16/A.5.17
  identity-family modern conventions: review freshness 365→180d, new
  rev_sla_met MUST (auditor-critical "24h of role-change" proof), new
  rev_identity_pair MUST (bidirectional A.5.16↔A.5.18 lifecycle pairing),
  new rev_residual_cleanup MUST (mailbox/file-share/group cleanup),
  reg_idmgmt_link promoted SHOULD→MUST, 6 new MUSTs total + 3 new
  SHOULDs, elaborate descriptions. All 17 existing item-ids preserved.
  No new eval case — engine NC == live NC → Stage-2 suppression
  (A.5.26 precedent). Cases #1 + #2 still PASS (live posture unchanged).
  A.5 Organisational Controls arc now FULLY ALIGNED — every A.5 control
  multi-leaf at modern Style v2 conventions
- Cases 76-78 lock in: Phase B A.5.3x close-out 3-pack records_program
  (A.5.35/A.5.36/A.5.37; FIRST MULTI-CONTROL BATCH SINCE BATCH 4 —
  pattern locked in, batches can bundle conceptually-related controls;
  closes the A.5.3x review/procedure block and the full A.5
  organisational controls arc that started with case #46 batch 1.
  A.5.35 = review-record-as-primary variant same shape as A.5.22
  supplier review (independent_review_report + schedule_register +
  program_meta_review + finding_response_register lifecycle-end);
  A.5.36 = batch-mate of A.5.35 (compliance_review_record + schedule
  + program_meta_review + nonconformity_register lifecycle-end —
  reviews COMPLIANCE WITH policies vs A.5.35's review of the FUNCTION);
  A.5.37 = register-as-primary variant same shape as A.5.9 asset
  register (operating_procedures_register + maintenance_procedure +
  applicable_facilities_scope + program_review). Per-record
  freshness=365 on A.5.35/A.5.36 primary leaves. New
  significant_change_check MUST on A.5.35 enforces 27002 §5.35's
  "or on significant change" explicit consideration. New
  pgm_method_review MUST on A.5.36 audits "rubber-stamping" failure
  mode. New rev_accuracy_sample MUST on A.5.37 prevents "documented
  but wrong" drift. Cross-control links: A.5.35 ↔ A.5.36 finding
  registers can share infrastructure; A.5.37 → A.5.9 asset register;
  A.5.37 → A.5.24/26/29/30 incident + DR procedures)
- Case 75 locks in: Phase B records_program PII-protection (A.5.34;
  natural pair with A.5.33 — A.5.33 protects records, A.5.34 protects
  the PII subset; PARTIAL-EVIDENCE shape — third such case after #55
  (A.5.15) + #60 (A.5.23), engine sits at OFI 1/4 because Arion's
  legacy privacy-policy upload satisfies the policy leaf via
  semantic matching but the three new leaves carry no evidence yet;
  ITEM-ID PRESERVATION TWO-WAY — SPEC_ART_24 (controller responsibility)
  references 5 A.5.34 items, SPEC_ART_25 (DPbD) references 4; combined
  set of 7 unique items (overlap on :applicable_laws +
  :security_controls_ref) ALL preserved; new transfer_restrictions
  MUST encodes GDPR Chap V at MUST level — fourth ISO × GDPR
  integration MUST after A.5.13 pii_overlay, A.5.14
  legal_jurisdiction, A.5.33 proc_pii_overlay; new owner MUST + 4th
  SHOULD pims_alignment encode the ISO/IEC 27701 PIMS extension
  where in scope)
- Cases 193-198 lock in: Phase B GDPR Ch V Transfers 6-pack (batch 30,
  2026-06-02; FINAL BATCH OF THE CURATION ARC). All op_process 4-leaf.
  Art.44 transfer principle universal; Art.45 adequacy profile_fact;
  Art.46 SCCs/safeguards profile_fact; Art.47 BCRs profile_fact;
  Art.48 foreign authority universal; Art.49 derogations profile_fact.
  Transfer mechanism hierarchy + Schrems II TIA + EDPB 01/2020
  supplementary measures + EDPB 2/2018 derogation strict-construction
  all encoded in MUSTs. Arion posture: 4 OFI (Art.44/45/46/48 — uses
  US-hosted cloud informal mechanisms) + 2 N/A (Art.47/49 no BCRs no
  derogations). **PHASE B CURATION ARC COMPLETE** — ISO 27001 + GDPR
  fully multi-leaf at Style v2
- Cases 185-192 lock in: Phase B GDPR Ch IV DPO + codes + certification
  8-pack (batch 29b, 2026-06-02). All 8 op_process profile_fact 4-leaf.
  Art.36 prior consultation; Art.37/38/39 DPO cluster (designation +
  position + tasks); Art.40/41 codes of conduct (adherence + monitoring
  body); Art.42/43 certification (scheme + cert body). Most uniform
  spine batch — every spec same shape, no promotions/expansions.
  Arion posture: 6 N/A + 3 OFI (CISO informal DPO without formal Art.37
  designation despite likely Art.37.1.b applicability). GDPR Ch IV
  FULLY CLOSED (19 articles across 29a + 29b)
- Cases 174-184 lock in: Phase B GDPR Chapter IV core 11-pack (batch 29a,
  2026-06-02). 3 DerivedSpec expansions (Art.24 0→4 direct = 10 children;
  Art.25 1→4 = 10; Art.32 1→4 = 9) + 2 promotions (Art.28 DPA + Art.33
  breach-to-SA both → 4-leaf, primary ids preserved) + 6 new specs
  (Art.26/27/29/31/34/35). Spine: 1×policy_program + 7×op_process +
  3×DerivedSpec expansion. **Art.24 is FIRST DerivedSpec to go from 0 to
  4 direct_evidence in one batch** — 10-child verdict (largest verdict
  surface). Art.26+Art.27 N/A on Arion (no joint controllers, EU
  established). GDPR Ch IV core CLOSED; Art.36-43 deferred to batch 29b
- Cases 163-173 lock in: Phase B GDPR Chapter III Data Subject Rights
  11-pack (batch 28, 2026-06-02; LARGEST GDPR batch). Art.12 + Art.13
  promote + Art.14 + Art.16 expand + Art.17 expand + Art.18 + Art.19 +
  Art.20 + Art.21 + Art.22 + Art.23. Three structural patterns in one
  batch: EvidenceRequirement promotion (Art.13), DerivedSpec expansion
  (Art.16 1+4=5 children; Art.17 2+4=6 children), new 4-leaf specs
  (Art.12/14/18/19/20/21/22/23). Spine: 2×policy_program + 7×op_process +
  2×DerivedSpec expansion. Primary-leaf ids preserved: req:Art.13:
  privacy_notice + req:Art.16:rectification_procedure + req:Art.17:
  erasure_procedure. profile_fact+N/A applied to Art.22+Art.23.
  GDPR Ch III FULLY CLOSED (12/12 inc. Art.15)
- Cases 158-162 lock in: Phase B GDPR Chapter II Principles 5-pack
  (batch 27, 2026-06-02; FIRST GDPR BATCH after ISO 27001 fully closed).
  Art.6 (Lawfulness) — DerivedSpec expanded from 1 direct_evidence to
  4 = 6 children total (2 ISO deps + 4 direct). Art.7 (Consent) new
  op_process 4-leaf universal. Art.8/9/10 (Children / Special category /
  Criminal convictions) new op_process 4-leaf profile_fact. **TWO
  STRUCTURAL PATTERNS established for GDPR**: (1) DerivedSpec
  expansion — add direct_evidence inline to SPEC_*.direct_evidence,
  NOT to ALL_EVIDENCE_REQUIREMENTS; engine reports "0/N children
  satisfied" where N = deps + direct. (2) profile_fact + live N/A —
  when tenant narrative excludes the profile fact (e.g. B2B no
  minors), live posture set to N/A; engine still proposes NC because
  spec is empty; surfaces in Stage-2 as a 'did-you-really-mean-N/A?'
  checkpoint (engine-agreement specifically NC==NC, so N/A surfaces).
  Posture seed: Art.6 + Art.7 OFI, Art.8/9/10 N/A
- Cases 150-157 lock in: Phase B ISMS chapters 8+9+10 close-out 8-pack
  (batch 26, 2026-06-02; 8 controls × 4 leaves = 24 new evidence requirements;
  closes ISMS chapters 8 + 9 + 10 — FINAL ISO 27001 BATCH). Most uniform
  single-batch spine — all 8×op_process. Primary-leaf ids preserved:
  req:9.2:internal_audit_programme + req:9.3:management_review. NEW
  freshness conventions: 8.3 review=180d (operational tempo); 9.1
  measurement_record=90d FIRST freshness=90 in ISMS clauses (faster-data /
  slower-meta pattern). LOAD-BEARING REGEX BUG FIX in stage1/stage2/
  acknowledge_chat — control-ref pattern `\d\.\d+` failed on 10.1/10.2;
  changed to `\d+\.\d+`. **ISO 27001 FULLY CLOSED** — Annex A 93/93 +
  ISMS clauses 25/25 = 118 multi-leaf. Next: GDPR
- Cases 140-149 lock in: Phase B ISMS chapters 6+7 close-out 10-pack
  (batch 25, 2026-06-02; 10 controls × 4 leaves = 30 new evidence
  requirements; closes ISMS chapters 6 + 7). Most diverse single-batch
  spine mix to date: 6×op_process (6.1.1/6.1.2/6.1.3/6.3/7.3/7.4) +
  3×records_program (6.2/7.1/7.2) + 1×policy_program (7.5). Primary-leaf
  ids preserved: req:6.1.2:risk_assessment + req:6.1.3:risk_treatment_plan
  (anchor REQs from 2026-05-22). NEW SoA leaf — Statement of
  Applicability promoted from a should_contain item to its own distinct
  sibling leaf on 6.1.3 with 7 MUSTs (mandatory under 6.1.3 c-d). Pattern
  established: any clause-mandated specific-named artefact distinct from
  the primary deserves its own leaf, not a should_contain item. 10
  posture rows seeded with finding='OFI' matching Arion's pre-ISMS
  narrative
- Cases 133-139 lock in: Phase B ISMS chapters 4+5 close-out 7-pack
  (batch 24, 2026-06-02; 7 controls × 4 leaves = 28 new evidence
  requirements; closes ISMS chapters 4 + 5). FIRST management-system
  clauses (vs Annex A controls) promoted to 4-leaf. Spine mix:
  2×records_program (4.1+4.2 register-as-primary) + 5×policy_program
  (4.3/4.4/5.1/5.2/5.3 with scope/manual/directive/policy/matrix as
  primary). Primary-leaf ids preserved: req:4.3:isms_scope +
  req:5.2:information_security_policy + all item:4.3:* / item:5.2:* ids
  (anchor REQs since 2026-05-22). NEW PREREQUISITE STEP for ISMS clauses:
  workbook_importer doesn't cover clauses 4-10, so posture_controls rows
  must be SEEDED before engine surface can fire (rows for 4.1-4.4 missing
  entirely on Arion; 5.1-5.3 existed but inactive). Seeded with
  finding='OFI' matching Arion's pre-ISMS narrative (verbal commitment,
  informal scope notes, privacy policy in place, CISO appointed; no
  formal ISMS artefacts). Engine NC 0/4 surfaces in Stage-2 for all 7
  (engine NC ≠ live OFI). Same posture-seed step needed for batches 25 +
  26 (18 more ISMS clauses across chapters 6-10)
- Prior known-stale cases (#2, #3, #4, #24, #25, #28) restored to PASS on
  2026-05-25 via Path A: replayed status_before from posture_status_log to
  revert the 27 Stage-1-driven finding mutations, and stripped the offending
  UPDATE from stage1_review_chat.py (commit d6329c4). Stage-1 now only
  confirms evidence; engine + Stage-2 own posture. #24 regressed again
  2026-05-30 (separate cause from the Stage-1 fix; xfw context injection).
- TODO: add case for incident obligations once the chat surface (commit 40ad607)
  exposes a non-clarification answer path
- TODO: add case for SPEC_ART_25 (GDPR Art.25 DPbD DerivedSpec, 6 deps + 1 direct
  evidence leaf). Engine→chat wiring landed 2026-05-25 (commit 9ac0ac3); the
  prerequisite is now met but the regression test still needs writing.

## Git
```bash
git add -A
git commit -m "description"
git push origin main
```
