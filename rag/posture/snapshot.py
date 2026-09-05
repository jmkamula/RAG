"""
rag/posture/snapshot.py — Ship 118'.a (2026-09-05).

Point-in-time posture reconstruction. Answers the question a regulator
asks after an incident: "on the day of the breach, what was your
compliance posture?"

Sources reconstructed from what's already tracked (Ship 4'.b addendum
made posture_status_log INSERT/SELECT-only; Ship 59'.b posture_assertions
is supersession-tracked; document_findings has full lifecycle
timestamps):

  finding + gap_description + source  ← posture_assertions
      (WHERE set_at <= as_of AND (superseded_at IS NULL OR superseded_at > as_of)
       AND status IN ('active','superseded')
       — pick most recent per (control_ref, standard_id))

  evidence linked                     ← document_findings
      (WHERE extracted_at <= as_of
       AND reviewed_at <= as_of
       AND (deleted_at IS NULL OR deleted_at > as_of)
       AND (expires_at IS NULL OR expires_at > as_of)      # Ship 118'.a A2 choice
       AND (resolved_at IS NULL OR resolved_at > as_of)
       AND review_status = 'approved')

  applicability_status + reason       ← posture_controls (CURRENT ONLY)
                                         ⚠ Ship 118'.b will add historical.

  cascade follow-ups open on date     ← triggered_implication
      (WHERE fired_at <= as_of
       AND (resolved_at IS NULL OR resolved_at > as_of))

Design decisions (locked with user 2026-09-05):
  · A2 — evidence includes expires_at guard (stale evidence doesn't appear)
  · B1 — for axes we don't have historical tracking on (applicability,
         scoping facts, gap_description on posture_controls), the response
         includes a `coverage_notes` field marking those axes as
         "current state; historical tracking begins <YYYY-MM-DD>".

as_of=None means "now" (current state).
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from typing import Optional


# ── Coverage constants ──────────────────────────────────────────────
# When Ship 118'.b lands (applicability_status_log + client_facts_log),
# update this constant. Snapshots asking for as_of >= this date will
# have full applicability/scoping history; before, current-only.
APPLICABILITY_TRACKING_BEGAN: Optional[date] = None  # set on 118'.b ship
SCOPING_TRACKING_BEGAN:       Optional[date] = None  # set on 118'.b ship


@dataclass
class EvidenceRow:
    filename:        str
    must_id:         str | None
    excerpt:         str | None
    section:         str | None
    confidence:      str | None
    extracted_at:    datetime | None
    reviewed_at:     datetime | None
    status:          str          # 'approved' — snapshot logic pre-filters


@dataclass
class ControlSnapshot:
    standard_id:            str
    control_ref:            str
    node_id:                str | None
    finding:                str          # NC / OFI / Comply / N/A / Not assessed
    finding_reason:         str | None
    finding_source:         str          # tenant / assessor / engine
    finding_set_at:         datetime | None
    applicability_status:   str          # applicable / na
    applicability_reason:   str | None
    applicability_note:     str          # coverage caveat
    evidence_count:         int
    evidence:               list[EvidenceRow] = field(default_factory=list)
    cascade_open_followups: int = 0


@dataclass
class PostureSnapshot:
    tenant_id:      str
    tenant_name:    str
    as_of:          str          # ISO date or 'now'
    generated_at:   str          # ISO datetime
    generated_by:   str | None   # user_id or api_key label
    control_count:  int
    controls:       list[ControlSnapshot]
    coverage_notes: dict         # per-axis caveats


# ── Snapshot logic ──────────────────────────────────────────────────

def _resolve_as_of(as_of: str | date | datetime | None) -> tuple[Optional[str], str]:
    """Normalize the as_of parameter into (SQL timestamp str, human label).

    Returns (None, 'now') when as_of is None or 'now'.
    """
    if as_of is None or (isinstance(as_of, str) and as_of.lower() in ("now", "")):
        return None, "now"
    if isinstance(as_of, str):
        # Accept YYYY-MM-DD (interpret as end-of-day UTC to include events
        # from that whole day) OR full ISO timestamp.
        if len(as_of) == 10:
            return f"{as_of} 23:59:59.999999+00", as_of
        return as_of, as_of
    if isinstance(as_of, date) and not isinstance(as_of, datetime):
        return f"{as_of.isoformat()} 23:59:59.999999+00", as_of.isoformat()
    if isinstance(as_of, datetime):
        return as_of.isoformat(), as_of.date().isoformat()
    raise ValueError(f"unsupported as_of type: {type(as_of).__name__}")


def _fetch_findings_snapshot(cur, tenant_id: str, as_of_sql: Optional[str]) -> dict:
    """For each (standard_id, control_ref), find the effective assertion.

    Returns dict keyed by (standard_id, control_ref) → assertion tuple:
      (finding, gap_description, source, set_at)

    When as_of_sql is None, returns the current active assertions.
    """
    if as_of_sql is None:
        cur.execute(
            """
            SELECT DISTINCT ON (control_ref, standard_id)
                   control_ref, standard_id, finding, gap_description, source, set_at
              FROM posture_assertions
             WHERE tenant_id = %s::uuid
               AND status = 'active'
             ORDER BY control_ref, standard_id, set_at DESC
            """,
            (tenant_id,),
        )
    else:
        cur.execute(
            """
            SELECT DISTINCT ON (control_ref, standard_id)
                   control_ref, standard_id, finding, gap_description, source, set_at
              FROM posture_assertions
             WHERE tenant_id = %s::uuid
               AND set_at <= %s::timestamptz
               AND (superseded_at IS NULL OR superseded_at > %s::timestamptz)
               AND status IN ('active', 'superseded')
             ORDER BY control_ref, standard_id, set_at DESC
            """,
            (tenant_id, as_of_sql, as_of_sql),
        )
    return {
        (std, ref): (finding, gap, source, set_at)
        for ref, std, finding, gap, source, set_at in cur.fetchall()
    }


def _fetch_evidence_snapshot(cur, tenant_id: str, as_of_sql: Optional[str]) -> dict:
    """Return dict keyed by (standard_id, control_ref) → list[EvidenceRow].

    Applies the Ship 118'.a A2 filter:
      approved + not-deleted + not-expired + not-resolved as of the date.
    """
    if as_of_sql is None:
        cur.execute(
            """
            SELECT df.standard_id, df.control_ref,
                   cd.filename, df.checklist_item_id,
                   df.excerpt, df.section_number, df.confidence,
                   df.extracted_at, df.reviewed_at
              FROM document_findings df
              JOIN client_documents cd ON cd.id = df.document_id
             WHERE df.tenant_id = %s::uuid
               AND df.is_active = TRUE
               AND df.review_status = 'approved'
               AND (df.expires_at IS NULL OR df.expires_at > NOW())
             ORDER BY df.standard_id, df.control_ref, df.extracted_at DESC
            """,
            (tenant_id,),
        )
    else:
        cur.execute(
            """
            SELECT df.standard_id, df.control_ref,
                   cd.filename, df.checklist_item_id,
                   df.excerpt, df.section_number, df.confidence,
                   df.extracted_at, df.reviewed_at
              FROM document_findings df
              JOIN client_documents cd ON cd.id = df.document_id
             WHERE df.tenant_id = %s::uuid
               AND df.extracted_at   <= %s::timestamptz
               AND df.reviewed_at    <= %s::timestamptz
               AND (df.deleted_at   IS NULL OR df.deleted_at   > %s::timestamptz)
               AND (df.expires_at   IS NULL OR df.expires_at   > %s::timestamptz)
               AND (df.resolved_at  IS NULL OR df.resolved_at  > %s::timestamptz)
               AND df.review_status = 'approved'
             ORDER BY df.standard_id, df.control_ref, df.extracted_at DESC
            """,
            (tenant_id, as_of_sql, as_of_sql, as_of_sql, as_of_sql, as_of_sql),
        )
    out: dict = {}
    for std, ref, fname, cid, excerpt, sec, conf, ext_at, rev_at in cur.fetchall():
        key = (std, ref)
        out.setdefault(key, []).append(EvidenceRow(
            filename     = fname,
            must_id      = cid,
            excerpt      = excerpt,
            section      = sec,
            confidence   = conf,
            extracted_at = ext_at,
            reviewed_at  = rev_at,
            status       = 'approved',
        ))
    return out


def _fetch_cascade_open_snapshot(cur, tenant_id: str, as_of_sql: Optional[str]) -> dict:
    """Count triggered_implication rows that were open on the given date.

    Open = fired_at <= as_of AND (resolved_at is null OR resolved_at > as_of).
    """
    if as_of_sql is None:
        cur.execute(
            """
            SELECT target_standard_id, target_control_ref, COUNT(*)
              FROM triggered_implication
             WHERE tenant_id = %s::uuid
               AND resolved_at IS NULL
             GROUP BY 1, 2
            """,
            (tenant_id,),
        )
    else:
        cur.execute(
            """
            SELECT target_standard_id, target_control_ref, COUNT(*)
              FROM triggered_implication
             WHERE tenant_id = %s::uuid
               AND fired_at <= %s::timestamptz
               AND (resolved_at IS NULL OR resolved_at > %s::timestamptz)
             GROUP BY 1, 2
            """,
            (tenant_id, as_of_sql, as_of_sql),
        )
    return {(std, ref): n for std, ref, n in cur.fetchall()}


def _fetch_applicability_current(cur, tenant_id: str) -> dict:
    """Current applicability_status + reason from posture_controls.

    Ship 118'.a limitation: current-only (see APPLICABILITY_TRACKING_BEGAN).
    Ship 118'.b will add historical tracking.
    """
    cur.execute(
        """
        SELECT standard_id, control_ref, applicability_status, applicability_reason
          FROM posture_controls
         WHERE tenant_id = %s::uuid
           AND is_active = TRUE
        """,
        (tenant_id,),
    )
    return {
        (std, ref): (status, reason)
        for std, ref, status, reason in cur.fetchall()
    }


def _fetch_tenant_meta(cur, tenant_id: str) -> tuple[str, str | None]:
    """Return (tenant_name, current_user_note)."""
    cur.execute("SELECT name FROM tenants WHERE id = %s::uuid", (tenant_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"tenant not found: {tenant_id}")
    return row[0], None


def snapshot_posture(
    pg_conn,
    tenant_id:   str,
    as_of:       str | date | datetime | None = None,
    generated_by: str | None = None,
) -> PostureSnapshot:
    """Reconstruct posture as of a given date (or now).

    Reads use RLS via set_session semantics — caller is responsible for
    ensuring pg_conn is in an appropriate session state, OR pass a
    connection owned by the arioncomply owner role (bypasses RLS).

    Returns a PostureSnapshot dataclass. Use .to_dict() for JSON
    serialisation, or asdict() for a nested plain dict.
    """
    as_of_sql, as_of_label = _resolve_as_of(as_of)

    with pg_conn.cursor() as cur:
        # RLS-safe set_config — no-op for owner-role connections.
        try:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        except Exception:
            pass  # owner-role connections don't need RLS context

        tenant_name, _ = _fetch_tenant_meta(cur, tenant_id)
        assertions   = _fetch_findings_snapshot(cur, tenant_id, as_of_sql)
        evidence     = _fetch_evidence_snapshot(cur, tenant_id, as_of_sql)
        cascade_open = _fetch_cascade_open_snapshot(cur, tenant_id, as_of_sql)
        applicability = _fetch_applicability_current(cur, tenant_id)

        # posture_controls rows the tenant is enrolled against, so we can
        # emit "Not assessed" for controls that never had an assertion.
        cur.execute(
            """
            SELECT DISTINCT standard_id, control_ref, node_id
              FROM posture_controls
             WHERE tenant_id = %s::uuid
               AND is_active = TRUE
             ORDER BY standard_id, control_ref
            """,
            (tenant_id,),
        )
        all_controls = cur.fetchall()

    # Build per-control snapshots
    controls: list[ControlSnapshot] = []
    _track_start = (
        APPLICABILITY_TRACKING_BEGAN.isoformat()
        if APPLICABILITY_TRACKING_BEGAN
        else "(Ship 118prime.b, not yet shipped)"
    )
    applicability_note = (
        "Applicability shown is current state; "
        "historical tracking begins " + _track_start
    )
    for std, ref, node_id in all_controls:
        key = (std, ref)

        # Finding
        if key in assertions:
            finding, gap, source, set_at = assertions[key]
        else:
            finding, gap, source, set_at = "Not assessed", None, "engine", None

        # Applicability (current-only for now)
        app_status, app_reason = applicability.get(key, ("applicable", None))

        controls.append(ControlSnapshot(
            standard_id            = std,
            control_ref            = ref,
            node_id                = node_id,
            finding                = finding,
            finding_reason         = gap,
            finding_source         = source,
            finding_set_at         = set_at,
            applicability_status   = app_status,
            applicability_reason   = app_reason,
            applicability_note     = applicability_note,
            evidence_count         = len(evidence.get(key, [])),
            evidence               = evidence.get(key, []),
            cascade_open_followups = cascade_open.get(key, 0),
        ))

    coverage_notes = {
        "finding": {
            "coverage": "full",
            "source":   "posture_assertions supersession trail",
            "note":     "Every finding change is preserved and time-ordered.",
        },
        "evidence": {
            "coverage": "full",
            "source":   "document_findings lifecycle timestamps",
            "note":     "Includes expires_at + deleted_at + resolved_at guards.",
        },
        "cascade_followups": {
            "coverage": "full",
            "source":   "triggered_implication",
            "note":     "fired_at + resolved_at reconstruct open follow-ups.",
        },
        "applicability_status": {
            "coverage": "current-only",
            "source":   "posture_controls (mutable)",
            "note":     "Historical tracking added in Ship 118'.b.",
        },
        "scoping_facts": {
            "coverage": "current-only",
            "source":   "client_facts + fact_source jsonb",
            "note":     "Historical tracking added in Ship 118'.b.",
        },
    }

    return PostureSnapshot(
        tenant_id      = tenant_id,
        tenant_name    = tenant_name,
        as_of          = as_of_label,
        generated_at   = datetime.now(timezone.utc).isoformat(),
        generated_by   = generated_by,
        control_count  = len(controls),
        controls       = controls,
        coverage_notes = coverage_notes,
    )


def snapshot_to_dict(snap: PostureSnapshot) -> dict:
    """Serialise for JSON export. Handles datetime → ISO strings."""
    def _encode(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return obj
    d = asdict(snap)
    # Walk + convert datetimes
    def _walk(x):
        if isinstance(x, dict):
            return {k: _walk(v) for k, v in x.items()}
        if isinstance(x, list):
            return [_walk(v) for v in x]
        return _encode(x)
    return _walk(d)


def snapshot_to_csv(snap: PostureSnapshot) -> str:
    """One row per control. Evidence + coverage_notes summarised as counts."""
    import csv
    from io import StringIO
    buf = StringIO()
    w = csv.writer(buf)
    w.writerow([
        "standard_id", "control_ref", "finding", "finding_reason",
        "finding_source", "finding_set_at",
        "applicability_status", "applicability_reason",
        "evidence_count", "cascade_open_followups",
    ])
    for c in snap.controls:
        w.writerow([
            c.standard_id, c.control_ref, c.finding, c.finding_reason or "",
            c.finding_source, c.finding_set_at.isoformat() if c.finding_set_at else "",
            c.applicability_status, c.applicability_reason or "",
            c.evidence_count, c.cascade_open_followups,
        ])
    return buf.getvalue()
