---
name: tenant-journey-wizard-2026-06-24
description: "SHIPPED 2026-06-24: tenant journey wizard backend. rag/journey/state.py computes per-tenant phase (Profile / Foundation / Operational / Annual), per-leaf MUST completion %, top-5 next-action recommendations. GET /api/v1/journey/state (full) + GET /api/v1/journey/next (one-shot). Reads-only: templates table + document_findings + tenant_must_overrides + client_facts + Neo4j MUST graph. Arion shipped at Phase 1 Foundation, 1.4% posture, anchor #1 (4.3 ISMS Scope) recommended."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

The templating arc shipped the artefacts (645 templates + render +
download + extractor fast-path + 20 hand-refined anchors). The
wizard wraps the templates into a **guided onboarding journey** so
tenants aren't presented with 645 items at once.

Backed by the 4-phase model agreed earlier:

| Phase | Trigger | Tenant effort | Reward signal |
|---|---|---|---|
| **0 — Profile** | ClientFacts incomplete | 5 min ClientFacts wizard | Scope narrows; non-applicable obligations disappear |
| **1 — Foundation** | Profile complete; any anchor < 100% | 4-6 anchor templates per week | Anchor count up; posture % jumps visibly |
| **2 — Operational** | All 20 anchors complete | Operational templates by family | Per-leaf completion % |
| **3 — Annual** | Everything filled | Freshness-driven reviews | Cadence-based prompts |

## Data sources (all reads-only)

```
templates                     leaves catalogue + must_count + version
document_findings             which MUSTs are satisfied per tenant
tenant_must_overrides         which MUSTs are N/A per tenant
client_facts                  profile completeness signal
Neo4j EvidenceRequirement     authoritative MUST item ids per leaf
```

Per-leaf completion % = satisfied / max(1, total - N/A).
Posture % = sum(satisfied) / sum(total - N/A) across all leaves.

## Phase determination logic

```python
if not profile_complete:        → 'profile'
elif anchors_complete < 20:     → 'foundation'
elif operational_complete < N:  → 'operational'
else:                            → 'annual'
```

Anchor set = the 20 hand-refined v2 templates. Order in
`_ANCHOR_LEAVES` encodes the recommended foundation sequence
(4.3 → 5.2 → 5.3 → 6.1.2 → 6.1.3 RTP → 6.1.3 SoA → 7.5 → 9.2 →
9.3 → 10.1 → A.5.1 → A.5.9 → A.5.15 → A.5.18 → A.5.19 → A.5.24
→ A.5.29 → A.6.3 → Art.30 → Art.32).

## Next-action recommender per phase

| Phase | Ranking |
|---|---|
| profile | empty — recommendation IS the profile itself |
| foundation | anchor leaves in documented order; first 5 incomplete |
| operational | non-anchor + has-template + incomplete; smaller MUSTs first (quick wins) |
| annual | empty in v1 (freshness-driven; defer) |

Each recommendation row carries: control_ref, title, completion %,
why string, template_url + download_url so the client can route the
tenant directly to fill.

## API

`GET /api/v1/journey/state` — full payload (JourneyState dataclass)
`GET /api/v1/journey/next`  — one-shot top recommendation only

Both authenticated via existing X-API-Key + require_api_key.
Tenant-scoped via set_session RLS.

## Smoke on Arion (2026-06-24)

```json
{
  "phase": "foundation",
  "phase_name": "Phase 1 — Foundation",
  "phase_message": "Build the foundation policies + procedures. 1/20 foundation
                    templates complete; 19 to go. Each foundation document
                    unlocks several dependent controls.",
  "profile_complete": true,
  "total_leaves": 645,
  "leaves_complete": 1,
  "posture_pct": 1.4,
  "anchors_total": 20,
  "anchors_complete": 1,
  "operational_total": 625,
  "operational_complete": 0,
  "next_actions": [
    {"control_ref": "4.3",   "title": "ISMS Scope Statement",         "completion_pct": 0.0},
    {"control_ref": "5.2",   "title": "Information Security Policy",  "completion_pct": 0.0},
    {"control_ref": "5.3",   "title": "Roles + Authorities Matrix",   "completion_pct": 0.0},
    {"control_ref": "6.1.2", "title": "Risk Assessment Procedure",    "completion_pct": 0.0},
    {"control_ref": "6.1.3", "title": "Risk Treatment Plan",          "completion_pct": 0.0}
  ]
}
```

## Files shipped

| File | Lines | Role |
|---|---|---|
| `rag/journey/__init__.py` | 1 | Package marker |
| `rag/journey/state.py` | 350 | `compute_journey_state(pg, neo, tenant_id)` |
| `api_server.py` (additions) | 70 | Two GET endpoints |

## What's NOT in v1

- **UI** — wizard is API-only; frontend wraps it (separate workstream)
- **Annual freshness scheduler** — phase 3 returns empty `next_actions`
  in v1; freshness-driven prompts are the natural next step
- **Cascade-value scoring** — operational ordering uses MUST count
  proxy; richer "this template unlocks N other controls" computation
  is a v2 enhancement (would need to walk the Neo4j cross_control_links
  graph + DerivedSpec derives_from chains)
- **Profile wizard endpoint** — `/api/v1/profile/update` (or similar)
  to drive Phase 0 doesn't exist; client must edit client_facts
  directly for now
- **In-app form rendering** — second tenant edit path (form generated
  from template markers) is deferred; download/upload is sufficient for v1

## Related

- [[templates-v1-foundation-2026-06-24]] — the template artefacts the
  wizard recommends
- [[curation-document-templates-idea]] — original idea memory; the
  wizard is the user-facing realisation
- [[feedback-anchor-before-choices]] — pattern used: anchored
  architecture before picking the chunk
