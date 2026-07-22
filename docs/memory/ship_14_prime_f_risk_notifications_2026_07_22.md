---
name: ship-14-prime-f-risk-notifications-2026-07-22
description: "Ship 14'.f — 4 risk-register notification kinds + sweep producer wired to the scheduler; write-path producer helper exposed"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 14'.f (2026-07-22) — sixth sub-arc of Ship 14. Ships the
notification producers deferred from 14'.e. Framing decision:
risk-register lifecycle events are TERMINAL — they don't cascade
to other controls the way `incident_declared` does — so they
land as pure notification producers, NOT as new cascade
taxonomy edges + implication rows.

## What ships

### 1. schema_v88 — allowlist extensions

- `tenant_notification_kind_check` grows from 13 → 17 kinds:
  `risk_added`, `risk_treatment_overdue`,
  `residual_above_threshold`, `risk_review_due` added
- `sweep_log_work_type_check` grows from 9 → 10 kinds:
  `risk_register_notify` added
- New RLS policy `app_risk_all` on `risks` — mirrors
  `app_posture_all` on `posture_controls`. Lets the
  `arioncomply_app` role scan across tenants in one query while
  keeping the default `tenant_isolation` policy for every other
  role.

### 2. `rag/risk/notify.py` — 2 entry points

**`emit_risk_added(pg_conn, tenant_id, external_ref, threat)`**
— write-path producer. Called on INSERT into `risks`. Fires
severity `low` — heads-up, not alarm. Dedup: title text match
within 7 days.

**`sweep_risk_register_notify(pg_conn, tick_id, dry_run)`** —
periodic scan wired to the `risk_register_notify` work_type.
Handles the 3 time-triggered kinds:

- **`risk_treatment_overdue`** — `implementation_date <
  CURRENT_DATE` AND `treatment_status <> 'implemented'`.
  Severity ladder: >90d critical, >30d high, else medium.
- **`residual_above_threshold`** — `residual_risk_level >= 15`
  (top quintile of 1-25 scale). Severity: `≥20 critical`,
  else `high`.
- **`risk_review_due`** — `review_date < CURRENT_DATE + 30d`.
  Severity ladder: past due high, <7d medium, else low.

Dedup: partial unique index on `(tenant_id, kind,
related_entity_id, related_control_ref) WHERE read_at IS NULL
AND dismissed_at IS NULL` — the DB enforces one active
notification per (tenant, kind, risk). Sweep also filters within
`_RISK_DEDUP_DAYS = 7` before insert to preserve read history.

Each notification body cites the specific ISO 27005:2022 §:
- Treatment overdue → §9.2 (operation)
- Residual above threshold → §8.6.3 (residual acceptance)
- Review due → §10 (leveraging related ISMS processes)

### 3. Scheduler wiring (`rag/scheduler/tick.py`)

`sweep_risk_register_notify` imported at module load + added to
`_WORK_TYPES`. The systemd timer (Ship 3'.a) picks it up
automatically at the next 30-min tick.

## Verification (end-to-end smoke test)

Flipped demo tenant risk `R001` to `treatment_status='in_progress'`
+ `residual_risk_level=20` + `review_date=CURRENT_DATE-5d`. Ran
the sweep manually:

```
{"work_type": "risk_register_notify", "scanned": 1, "acted_on": 3,
 "errored": 0, "detail": {"per_tenant": {"00000000":
   {"overdue": 1, "above_threshold": 1, "review_due": 1,
    "deduped": 0}}}}
```

3 notifications inserted with correct severity:
- `risk_treatment_overdue` critical (impl_date >90 days ago)
- `residual_above_threshold` critical (residual 20/25)
- `risk_review_due` high (past due)

Ran again immediately → all 3 deduped:
```
{"acted_on": 0, "deduped": 3}
```

Dedup verified. Demo state restored (row flipped back +
notifications deleted).

## Ship 14'.a addendum — reviewer discipline answers

**1. Role split?**

N/A — notifications reference the risk row (via
`related_entity_id`), not a specific control. When a tenant
opens a notification's "Open risk" deep-link, the drill-in
detail page (Ship 14'.d) renders linked_controls side-by-side
per role — that's where the role model is respected.

**2. Parallel CaseFile view?**

N/A — notifications are their own surface, orthogonal to chat.
No CaseFile touched.

**3. Deterministic routing?**

Yes — sweep uses deterministic SQL predicates
(`implementation_date < CURRENT_DATE`, `residual_risk_level >=
15`, `review_date < CURRENT_DATE + 30d`). No LLM inference of
"which risks matter" — the tenant's own data determines it.

**4. Guidance-normative discipline?**

Preserved — notifications reference risk rows the tenant
authored, not guidance-derived obligations. Bodies CITE
27005:2022 § pointers as authority for the recommended action,
but don't add new MUSTs.

## What did NOT ship

- **Workbook-importer wire-up for `emit_risk_added`** —
  `_write_rows` in `db/workbook_importer.py` needs to detect
  new INSERTs (vs UPSERT updates) and call `emit_risk_added()`.
  Adding INSERT-detection is invasive; deferred to a follow-up
  once a POST /risks endpoint arrives (which naturally has
  INSERT-only semantics).
- **UI badge on the notifications inbox for risk kinds** — the
  existing inbox already renders arbitrary notification kinds;
  the 4 new kinds surface automatically. Any custom rendering
  (e.g. one-click "Open R-042" deep-link buttons) is a follow-up
  in Ship 14'.g or later.
- **Cascade taxonomy edges + meditation patterns** — risk
  events are terminal (see framing note above); no cascade
  propagation needed. If a future arc wires risk events to
  trigger IMPLIES/BLOCKS on their linked controls, that'd
  become its own arc.

## Impact on baseline

Eval confirmed: **228/229 PASS + 1 WARN + 0 FAIL** — baseline
unchanged. Zero regressions from the new schema constraints,
notify module, sweep function, or RLS policy.

## Ship 14 progress

| Sub-arc | Status |
|---|---|
| 14'.a Design + role-model + case-file addendum | ✓ |
| 14'.b schema_v87 + xlsx template + upload path | ✓ |
| 14'.c API surface (internal + external) | ✓ |
| 14'.d Dashboard cards + heatmap + drill-in | ✓ |
| 14'.e Chat surfaces + case-file discipline + nav badge | ✓ |
| **14'.f Notification producers (sweep + write-path)** | **✓ (this doc)** |
| 14'.g Eval + arc retrospective | next |

## Related

- [[ship-14-prime-a-risk-register-design-2026-07-22]] — design
  memo (mentioned cascade events in the original scope; this
  sub-arc reframes them as pure notifications since risks are
  terminal nodes)
- Ship 3'.a scheduler productionization — the systemd timer
  that fires the sweep every 30 min
- Ship 3'.b/'.c/'.e/'.f/'.g notification producers — the
  discipline this arc mirrors (dedup window, severity ladder,
  per-tenant iteration, silent-fail)
- Ship 14'.g: eval cases + arc retrospective
