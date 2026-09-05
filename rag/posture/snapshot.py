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
# Ship 118'.b landed applicability_status_log + client_facts_log on
# 2026-09-05. Snapshots asking for as_of >= this date have full
# history for applicability + scoping; before, we fall back to
# current-only (with a coverage_note explaining).
APPLICABILITY_TRACKING_BEGAN: Optional[date] = date(2026, 9, 5)
SCOPING_TRACKING_BEGAN:       Optional[date] = date(2026, 9, 5)


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


def _fetch_applicability_snapshot(
    cur, tenant_id: str, as_of_sql: Optional[str], as_of_label: str
) -> tuple[dict, str]:
    """Return ({(std, ref): (status, reason)}, coverage_kind).

    coverage_kind ∈ {'full', 'current-only'} — full when the caller
    asked for a date >= APPLICABILITY_TRACKING_BEGAN AND we have log
    coverage for that window, current-only otherwise.

    Ship 118'.b — reads applicability_status_log for historical
    reconstruction when the date is in the recording window. Prior to
    the tracking start date, we can only report the current state.
    """
    # Case 1: current
    if as_of_sql is None:
        cur.execute(
            """
            SELECT standard_id, control_ref, applicability_status, applicability_reason
              FROM posture_controls
             WHERE tenant_id = %s::uuid
               AND is_active = TRUE
            """,
            (tenant_id,),
        )
        return (
            {(std, ref): (status, reason) for std, ref, status, reason in cur.fetchall()},
            "full",
        )

    # Case 2: historical — check coverage window first
    tracking_start = APPLICABILITY_TRACKING_BEGAN
    asked_date = date.fromisoformat(as_of_label[:10]) if len(as_of_label) >= 10 else None
    if tracking_start is None or asked_date is None or asked_date < tracking_start:
        # Fall back to current-only
        cur.execute(
            """
            SELECT standard_id, control_ref, applicability_status, applicability_reason
              FROM posture_controls
             WHERE tenant_id = %s::uuid
               AND is_active = TRUE
            """,
            (tenant_id,),
        )
        return (
            {(std, ref): (status, reason) for std, ref, status, reason in cur.fetchall()},
            "current-only",
        )

    # Case 3: historical + in coverage window — reconstruct from log.
    # For each (standard, control), find the most recent log entry
    # with changed_at <= as_of. If none, the control has never had a
    # log entry (meaning it's been at its schema default 'applicable'
    # since tracking began — safe to report as 'applicable').
    cur.execute(
        """
        WITH tenant_controls AS (
            SELECT DISTINCT standard_id, control_ref
              FROM posture_controls
             WHERE tenant_id = %s::uuid AND is_active = TRUE
        ),
        latest_log AS (
            SELECT DISTINCT ON (standard_id, control_ref)
                   standard_id, control_ref, status_after, reason_after
              FROM applicability_status_log
             WHERE tenant_id = %s::uuid
               AND changed_at <= %s::timestamptz
             ORDER BY standard_id, control_ref, changed_at DESC
        )
        SELECT tc.standard_id, tc.control_ref,
               COALESCE(ll.status_after, 'applicable') AS status,
               ll.reason_after AS reason
          FROM tenant_controls tc
          LEFT JOIN latest_log ll USING (standard_id, control_ref)
        """,
        (tenant_id, tenant_id, as_of_sql),
    )
    return (
        {(std, ref): (status, reason) for std, ref, status, reason in cur.fetchall()},
        "full",
    )


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
        applicability, applicability_coverage = _fetch_applicability_snapshot(
            cur, tenant_id, as_of_sql, as_of_label,
        )

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
    if applicability_coverage == "full":
        applicability_note = (
            "Applicability reconstructed from applicability_status_log "
            "— reflects state at requested date."
        )
    else:
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
            "coverage": applicability_coverage,
            "source":   ("applicability_status_log (Ship 118'.b)"
                         if applicability_coverage == "full"
                         else "posture_controls (current-only fallback)"),
            "note":     ("Full reconstruction from log."
                         if applicability_coverage == "full"
                         else f"Requested date is before tracking start "
                              f"({_track_start}); showing current state."),
        },
        "scoping_facts": {
            "coverage": ("full" if (
                as_of_sql is not None
                and SCOPING_TRACKING_BEGAN is not None
                and date.fromisoformat(as_of_label[:10]) >= SCOPING_TRACKING_BEGAN
            ) else "current-only"),
            "source":   "client_facts_log (Ship 118'.b)",
            "note":     "Point-in-time scoping-fact reconstruction: query client_facts_log directly.",
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


# ── HTML rendering (Ship 118'.c) ────────────────────────────────────
# Print-optimised self-contained HTML. No external assets. Auditor
# opens the URL in a browser + uses "Save as PDF" from the browser
# menu. Includes a date picker that reloads the page with new
# ?as_of= query param.

_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Compliance snapshot — {tenant_name} — {as_of}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root {{
  --fg:          #1a1a1a;
  --muted:       #5f5e5a;
  --line:        #e2e0d8;
  --paper:       #fbfaf4;
  --panel:       #ffffff;
  --accent:      #534AB7;
  --accent-soft: #EEEDFE;
  --nc:          #B92A28;
  --nc-soft:     #FEECEA;
  --ofi:         #a37b00;
  --ofi-soft:    #fff3b0;
  --comply:      #1D9E75;
  --comply-soft: #E5F5EE;
  --na:          #6b7280;
  --na-soft:     #f3f4f6;
  --sans:        -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  --mono:        "SF Mono", Menlo, Consolas, monospace;
}}
* {{ box-sizing: border-box; }}
body {{
  font-family: var(--sans); font-size: 14px; line-height: 1.55; color: var(--fg);
  background: var(--paper); max-width: 1100px; margin: 0 auto;
  padding: 32px 28px 100px;
}}
h1 {{ font-size: 2em; margin: 0.2em 0 0.4em; letter-spacing: -0.01em; }}
h2 {{ font-size: 1.3em; margin: 2em 0 0.5em; padding-bottom: 0.3em;
     border-bottom: 2px solid var(--line); }}
h3 {{ font-size: 1.05em; margin: 1.5em 0 0.4em; color: var(--accent); }}
p  {{ margin: 0.4em 0 0.8em; }}
code {{ font-family: var(--mono); font-size: 0.9em; background: #f2f0e8;
       padding: 1px 5px; border-radius: 3px; }}
a  {{ color: var(--accent); }}

.header {{
  padding: 20px 24px; background: linear-gradient(135deg, #F3F1FA, #EEEDFE);
  border-left: 4px solid var(--accent); border-radius: 6px; margin-bottom: 24px;
}}
.header .eyebrow {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em;
                   font-weight: 700; color: var(--accent); margin-bottom: 6px; }}
.header .meta {{ font-size: 12px; color: var(--muted); margin-top: 6px; }}
.meta-grid {{ display: grid; grid-template-columns: max-content auto;
              gap: 6px 14px; margin: 12px 0; font-size: 13px; }}
.meta-grid dt {{ color: var(--muted); font-weight: 600; }}
.meta-grid dd {{ margin: 0; }}

.picker-bar {{
  padding: 14px 18px; background: var(--panel); border: 1px solid var(--line);
  border-radius: 6px; margin-bottom: 20px; display: flex; align-items: center;
  gap: 12px; flex-wrap: wrap;
}}
.picker-bar label {{ font-weight: 600; font-size: 13px; color: var(--muted); }}
.picker-bar input[type=date] {{ padding: 6px 10px; border: 1px solid var(--line);
                                 border-radius: 4px; font-family: inherit; font-size: 13px; }}
.picker-bar button {{ padding: 6px 14px; border: 1px solid var(--accent);
                       background: var(--accent); color: white; border-radius: 4px;
                       cursor: pointer; font-family: inherit; font-size: 13px; }}
.picker-bar a {{ font-size: 12px; color: var(--muted); text-decoration: underline; }}

.summary-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px; margin: 16px 0;
}}
.summary-card {{
  padding: 14px 16px; background: var(--panel); border: 1px solid var(--line);
  border-radius: 6px; text-align: center;
}}
.summary-card .num {{ font-size: 1.6em; font-weight: 700; display: block; line-height: 1.1; }}
.summary-card .label {{ font-size: 11px; color: var(--muted); text-transform: uppercase;
                        letter-spacing: 0.05em; margin-top: 4px; }}
.summary-card.nc     .num {{ color: var(--nc); }}
.summary-card.ofi    .num {{ color: var(--ofi); }}
.summary-card.comply .num {{ color: var(--comply); }}
.summary-card.na     .num {{ color: var(--na); }}
.summary-card.na-scope .num {{ color: var(--accent); }}

.coverage-notes {{
  background: #f6f4ec; border: 1px solid var(--line); border-radius: 6px;
  padding: 12px 16px; margin: 16px 0; font-size: 12px;
}}
.coverage-notes h4 {{ margin: 0 0 8px; font-size: 11px; text-transform: uppercase;
                       letter-spacing: 0.1em; color: var(--muted); }}
.coverage-notes dl {{ display: grid; grid-template-columns: max-content auto;
                       gap: 4px 12px; margin: 0; }}
.coverage-notes dt {{ font-weight: 600; }}
.coverage-notes dd {{ margin: 0; color: var(--muted); }}
.coverage-notes .cov-full {{ color: var(--comply); font-weight: 600; }}
.coverage-notes .cov-partial {{ color: var(--ofi); font-weight: 600; }}

table {{ width: 100%; border-collapse: collapse; margin: 12px 0 20px; font-size: 12.5px; }}
th, td {{ border-bottom: 1px solid var(--line); padding: 8px 10px; text-align: left;
         vertical-align: top; }}
th {{ background: #f2f0e8; font-weight: 700; font-size: 11px; text-transform: uppercase;
     letter-spacing: 0.04em; color: var(--muted); }}
td.ref {{ font-family: var(--mono); font-size: 11.5px; white-space: nowrap; }}
td.reason {{ color: var(--muted); font-size: 11.5px; max-width: 480px; }}

.pill {{ display: inline-block; padding: 2px 8px; border-radius: 10px;
        font-size: 10.5px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.04em; }}
.pill.nc      {{ background: var(--nc-soft);     color: var(--nc); }}
.pill.ofi     {{ background: var(--ofi-soft);    color: var(--ofi); }}
.pill.comply  {{ background: var(--comply-soft); color: var(--comply); }}
.pill.na      {{ background: var(--na-soft);     color: var(--na); }}
.pill.na-scope{{ background: var(--accent-soft); color: var(--accent); }}
.pill.notass  {{ background: #f2f0e8;            color: var(--muted); }}

.footer-legal {{
  margin-top: 40px; padding: 18px 20px; background: var(--panel);
  border: 1px solid var(--line); border-radius: 6px; font-size: 12px; color: var(--muted);
}}
.footer-legal strong {{ color: var(--fg); }}
.watermark {{ position: fixed; bottom: 8px; right: 12px; font-size: 10px;
              color: rgba(0,0,0,0.25); font-family: var(--mono); }}

/* Print rules */
@media print {{
  body {{ background: white; padding: 0.5in; max-width: none; }}
  .picker-bar {{ display: none; }}
  .watermark {{ position: fixed; bottom: 0.2in; right: 0.4in; font-size: 8pt; }}
  h2 {{ page-break-after: avoid; }}
  table {{ page-break-inside: auto; }}
  tr {{ page-break-inside: avoid; page-break-after: auto; }}
  .framework-section {{ page-break-before: auto; }}
}}
</style>
</head>
<body>

<div class="header">
  <div class="eyebrow">Compliance snapshot</div>
  <h1>{tenant_name}</h1>
  <p style="margin:6px 0"><strong>As of:</strong> {as_of}</p>
  <div class="meta">
    Generated {generated_at} &middot; Snapshot ID: <code>{snapshot_id}</code>
  </div>
</div>

<div class="picker-bar">
  <form method="get" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:0">
    <label for="as_of_input">View posture as of:</label>
    <input type="date" id="as_of_input" name="as_of" value="{as_of_input}"
           max="{today}" min="2026-01-01">
    <input type="hidden" name="fmt" value="html">
    <button type="submit">Reload</button>
    <a href="?fmt=html">Reset to today</a>
    <span style="margin-left:auto;color:var(--muted);font-size:11px">
      To save as PDF: use your browser's Print &rarr; Save as PDF
    </span>
  </form>
</div>

<div class="summary-grid">
  <div class="summary-card"><span class="num">{total}</span><span class="label">total controls</span></div>
  <div class="summary-card nc"><span class="num">{nc_count}</span><span class="label">non-conformity</span></div>
  <div class="summary-card ofi"><span class="num">{ofi_count}</span><span class="label">opportunity for improvement</span></div>
  <div class="summary-card comply"><span class="num">{comply_count}</span><span class="label">comply</span></div>
  <div class="summary-card na-scope"><span class="num">{na_scope_count}</span><span class="label">out of scope (N/A)</span></div>
  <div class="summary-card"><span class="num">{notass_count}</span><span class="label">not assessed</span></div>
  <div class="summary-card"><span class="num">{evidence_total}</span><span class="label">evidence rows</span></div>
  <div class="summary-card"><span class="num">{cascade_total}</span><span class="label">open follow-ups</span></div>
</div>

<div class="coverage-notes">
  <h4>Coverage notes — what this snapshot can and cannot reconstruct</h4>
  <dl>
    {coverage_rows}
  </dl>
</div>

{framework_sections}

<div class="footer-legal">
  <p><strong>About this document.</strong> This is a compliance snapshot generated
  by ArionComply from tenant {tenant_name}'s ledger. It reflects the compliance
  posture as of {as_of}, reconstructed from the tenant's assertion history +
  evidence lifecycle timestamps.</p>
  <p><strong>Data protection.</strong> This snapshot may contain third-party
  personal data (data subjects named in evidence, staff who acted on findings).
  It is intended for the audit engagement it was generated under. Retention +
  further distribution rules follow the tenant's data-protection policy and the
  auditor's engagement letter.</p>
  <p><strong>Not a certification.</strong> ArionComply surfaces compliance state
  as observed; the tenant + their auditor own the compliance decision.</p>
</div>

<div class="watermark">
  {tenant_name} &middot; {snapshot_id}
</div>

</body>
</html>
"""


def _render_pill(finding: str, applicability: str) -> str:
    """CSS-styled pill for the finding column."""
    if applicability == "na":
        return '<span class="pill na-scope">N/A (out of scope)</span>'
    css_class = {
        "NC":            "nc",
        "OFI":           "ofi",
        "Comply":        "comply",
        "N/A":           "na",
        "Not assessed":  "notass",
    }.get(finding, "notass")
    label = finding
    return f'<span class="pill {css_class}">{label}</span>'


def _render_framework_section(std: str, rows: list[ControlSnapshot]) -> str:
    """Render one <section> per framework with a controls table."""
    from html import escape

    def _human_std(s: str) -> str:
        return (s.replace("ISO27001:2022",  "ISO 27001:2022")
                 .replace("ISO27701:2019",  "ISO 27701:2019")
                 .replace("GDPR:2016/679",  "GDPR (2016/679)"))

    rows_html = []
    for c in sorted(rows, key=lambda r: r.control_ref):
        pill = _render_pill(c.finding, c.applicability_status)
        reason = escape(c.finding_reason or "") if c.applicability_status != "na" else escape(c.applicability_reason or "")
        evidence_note = ""
        if c.evidence_count > 0:
            evidence_note = f'<br><span style="color:var(--muted);font-size:11px">{c.evidence_count} evidence row{"s" if c.evidence_count != 1 else ""}</span>'
        followup_note = ""
        if c.cascade_open_followups > 0:
            followup_note = f'<br><span style="color:var(--ofi);font-size:11px">{c.cascade_open_followups} open follow-up{"s" if c.cascade_open_followups != 1 else ""}</span>'
        rows_html.append(f"""
        <tr>
          <td class="ref">{escape(c.control_ref)}</td>
          <td>{pill}{evidence_note}{followup_note}</td>
          <td class="reason">{reason}</td>
        </tr>
        """)
    return f"""
    <section class="framework-section">
      <h2>{_human_std(std)}</h2>
      <table>
        <thead>
          <tr><th style="width:12%">Control</th><th style="width:22%">Verdict</th><th>Reason / gap</th></tr>
        </thead>
        <tbody>
          {"".join(rows_html)}
        </tbody>
      </table>
    </section>
    """


def snapshot_to_html(snap: PostureSnapshot, snapshot_id: str | None = None) -> str:
    """Print-optimised self-contained HTML."""
    import uuid as _uuid
    from collections import Counter
    from datetime import date as _date
    from html import escape

    sid = snapshot_id or str(_uuid.uuid4())

    # Summary counts
    total    = len(snap.controls)
    finding_c = Counter((c.finding, c.applicability_status) for c in snap.controls)
    def _count(finding_val, na_scope=None):
        n = 0
        for (f, a), k in finding_c.items():
            if a == "na" and na_scope is not True:
                continue
            if a != "na" and na_scope is True:
                continue
            if f == finding_val:
                n += k
        return n

    nc_count      = _count("NC")
    ofi_count     = _count("OFI")
    comply_count  = _count("Comply")
    notass_count  = _count("Not assessed")
    na_scope_count = sum(1 for c in snap.controls if c.applicability_status == "na")
    evidence_total = sum(c.evidence_count for c in snap.controls)
    cascade_total  = sum(c.cascade_open_followups for c in snap.controls)

    # Coverage rows
    coverage_rows = []
    for axis, meta in snap.coverage_notes.items():
        cov = meta.get("coverage", "?")
        cov_class = "cov-full" if cov == "full" else "cov-partial"
        coverage_rows.append(
            f'<dt>{escape(axis)}</dt>'
            f'<dd><span class="{cov_class}">{escape(cov)}</span> &middot; {escape(meta.get("note",""))}</dd>'
        )

    # Framework sections
    per_std: dict = {}
    for c in snap.controls:
        per_std.setdefault(c.standard_id, []).append(c)
    section_html = "\n".join(
        _render_framework_section(std, rows)
        for std, rows in sorted(per_std.items())
    )

    # Input date value
    as_of_input = snap.as_of if len(snap.as_of) >= 10 and snap.as_of != "now" else ""
    today_str = _date.today().isoformat()

    return _HTML_TEMPLATE.format(
        tenant_name    = escape(snap.tenant_name),
        as_of          = escape(snap.as_of),
        as_of_input    = escape(as_of_input),
        today          = today_str,
        generated_at   = escape(snap.generated_at),
        snapshot_id    = escape(sid),
        total          = total,
        nc_count       = nc_count,
        ofi_count      = ofi_count,
        comply_count   = comply_count,
        na_scope_count = na_scope_count,
        notass_count   = notass_count,
        evidence_total = evidence_total,
        cascade_total  = cascade_total,
        coverage_rows  = "\n".join(coverage_rows),
        framework_sections = section_html,
    )
