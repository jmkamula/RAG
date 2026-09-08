"""
Ship 129'.d — enrolment-nudge notification producer.

Fires when tenant facts (client_facts) indicate a framework is
applicable but the tenant hasn't enrolled it. Discovery-count
enrichment (findings we've silently discovered for the framework)
lands in the notification body as supporting evidence, NOT as
the trigger.

Design principles (Ship 129' arc):
  - Trigger is JURISDICTION not DISCOVERY. A tenant with 0
    findings but `eu_data_subjects=TRUE` still deserves the nudge;
    a tenant with 500 findings but `eu_data_subjects=FALSE` does
    NOT.
  - Facts must be `declared` or `derived` (Ship 110'.d rule).
    `default` facts don't fire the nudge — conservative-in-doubt.
  - Dedup per (tenant, standard) within _NUDGE_DEDUP_DAYS. Nudges
    are gentle, not spammy.
  - Idempotent — safe to re-run at any sweep tick. Reruns skip via
    dedup, so no accidental notification storm.

See [[feedback-discovery-vs-surfacing-separation]] +
    [[ship-129-prime-arc-retrospective-2026-09-08]].
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable


logger = logging.getLogger(__name__)


# Dedup window in days. One nudge per (tenant, framework) per 30d —
# tenants shouldn't feel harassed.
_NUDGE_DEDUP_DAYS = 30


@dataclass(frozen=True)
class FrameworkNudge:
    """Framework-applicability rule for enrolment nudge.

    Fields:
      standard_id    — canonical id in the standards table (matches
                       tenant_standards.standard_id + document_findings
                       .standard_id).
      display_name   — human-readable framework label for the
                       notification title + body.
      driving_facts  — client_facts columns whose value the rule reads.
                       Rule skips if ANY driving fact has fact_source
                       = 'default' (Ship 110'.d conservative-in-doubt
                       rule).
      predicate      — takes dict of {fact_col: value}, returns True
                       if the rule should fire (nudge the tenant to
                       enrol).
      why_message    — human-readable sentence explaining WHY the nudge
                       fires. Used in notification body.
    """
    standard_id:   str
    display_name:  str
    driving_facts: tuple[str, ...]
    predicate:     Callable[[dict], bool]
    why_message:   str


# ── Nudge rules ──────────────────────────────────────────────────

_NUDGES: tuple[FrameworkNudge, ...] = (

    # GDPR — territorial scope met (EU or UK subjects).
    FrameworkNudge(
        standard_id   = "GDPR:2016/679",
        display_name  = "GDPR",
        driving_facts = ("eu_data_subjects", "uk_data_subjects"),
        predicate     = lambda f: (
            f["eu_data_subjects"] is True or f["uk_data_subjects"] is True
        ),
        why_message   = (
            "Your organisation processes personal data of EU or UK data "
            "subjects. GDPR applies regardless of where your organisation "
            "is established."
        ),
    ),

    # ISO 27701 — PIMS extension is worth adding on top of GDPR /
    # ISO 27001 when the tenant processes personal data.
    FrameworkNudge(
        standard_id   = "ISO27701:2019",
        display_name  = "ISO 27701 (PIMS extension)",
        driving_facts = ("processes_personal_data",),
        predicate     = lambda f: f["processes_personal_data"] is True,
        why_message   = (
            "Your organisation processes personal data. ISO 27701 extends "
            "your ISO 27001 ISMS with a Privacy Information Management "
            "System, and its controls map directly to GDPR obligations."
        ),
    ),
)


# ── Write-path producer (optional; not wired yet) ────────────────


def emit_enrolment_nudge(
    pg_conn,
    tenant_id: str,
    nudge: FrameworkNudge,
    discovery_count: int = 0,
) -> bool:
    """Emit ONE unenrolled_framework_applicable notification if it
    passes dedup. Returns True on insert, False on dedup or error.

    Caller is responsible for having verified: (a) rule fires per
    driving facts, (b) framework is not already enrolled.
    """
    if not tenant_id or not nudge:
        return False
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
            )
            # Dedup — one nudge per (tenant, framework) per window.
            cur.execute(
                "SELECT 1 FROM tenant_notification "
                " WHERE tenant_id = %s::uuid "
                "   AND kind = 'unenrolled_framework_applicable' "
                "   AND body LIKE %s "
                "   AND fired_at > NOW() - make_interval(days => %s) "
                " LIMIT 1",
                (tenant_id, f"%{nudge.standard_id}%", _NUDGE_DEDUP_DAYS),
            )
            if cur.fetchone() is not None:
                return False

            title = f"{nudge.display_name} looks applicable — consider enrolling"
            body_parts = [nudge.why_message]
            if discovery_count > 0:
                body_parts.append(
                    f"We've already scanned your uploaded evidence and "
                    f"found {discovery_count} {nudge.display_name} findings "
                    f"ready to activate on enrolment (no re-upload needed)."
                )
            body_parts.append(
                f"Enrol from Profile → Frameworks. "
                f"Framework id: {nudge.standard_id}."
            )
            body = " ".join(body_parts)

            cur.execute(
                "INSERT INTO tenant_notification ("
                "  tenant_id, kind, title, body, severity, "
                "  related_entity_kind "
                ") VALUES (%s::uuid, 'unenrolled_framework_applicable', "
                "          %s, %s, 'low', 'framework')",
                (tenant_id, title, body),
            )
        return True
    except Exception as e:
        logger.warning("emit_enrolment_nudge: swallowed error: %s", e)
        try: pg_conn.rollback()
        except Exception: pass
        return False


# ── Sweep ────────────────────────────────────────────────────────


def _tenant_facts(pg_conn, tenant_id: str) -> dict:
    """Load the tenant's client_facts row + fact_source jsonb.

    Returns dict of {col: value} for the fact columns each rule reads,
    plus a `_fact_source` sub-dict.

    Returns empty dict if no client_facts row exists for the tenant.

    Sets app.tenant_id first — client_facts has strict RLS
    (`tenant_isolation`) and the arioncomply_app role must have the
    session variable set before reads succeed.
    """
    cols = set()
    for n in _NUDGES:
        cols.update(n.driving_facts)
    col_list = sorted(cols)
    if not col_list:
        return {}
    sql = (
        "SELECT " + ", ".join(col_list) + ", fact_source "
        "  FROM client_facts "
        " WHERE tenant_id = %s::uuid "
        " LIMIT 1"
    )
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute(sql, (tenant_id,))
        row = cur.fetchone()
    if row is None:
        return {}
    out: dict = {c: row[i] for i, c in enumerate(col_list)}
    out["_fact_source"] = row[-1] or {}
    return out


def _facts_ready(facts: dict, driving: tuple[str, ...]) -> bool:
    """True iff every driving fact has fact_source in ('declared',
    'derived'). Skips rules where any driver is at 'default' —
    matches the Ship 110'.d applicability engine convention.
    """
    src = facts.get("_fact_source") or {}
    for fc in driving:
        s = src.get(fc, "default")
        if s not in ("declared", "derived"):
            return False
    return True


def _enrolled_standards(pg_conn, tenant_id: str) -> set[str]:
    """Return set of standard_ids the tenant has enrolled (non-lapsed).
    Same predicate as Ship 129'.a/b Stage queue filters.

    tenant_standards has strict RLS; set app.tenant_id first.
    """
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute(
            "SELECT standard_id FROM tenant_standards "
            " WHERE tenant_id = %s::uuid AND status <> 'lapsed'",
            (tenant_id,),
        )
        return {r[0] for r in cur.fetchall()}


def _discovery_count(pg_conn, tenant_id: str, standard_id: str) -> int:
    """Count active document_findings for the (tenant, standard) that
    would activate if the framework were enrolled. Best-effort — used
    for enrichment, never for the trigger."""
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (tenant_id,))
            cur.execute(
                "SELECT COUNT(*) FROM document_findings "
                " WHERE tenant_id  = %s::uuid "
                "   AND standard_id = %s "
                "   AND is_active   = TRUE",
                (tenant_id, standard_id),
            )
            return int(cur.fetchone()[0] or 0)
    except Exception:
        return 0


def sweep_enrolment_nudge(
    pg_conn, tick_id: str, dry_run: bool = False,
) -> dict:
    """Per-tenant scan. For each active tenant, evaluate each nudge
    rule against client_facts. Emit ONE notification per (tenant,
    unenrolled framework) that: (a) has all driving facts declared/
    derived, (b) predicate returns True, (c) framework not currently
    enrolled, (d) dedup window has elapsed.

    Returns summary dict per the tick.py sweep convention.
    """
    from rag.scheduler.tick import _log_start, _log_complete

    row_id = _log_start(pg_conn, tick_id, "enrolment_nudge")

    scanned = acted = errored = 0
    per_tenant: dict[str, dict] = {}
    error_type = error_detail = None

    try:
        with pg_conn.cursor() as cur:
            # Iterate via posture_controls (has app_posture_all permissive
            # policy) rather than tenants (RLS-restricted to app.tenant_id).
            # Any tenant worth nudging has been seeded with posture on at
            # least one framework — no viable tenant is missed. Avoids
            # broadening the tenants-table RLS to arioncomply_app.
            cur.execute(
                "SELECT DISTINCT tenant_id::text "
                "  FROM posture_controls "
                " ORDER BY 1"
            )
            tenants = [r[0] for r in cur.fetchall()]

        for tenant_id in tenants:
            scanned += 1
            stats = {"emitted": 0, "skipped_dedup": 0,
                     "skipped_enrolled": 0, "skipped_predicate": 0,
                     "skipped_facts_not_ready": 0}
            try:
                facts = _tenant_facts(pg_conn, tenant_id)
                if not facts:
                    stats["skipped_facts_not_ready"] += len(_NUDGES)
                    per_tenant[tenant_id] = stats
                    continue
                enrolled = _enrolled_standards(pg_conn, tenant_id)
                for nudge in _NUDGES:
                    if nudge.standard_id in enrolled:
                        stats["skipped_enrolled"] += 1
                        continue
                    if not _facts_ready(facts, nudge.driving_facts):
                        stats["skipped_facts_not_ready"] += 1
                        continue
                    if not nudge.predicate(facts):
                        stats["skipped_predicate"] += 1
                        continue
                    if dry_run:
                        stats["emitted"] += 1
                        acted += 1
                        continue
                    count = _discovery_count(
                        pg_conn, tenant_id, nudge.standard_id,
                    )
                    if emit_enrolment_nudge(
                        pg_conn, tenant_id, nudge, discovery_count=count,
                    ):
                        stats["emitted"] += 1
                        acted += 1
                        pg_conn.commit()
                    else:
                        stats["skipped_dedup"] += 1
            except Exception as e:
                errored += 1
                logger.warning(
                    "sweep_enrolment_nudge: tenant %s error: %s",
                    tenant_id, e,
                )
                try: pg_conn.rollback()
                except Exception: pass
            per_tenant[tenant_id] = stats

    except Exception as e:
        error_type = type(e).__name__
        error_detail = str(e)[:400]
        errored += 1
        logger.exception("sweep_enrolment_nudge failed at top level")

    summary = {
        "items_scanned":  scanned,
        "items_acted_on": acted,
        "items_error":    errored,
        "per_tenant":     per_tenant,
    }
    _log_complete(
        pg_conn, row_id,
        items_scanned  = scanned,
        items_acted_on = acted,
        items_error    = errored,
        detail         = {"per_tenant": per_tenant, "dry_run": dry_run},
        status         = "failed" if error_type else "completed",
        error_type     = error_type,
        error_detail   = error_detail,
    )
    return summary
