---
name: ship-20-prime-c-family-b-2026-07-23
description: "Ship 20'.c — Family B intro + 1 related card wired to 3 single-ref short-circuits; new fetch_control_metadata + build_short_circuit_structured helpers"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 20'.c — second delivery sub-arc of Ship 20. 3 single-ref
short-circuit sites now emit intro + 1 related card
populated deterministically from CaseFileShim + Neo4j metadata +
advisory per-leaf data. Commit `db9554f`.

## New helpers in `rag/casefile/answer_augment.py`

### fetch_control_metadata(refs)
Batch Neo4j query returning `{ref: {title, standard_id}}`. Uses
`RequirementNode.ref` property (initial guess `rn.control_ref`
was wrong — corrected after smoke test showed empty titles).
Fails silently → returns partial or empty dict.

### _reindex_posture_by_ref(posture_by_node_id)
Converts the node_id-keyed posture the graph node holds into
the ref-keyed form CaseFileShim exposes to build_related_cards.
Last ref wins on collision (matches CaseFile.posture_by_ref).

### build_short_circuit_structured(intro_text, primary_ref,
                                   extra_refs, tenant,
                                   posture_by_node_id, tenant_id)
Family B/C builder. Opens its own short-lived pg connection for
advisory data (evidence_summary / still_needed / leaves) when
caller doesn't pass one; mirrors LLM-path augment flow.

## Sites migrated

- **acknowledge_gap** (line 2242) — single ref from
  `_ack_intent.control_ref`. Card carries title, verdict, role,
  DRAFT chip, leaves checklist.
- **cascade_implications** (line 2487) — single ref from
  `_ci_ref` extraction. Falls back to intro-only when no ref.
- **timeline** (line 2514) — single ref from timeline extract.

All 3 sites preserve `attach_templates=False`, `attach_advisory=
False`. `answer_text` unchanged.

## Verified end-to-end

`show me the timeline for A.5.18`:
- Related card populated: title="Access rights",
  standard_display="ISO 27001:2022", role="program",
  verdict="NC", draft=True.
- 4 leaves with per-MUST counts (○ Access Revocation Record 4/8,
  ○ Access Rights Review 5/8, etc.).
- Ship 18/19 primary-card frontend render handles this
  identically to LLM path — no frontend changes needed.

## Ship 20 progress

| Sub-arc | Status |
|---|---|
| 20'.a Design memo | ✓ (9846eb6) |
| 20'.b Family A | ✓ (96031b8) |
| **20'.c Family B (this)** | **✓ (db9554f)** |
| 20'.d Family C | next |
| 20'.e Eval + retro | pending |

## Related

- [[ship-20-prime-a-short-circuit-design-2026-07-23]] — design
- [[ship-20-prime-b-family-a-2026-07-23]] — Family A
- [[ship-19-prime-arc-retrospective-2026-07-23]] — card polish
  that this arc's cards render into
