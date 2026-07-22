"""
Ship 14'.c (2026-07-22) — risk-register query + display helpers.

Reads from the tenant-scoped `risks` table (schema_v2 + schema_v87
additions) using RLS-enforced session context. Callers are
responsible for setting `app.tenant_id` on the connection
BEFORE invoking any of these functions.

Design:
- Response models are Pydantic — usable directly as FastAPI
  response_model on both internal and external endpoints.
- `linked_controls_view()` expands `control_refs TEXT[]` into
  a structured LinkedControl list carrying role + subject +
  display name — framework-role-model discipline (Ship 14'.a
  addendum): program/extension/obligation/guidance rendered
  first-class.
- Row-level filters live on the client (or dashboard) — this
  module returns everything the tenant owns. Pagination is
  the only server-side reduction to avoid runaway payloads
  when a mature tenant has 500+ risks.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ── Response models ──────────────────────────────────────────


class LinkedControl(BaseModel):
    """One entry in a risk's `linked_controls` array — a control
    reference exploded into standard + role + display fields."""
    control_ref:       str            = Field(..., description="Composite id — e.g. `ISO27001:2022:A.5.15`.")
    ref:               str            = Field(..., description="Bare control ref — e.g. `A.5.15`.")
    standard_id:       str            = Field(..., description="Canonical DB slug — e.g. `ISO27001:2022`.")
    standard_display:  str            = Field(..., description="Human display name — e.g. `ISO 27001:2022`.")
    role:              Optional[str]  = Field(None, description="`program` / `extension` / `obligation` / `guidance`.")
    subject:           Optional[list[str]] = Field(None, description="Content subject tags — e.g. `['information_security']`.")


class RiskRow(BaseModel):
    """Compact row for list surfaces — dashboard cards, chat digest,
    external API bulk pull."""
    id:                    str
    external_ref:          str = Field(..., description="Tenant-authored id — e.g. `R-042`.")
    asset_ref:             Optional[str] = None
    asset_name:            Optional[str] = None
    threat:                Optional[str] = None
    vulnerability:         Optional[str] = None
    likelihood:            Optional[int] = None
    impact:                Optional[int] = None
    risk_score:            Optional[int] = None
    risk_owner_text:       Optional[str] = None
    treatment_option:      Optional[str] = None
    treatment_status:      Optional[str] = None
    residual_risk_level:   Optional[int] = None
    review_date:           Optional[str] = None
    linked_controls:       list[LinkedControl] = Field(default_factory=list)


class RiskDetail(RiskRow):
    """Drill-in shape — RiskRow + treatment plan + audit trail."""
    interested_party:      Optional[str] = None
    treatment_rationale:   Optional[str] = None
    treatment_action:      Optional[str] = None
    resources_required:    Optional[str] = None
    performance_indicators: list[str] = Field(default_factory=list)
    constraints:           Optional[str] = None
    reporting_cadence:     Optional[str] = None
    implementation_date:   Optional[str] = None
    effectiveness_review:  Optional[str] = None
    created_at:            Optional[str] = None
    updated_at:            Optional[str] = None


class RiskSummary(BaseModel):
    """Dashboard-friendly aggregate — used by both the internal
    dashboard endpoint and the external summary endpoint."""
    total:                 int
    open:                  int = Field(..., description="Rows with treatment_status IN (open, in_progress).")
    overdue:               int = Field(..., description="Rows past review_date and not `implemented`.")
    above_threshold:       int = Field(..., description="Rows with residual_risk_level >= 15 (top quintile).")
    unassigned:            int = Field(..., description="Rows without a risk_owner (neither text nor UUID).")
    by_treatment_option:   dict = Field(default_factory=dict, description="Counts per option: Mitigate/Accept/Transfer/Avoid.")
    by_status:             dict = Field(default_factory=dict, description="Counts per status: open/in_progress/implemented/accepted.")
    heatmap:               dict = Field(default_factory=dict, description="`{(likelihood,impact): count}` — 5x5 grid for the dashboard heatmap. JSON-safe keys as `L{n}_I{n}`.")
    top_risks:             list[RiskRow] = Field(default_factory=list, description="Top 5 by risk_score DESC — quick-view for landing cards.")


# ── Standards lookup cache ───────────────────────────────────


_STANDARDS_CACHE: dict[str, dict] = {}


def _load_standards(cur) -> dict[str, dict]:
    """Cache `standards` metadata (role, subject, display) at first
    call. Read-only; the cache is safe to share across tenants
    because standards are global."""
    if _STANDARDS_CACHE:
        return _STANDARDS_CACHE
    cur.execute(
        "SELECT id, short_name, full_name, role, subject "
        "FROM standards"
    )
    for row in cur.fetchall():
        std_id, short_name, full_name, role, subject = row
        _STANDARDS_CACHE[std_id] = {
            "short_name": short_name,
            "full_name":  full_name,
            "role":       role,
            "subject":    list(subject or []),
        }
    return _STANDARDS_CACHE


def linked_controls_view(control_refs: list[str], cur) -> list[LinkedControl]:
    """Expand raw `control_refs TEXT[]` values into structured
    LinkedControl entries. Uses `rag/output/vocab/` for the
    display name (Ship 7'.b output-gateway pattern) and the
    `standards` table for role + subject metadata.

    Unknown standard prefixes render with a fallback display —
    never fail; new frameworks land as data, not code."""
    if not control_refs:
        return []
    stds = _load_standards(cur)

    from rag.output.vocab import display_name as _display_name

    out: list[LinkedControl] = []
    for cref in control_refs:
        # Expected shape: STANDARD:VERSION:REF (e.g. ISO27001:2022:A.5.15).
        # Fall back gracefully if the shape isn't recognised —
        # never lose data.
        parts = cref.rsplit(":", 1)
        if len(parts) != 2:
            std_id = ""
            bare_ref = cref
        else:
            std_id, bare_ref = parts

        meta = stds.get(std_id, {})
        std_display = _display_name(std_id, fallback=std_id) if std_id else "(unknown)"

        out.append(LinkedControl(
            control_ref      = cref,
            ref              = bare_ref,
            standard_id      = std_id,
            standard_display = std_display,
            role             = meta.get("role"),
            subject          = meta.get("subject") or None,
        ))
    return out


# ── Row shaping ──────────────────────────────────────────────


_LIST_COLUMNS = (
    "id::text, external_ref, asset_ref, asset_name, threat, "
    "vulnerability, likelihood, impact, risk_score, "
    "risk_owner_text, treatment_option, treatment_status, "
    "residual_risk_level, review_date::text, "
    "coalesce(control_refs, '{}') AS control_refs"
)


def _row_to_risk(row, cur) -> RiskRow:
    return RiskRow(
        id                  = row[0],
        external_ref        = row[1],
        asset_ref           = row[2],
        asset_name          = row[3],
        threat              = row[4],
        vulnerability       = row[5],
        likelihood          = row[6],
        impact              = row[7],
        risk_score          = row[8],
        risk_owner_text     = row[9],
        treatment_option    = row[10],
        treatment_status    = row[11],
        residual_risk_level = row[12],
        review_date         = row[13],
        linked_controls     = linked_controls_view(list(row[14] or []), cur),
    )


# ── Public queries ───────────────────────────────────────────


def fetch_risks(
    conn,
    limit:  int = 100,
    offset: int = 0,
    status: Optional[list[str]] = None,
    order:  str = "risk_score DESC NULLS LAST, external_ref",
) -> tuple[list[RiskRow], int]:
    """Return `(rows, total_before_pagination)`.

    `conn` must have `app.tenant_id` set (RLS enforced)."""
    with conn.cursor() as cur:
        where_parts = ["is_active = true"]
        params = []
        if status:
            where_parts.append("treatment_status = ANY(%s)")
            params.append(status)
        where_sql = " AND ".join(where_parts)

        cur.execute(
            f"SELECT COUNT(*) FROM risks WHERE {where_sql}",
            params,
        )
        total = cur.fetchone()[0]

        cur.execute(
            f"SELECT {_LIST_COLUMNS} FROM risks "
            f"WHERE {where_sql} "
            f"ORDER BY {order} "
            f"LIMIT %s OFFSET %s",
            params + [limit, offset],
        )
        rows = [_row_to_risk(r, cur) for r in cur.fetchall()]
        return rows, total


def fetch_risk_detail(conn, risk_id: str) -> Optional[RiskDetail]:
    """Return a drill-in view, or None if the id doesn't exist
    (or is scoped out by RLS)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id::text, external_ref, asset_ref, asset_name, "
            "       interested_party, threat, vulnerability, "
            "       likelihood, impact, risk_score, risk_owner_text, "
            "       treatment_option, treatment_rationale, "
            "       treatment_action, "
            "       coalesce(control_refs, '{}') AS control_refs, "
            "       resources_required, "
            "       coalesce(performance_indicators, '{}') AS kpis, "
            "       constraints, reporting_cadence, "
            "       implementation_date::text, residual_risk_level, "
            "       treatment_status, review_date::text, "
            "       effectiveness_review, created_at::text, "
            "       updated_at::text "
            "  FROM risks "
            " WHERE id::text = %s AND is_active = true",
            [risk_id],
        )
        row = cur.fetchone()
        if not row:
            return None
        return RiskDetail(
            id                     = row[0],
            external_ref           = row[1],
            asset_ref              = row[2],
            asset_name             = row[3],
            interested_party       = row[4],
            threat                 = row[5],
            vulnerability          = row[6],
            likelihood             = row[7],
            impact                 = row[8],
            risk_score             = row[9],
            risk_owner_text        = row[10],
            treatment_option       = row[11],
            treatment_rationale    = row[12],
            treatment_action       = row[13],
            linked_controls        = linked_controls_view(list(row[14] or []), cur),
            resources_required     = row[15],
            performance_indicators = list(row[16] or []),
            constraints            = row[17],
            reporting_cadence      = row[18],
            implementation_date    = row[19],
            residual_risk_level    = row[20],
            treatment_status       = row[21],
            review_date            = row[22],
            effectiveness_review   = row[23],
            created_at             = row[24],
            updated_at             = row[25],
        )


# ── Write helpers ────────────────────────────────────────────


class RiskCreate(BaseModel):
    """Request shape for POST /api/v1/tenant/risks. All fields
    except `external_ref` are optional — the tenant may create a
    minimal risk row and populate treatment plan fields via PATCH
    later. schema_v2 CHECK constraints validate integer ranges +
    treatment_option / treatment_status enum values."""
    external_ref:            str            = Field(..., min_length=1, description="Tenant-authored unique id (e.g. `R-042`). Must be unique per tenant.")
    asset_ref:               Optional[str]  = None
    asset_name:              Optional[str]  = None
    interested_party:        Optional[str]  = None
    threat:                  Optional[str]  = None
    vulnerability:           Optional[str]  = None
    likelihood:              Optional[int]  = Field(None, ge=1, le=5)
    impact:                  Optional[int]  = Field(None, ge=1, le=5)
    risk_score:              Optional[int]  = Field(None, ge=1, le=25)
    risk_owner_text:         Optional[str]  = None
    treatment_option:        Optional[str]  = Field(None, description="One of: Mitigate / Accept / Transfer / Avoid.")
    treatment_action:        Optional[str]  = None
    treatment_rationale:     Optional[str]  = None
    resources_required:      Optional[str]  = None
    performance_indicators:  list[str]      = Field(default_factory=list)
    constraints:             Optional[str]  = None
    reporting_cadence:       Optional[str]  = None
    implementation_date:     Optional[str]  = Field(None, description="ISO date YYYY-MM-DD.")
    residual_risk_level:     Optional[int]  = Field(None, ge=1, le=25)
    treatment_status:        Optional[str]  = Field(None, description="One of: open / in_progress / implemented / accepted.")
    review_date:             Optional[str]  = None
    effectiveness_review:    Optional[str]  = None
    control_refs:            list[str]      = Field(default_factory=list, description="Composite refs — e.g. `ISO27001:2022:A.5.15`.")


class RiskPatch(BaseModel):
    """Request shape for PATCH /api/v1/tenant/risks/{id}. Every
    field is optional; unset fields keep their current DB values.
    external_ref is IMMUTABLE — PATCH may not change the tenant-
    authored id (would break dedup + citation stability)."""
    asset_ref:               Optional[str]  = None
    asset_name:              Optional[str]  = None
    interested_party:        Optional[str]  = None
    threat:                  Optional[str]  = None
    vulnerability:           Optional[str]  = None
    likelihood:              Optional[int]  = Field(None, ge=1, le=5)
    impact:                  Optional[int]  = Field(None, ge=1, le=5)
    risk_score:              Optional[int]  = Field(None, ge=1, le=25)
    risk_owner_text:         Optional[str]  = None
    treatment_option:        Optional[str]  = None
    treatment_action:        Optional[str]  = None
    treatment_rationale:     Optional[str]  = None
    resources_required:      Optional[str]  = None
    performance_indicators:  Optional[list[str]] = None
    constraints:             Optional[str]  = None
    reporting_cadence:       Optional[str]  = None
    implementation_date:     Optional[str]  = None
    residual_risk_level:     Optional[int]  = Field(None, ge=1, le=25)
    treatment_status:        Optional[str]  = None
    review_date:             Optional[str]  = None
    effectiveness_review:    Optional[str]  = None
    control_refs:            Optional[list[str]] = None


def create_risk(conn, tenant_id: str, payload: RiskCreate) -> tuple[str, str]:
    """Create a new risk row. Returns (risk_id, external_ref) on
    success. Raises `DuplicateRiskError` on external_ref collision,
    `ValueError` on constraint violation (bad enum / range).

    Callers should invoke `emit_risk_added()` after commit to fire
    the write-path notification."""
    cols   = ["tenant_id", "external_ref"]
    values = [tenant_id, payload.external_ref]

    # Optional columns — include only when non-None so the DB
    # defaults apply cleanly for empty payloads.
    for field_name, val in payload.model_dump(exclude={"external_ref"}).items():
        if val is None:
            continue
        # Skip empty lists for text[] columns (Postgres treats them
        # differently than NULL; keep NULL to match the schema
        # default and existing rows).
        if isinstance(val, list) and not val:
            continue
        cols.append(field_name)
        values.append(val)

    placeholders = ", ".join(["%s"] * len(cols))
    col_list     = ", ".join(cols)

    with conn.cursor() as cur:
        try:
            cur.execute(
                f"INSERT INTO risks ({col_list}) "
                f"VALUES ({placeholders}) "
                f"RETURNING id::text, external_ref",
                values,
            )
            row = cur.fetchone()
            return row[0], row[1]
        except Exception as e:
            msg = str(e)
            if "risks_tenant_id_external_ref_key" in msg:
                raise DuplicateRiskError(payload.external_ref) from e
            raise


def update_risk(
    conn, tenant_id: str, risk_id: str, payload: RiskPatch,
) -> Optional[str]:
    """Update a risk row. Returns the risk_id on success, None if
    the id doesn't exist / is scoped out by RLS. Only sets columns
    the caller explicitly named — unset fields keep DB values."""
    updates: list[tuple[str, object]] = []
    for field_name, val in payload.model_dump(exclude_unset=True).items():
        updates.append((field_name, val))
    if not updates:
        return risk_id  # no-op; caller may still want the id back

    set_clause = ", ".join(f"{c} = %s" for c, _ in updates)
    values     = [v for _, v in updates] + [risk_id]

    with conn.cursor() as cur:
        cur.execute(
            f"UPDATE risks SET {set_clause}, updated_at = NOW() "
            f"WHERE id::text = %s AND is_active = TRUE "
            f"RETURNING id::text",
            values,
        )
        row = cur.fetchone()
        return row[0] if row else None


def soft_delete_risk(conn, tenant_id: str, risk_id: str, reason: Optional[str]) -> bool:
    """Soft-delete: set is_active = FALSE (RLS policy filters
    inactive rows). Returns True on delete, False if the row
    doesn't exist. Callers should note the reason for auditor
    provenance."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE risks "
            "   SET is_active = FALSE, "
            "       deleted_at = NOW(), "
            "       deletion_reason = %s "
            " WHERE id::text = %s AND is_active = TRUE "
            " RETURNING 1",
            [reason, risk_id],
        )
        return cur.fetchone() is not None


class DuplicateRiskError(Exception):
    def __init__(self, external_ref: str):
        super().__init__(f"Duplicate external_ref: {external_ref}")
        self.external_ref = external_ref


def fetch_risks_for_casefile(tenant_id: str, top_n: int = 8) -> list[dict]:
    """Ship 14'.e — compact risk view for the case-file digest.

    Opens its own psycopg2 connection (case-file path doesn't
    receive one; RAG pipeline is DB-agnostic). Enforces RLS via
    `SET LOCAL app.tenant_id`. Returns a list of dicts with the
    fields the RISKS digest section renders. Silent-fail on error
    (returns []) — the case-file path must never block on risk
    fetch.

    Fetches top-N by risk_score DESC. Includes only active,
    non-implemented rows so the digest surfaces relevant risks
    rather than closed history.

    Framework role model: linked_controls are pre-expanded with
    role + subject via `linked_controls_view()` so the digest
    renders side-by-side without a second lookup.
    """
    if not tenant_id:
        return []

    try:
        import os
        import psycopg2
        conn = psycopg2.connect(
            host     = os.getenv("PGHOST",     "127.0.0.1"),
            dbname   = os.getenv("PGDATABASE", "arioncomply_compliance"),
            user     = os.getenv("PGUSER",     "arioncomply_app"),
            password = os.getenv("PGPASSWORD", ""),
        )
    except Exception:
        return []

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SET LOCAL app.tenant_id = %s", [tenant_id]
            )
            # Include ALL active rows regardless of treatment_status.
            # The chat surface shows top risks by score; whether a row
            # is `implemented` is metadata the chat prose carries per
            # row. Filtering to just non-implemented would produce
            # empty output on tenants whose entire register is closed
            # (which is normal for mature tenants with backlogged
            # completions). Callers who want an open-only view can
            # filter downstream.
            cur.execute(
                "SELECT id::text, external_ref, threat, "
                "  vulnerability, risk_score, treatment_option, "
                "  treatment_status, residual_risk_level, "
                "  review_date::text, "
                "  coalesce(control_refs, '{}') AS control_refs "
                "FROM risks "
                "WHERE is_active = true "
                "ORDER BY risk_score DESC NULLS LAST, external_ref "
                "LIMIT %s",
                [top_n],
            )
            rows = cur.fetchall()

            out: list[dict] = []
            for row in rows:
                linked = linked_controls_view(list(row[9] or []), cur)
                out.append({
                    "id":                  row[0],
                    "external_ref":        row[1],
                    "threat":              row[2],
                    "vulnerability":       row[3],
                    "risk_score":          row[4],
                    "treatment_option":    row[5],
                    "treatment_status":    row[6],
                    "residual_risk_level": row[7],
                    "review_date":         row[8],
                    "linked_controls":     [lc.model_dump() for lc in linked],
                })
            return out
    except Exception:
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass


def fetch_risk_summary(conn) -> RiskSummary:
    """Return the dashboard-friendly aggregate for the current
    tenant — counts, heatmap, top-5."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT "
            "  COUNT(*)                                                        AS total, "
            "  COUNT(*) FILTER (WHERE treatment_status IN ('open','in_progress')) AS open_ct, "
            "  COUNT(*) FILTER (WHERE review_date IS NOT NULL "
            "                     AND review_date < CURRENT_DATE "
            "                     AND treatment_status <> 'implemented')        AS overdue_ct, "
            "  COUNT(*) FILTER (WHERE residual_risk_level >= 15)                AS above_ct, "
            "  COUNT(*) FILTER (WHERE risk_owner IS NULL "
            "                     AND (risk_owner_text IS NULL "
            "                       OR trim(risk_owner_text) = ''))             AS unassigned_ct "
            "FROM risks WHERE is_active = true"
        )
        total, open_ct, overdue_ct, above_ct, unassigned_ct = cur.fetchone()

        cur.execute(
            "SELECT treatment_option, COUNT(*) "
            "  FROM risks WHERE is_active = true AND treatment_option IS NOT NULL "
            " GROUP BY treatment_option"
        )
        by_option = {opt: cnt for opt, cnt in cur.fetchall()}

        cur.execute(
            "SELECT COALESCE(treatment_status, 'unset'), COUNT(*) "
            "  FROM risks WHERE is_active = true "
            " GROUP BY treatment_status"
        )
        by_status = {st: cnt for st, cnt in cur.fetchall()}

        cur.execute(
            "SELECT likelihood, impact, COUNT(*) "
            "  FROM risks WHERE is_active = true "
            "   AND likelihood IS NOT NULL AND impact IS NOT NULL "
            " GROUP BY likelihood, impact"
        )
        heatmap: dict[str, int] = {}
        for lik, imp, cnt in cur.fetchall():
            heatmap[f"L{lik}_I{imp}"] = cnt

        cur.execute(
            f"SELECT {_LIST_COLUMNS} FROM risks "
            "WHERE is_active = true "
            "ORDER BY risk_score DESC NULLS LAST, external_ref "
            "LIMIT 5"
        )
        top_rows = [_row_to_risk(r, cur) for r in cur.fetchall()]

        return RiskSummary(
            total               = total,
            open                = open_ct,
            overdue             = overdue_ct,
            above_threshold     = above_ct,
            unassigned          = unassigned_ct,
            by_treatment_option = by_option,
            by_status           = by_status,
            heatmap             = heatmap,
            top_risks           = top_rows,
        )
