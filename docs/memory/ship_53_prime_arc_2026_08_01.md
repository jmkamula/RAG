---
name: ship-53-prime-arc-2026-08-01
description: "Ship 53' consultant-grade grounding arc — 6 sub-arcs 2026-08-01. gpt-4.1 chat_answer + gpt-4.1-mini small purposes; ISO 27701 Chroma indexing gap closed (49 nodes); 27701 marker corrected (self-contained model); EDPB Guidelines corpus grounding (1190 chunks across 9 docs) with per-ref semantic-query digest section. Verified across 7 GDPR remediation surfaces. Full retro at docs/memory/ship_53_prime_arc_retrospective_2026_08_01.md."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 53' delivered consultant-grade grounding in one contiguous
2026-08-01 session. Six sub-arcs across three grounding surfaces
plus a model migration that surfaced a latent data gap.

**Commits** (chronological):
- `cdc708e` — ISO 27002/27003 guidance attribution in digest
- `9d6f500` — LLM model migration (gpt-4.1 + gpt-4.1-mini)
- `c635fbb` — ISO 27701 Chroma indexing gap closed (49 nodes)
- `f3d23d7` — 27701 guidance marker correction (27002 → 27701)
- `ac1cf4c` — EDPB Guidelines corpus grounding (1190 chunks)
- `6e7b222` — Retrospective

**Key architectural takeaways**:

- `_infer_guidance_standard(ref, standard_id)` in
  `rag/casefile/digest.py` maps ref→guidance-authority. Correct
  mappings: ISO 27001 A.5-A.8 → ISO 27002:2022; ISO 27001 ISMS
  body → ISO 27003:2017; ISO 27701 → ISO 27701:2019 (self-contained).
- Chat model config lives in `rag/llm_models.py` — `MODEL_CHAT_ANSWER
  = "gpt-4.1"`. Anthropic sites (EXTRACTOR = sonnet-4-6,
  ENRICHER = haiku-4-5) untouched.
- New Chroma collection `edpb_guidelines` (1190 chunks) + merged
  into `arioncombly_all` (1668 docs).
- New `_render_edpb_guidance()` digest section fires per cited GDPR
  ref; uses `VectorIndexer.get_collection()` (never raw HttpClient
  — dimension mismatch).
- Adding a new grounding corpus (ISO 27018, ISO 29134, ICO guides,
  CJEU): mirror `scripts/index_edpb_to_chroma.py` shape + add a
  parallel `_render_<corpus>_guidance()`.

**Verified**: 7 GDPR remediation surfaces (Art.35 DPIA, Art.28
Controller-Processor, Art.33 Breach, Art.6 Lawful basis, Art.15
Right of access, Art.25 DPbD, Art.44 Transfers) — every action
card cites the correct EDPB/WP29 source doc.

**Cost impact**: ~$0.012-0.013 per GDPR turn (up from ~$0.010).
Latency ~4-5s wall (up from ~3s). Trivial for the quality shift.

**Deliberately NOT done** (documented for future sessions):
- ISO 27018 for cloud-processor B.8.x grounding
- ISO 29134 for DPIA-adjacent controls
- ISO 29100 / 29151 privacy framework
- National SA guidance (ICO, CNIL, etc.)
- WP29 wp251 automated decisions
- CJEU case law integration
- Bracket-form citation strict enforcement (Art.44 slipped
  into inline form)

See full retrospective at
`docs/memory/ship_53_prime_arc_retrospective_2026_08_01.md`
for the 8 codified lessons + consulting-grounding scaffold.
