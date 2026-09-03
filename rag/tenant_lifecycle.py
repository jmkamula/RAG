"""
rag/tenant_lifecycle.py — determine tenant's onboarding lifecycle stage.

Ship 107' (2026-09-03) — architectural gate for producers that shouldn't
fire during onboarding. A fresh Quickstart tenant with a framework
enrolled but no client_facts / no journey_status / no assessments is
not the same as a mature program running for months. Producers should
distinguish.

Three stages:

  setup     — fresh Quickstart tenant. No client_facts row, no
              journey_status declared. Producers stay silent —
              tenant hasn't established scope or begun any work.
              Engine may compute proposals internally for the
              dashboard drill-in, but doesn't push to Stage-2
              queue or fire notifications.

  building  — tenant has declared journey_status OR populated
              client_facts. Producers surface proposals for
              CHANGES to existing assessments only; skip
              Not-assessed defaults (nothing to disagree with
              when tenant hasn't looked yet).

  active    — ≥1 posture_control with a real assessment
              (Comply/OFI/NC) OR ≥1 document upload. Full
              producer behavior.

Public function:
  lifecycle_stage(pg_conn, tenant_id) -> Literal['setup','building','active']

Callable per-tenant during a batch; producers should cache the
result across control-level loops within one run.

The gate is queried from:
  · rag/posture_loader.py — engine proposal writes + notifications
  · rag/scheduler/tick.py — periodic sweeps (skip setup-stage tenants)
  · rag/cascade/notify.py — cascade notification sites (future)
"""
from __future__ import annotations
from typing import Literal

LifecycleStage = Literal["setup", "building", "active"]


def lifecycle_stage(pg_conn, tenant_id: str) -> LifecycleStage:
    """Return the tenant's current onboarding lifecycle stage.

    Three cheap EXISTS queries against indexed columns. Safe to call
    per-tenant during a batch (producers should still cache the
    result across control-level loops within one run for hygiene).
    """
    with pg_conn.cursor() as cur:
        # ── Active — any real assessment or upload ──
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM posture_controls
                 WHERE tenant_id = %s::uuid
                   AND is_active = TRUE
                   AND finding IS NOT NULL
                   AND finding NOT IN ('Not assessed', '')
            )
        """, (tenant_id,))
        if cur.fetchone()[0]:
            return "active"

        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM document_uploads
                 WHERE tenant_id = %s::uuid
            )
        """, (tenant_id,))
        if cur.fetchone()[0]:
            return "active"

        # ── Building — journey_status set OR client_facts row exists ──
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM client_facts
                 WHERE tenant_id = %s::uuid
            )
        """, (tenant_id,))
        if cur.fetchone()[0]:
            return "building"

        # ── Setup — fresh Quickstart, nothing declared ──
        return "setup"
