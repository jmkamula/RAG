---
name: engine-verdict-verification-snippet
description: "Undocumented one-liner to verify engine verdicts end-to-end after spec curation, plus the stderr/result-shape gotchas"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 37fc2b1a-23c8-415f-a22c-97ab3f049706
---

After modifying `enrichment/documents/document_requirements.py` and running
`python3 enrichment/documents/load_to_neo4j.py`, verify engine end-to-end
with `rag.posture.engine_runner.compute_engine_verdicts(pg, neo, TENANT)`.
This is the verification step every GDPR curation commit reports
("Verified end-to-end on tenant arion: ..."). It is not wrapped in a CLI
or script — call it directly.

```python
from rag.posture.engine_runner import compute_engine_verdicts
TENANT = '00000000-0000-0000-0000-000000000001'  # Arion Networks
verdicts = compute_engine_verdicts(pg_conn, neo4j_driver, TENANT)
# returns dict[control_id, ControlVerdict]
# control_id is like 'GDPR:2016/679:Art.5.1.a' (matches RequirementNode.id)
# ControlVerdict fields: posture, curation_status, applies, reason,
#                        derived_from (list of child verdicts), leaves,
#                        our_gaps, tenant_gaps, gap_list
```

Two gotchas that cost me time:

1. **Stderr drowns stdout.** The Neo4j driver emits an UNRECOGNIZED warning
   about a non-existent `applies_when` property on EVERY engine query.
   Suppression is in place for the driver itself (see
   [[applies_when_warning_suppression]]) but `compute_engine_verdicts`
   uses a separate driver path. Redirect: `python3 ... 2>/dev/null`.

2. **Cypher records need `AS alias` for dict access.** `s.run('MATCH (n)
   RETURN n.id')` returns a Record where `r['id']` raises KeyError. Use
   `s.run('MATCH (n) RETURN n.id AS id')` and `r['id']` works.

Verdict-count deltas are the headline number in commit messages (e.g.
"130 verdicts total" → "138 verdicts total" across today's 8 specs).
GDPR-only count via `sum(1 for k in v if k.startswith('GDPR:'))`.

Related: [[posture_engine_alignment_plan_2026_05_22]] for the broader
plan this verification supports.
