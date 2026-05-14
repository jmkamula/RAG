"""
ArionComply — Posture Loader

Reads tenant posture from Postgres posture_controls table.
Replaces the ARION_POSTURE hardcode in chat.py.

Returns the same dict format the pipeline expects:
  {
    "ISO27001:2022:A.5.18": {
      "finding":         "NC",
      "gap_description": "Access register records from Q4 2024 incomplete",
      "action_required": "Complete and sign off Q4 2024 access register",
      "source":          "assessor",
      "source_authority":"Arion Networks Internal Audit (AUD001, April 2025)",
      "platform_ref":    "PC-ARN-0105",
      "external_ref":    "F001/F005",
      "confidence":      "high",
    },
    ...
  }

Also loads ClientFacts from Postgres client_facts table,
replacing the ARION_FACTS hardcode.

Usage:
  from rag.posture_loader import load_posture, load_client_facts

  posture = load_posture(pg_conn, tenant_id)
  facts   = load_client_facts(pg_conn, tenant_id)
"""
from __future__ import annotations
import os
import logging

logger = logging.getLogger(__name__)


def load_posture(pg_conn, tenant_id: str) -> dict:
    """
    Load all assessed posture controls for a tenant from Postgres.

    Returns dict keyed by node_id (e.g. "ISO27001:2022:A.5.18"):
      {finding, gap_description, action_required, source,
       source_authority, platform_ref, external_ref, confidence,
       remediation_status, soa_notes}

    Only returns rows where finding is not 'Not assessed' —
    unassessed controls have no posture data to provide.

    N/A controls ARE included (source='workbook', finding='N/A')
    so the pipeline can correctly exclude them from obligation checks.
    """
    try:
        with pg_conn.cursor() as cur:
            # Set tenant context for RLS enforcement
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute("""
                SELECT
                    COALESCE(node_id, standard_id || ':' || control_ref) AS node_id,
                    control_ref,
                    standard_id,
                    finding,
                    confidence,
                    gap_description,
                    action_required,
                    source,
                    source_authority,
                    platform_ref,
                    external_ref,
                    soa_notes,
                    remediation_status,
                    linked_policies,
                    last_updated
                FROM posture_controls
                WHERE tenant_id = %s
                  AND finding != 'Not assessed'
                  AND control_ref IS NOT NULL
                ORDER BY
                    CASE finding
                        WHEN 'NC'     THEN 1
                        WHEN 'OFI'    THEN 2
                        WHEN 'Comply' THEN 3
                        WHEN 'N/A'    THEN 4
                        ELSE 5
                    END,
                    control_ref
            """, (tenant_id,))

            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]

    except Exception as e:
        logger.error(f"load_posture failed for {tenant_id}: {e}")
        return {}

    posture = {}
    for row in rows:
        rec = dict(zip(cols, row))
        nid = rec.pop("node_id")
        if nid:
            posture[nid] = rec

    logger.info(
        f"load_posture: {len(posture)} controls loaded for {tenant_id} "
        f"({sum(1 for r in posture.values() if r['finding']=='NC')} NC, "
        f"{sum(1 for r in posture.values() if r['finding']=='OFI')} OFI, "
        f"{sum(1 for r in posture.values() if r['finding']=='Comply')} Comply, "
        f"{sum(1 for r in posture.values() if r['finding']=='N/A')} N/A)"
    )
    return posture


def load_client_facts(pg_conn, tenant_id: str):
    """
    Load ClientFacts for a tenant from Postgres client_facts table.
    Returns a ClientFacts dataclass instance.
    Falls back to safe defaults if row not found.
    """
    from enrichment.obligations.client_facts import ClientFacts

    defaults = {
        "sector":                   "technology",
        "processes_personal_data":  True,
        "eu_data_subjects":         True,
        "role_controller":          True,
        "role_processor":           False,
        "special_category_data":    False,
        "childrens_data":           False,
        "develops_software":        False,
        "uses_cloud_services":      True,
        "uses_processors":          True,
        "has_remote_workers":       True,
        "has_physical_premises":    False,
        "large_scale_processing":   False,
        "high_risk_processing":     False,
        "transfers_data_outside_eu":False,
        "collected_via":            "workbook",
    }

    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute("""
                SELECT
                    sector,
                    processes_personal_data,
                    eu_data_subjects,
                    role_controller,
                    role_processor,
                    special_category_data,
                    childrens_data,
                    develops_software,
                    uses_cloud_services,
                    uses_processors,
                    has_remote_workers,
                    has_physical_premises,
                    large_scale_processing,
                    high_risk_processing,
                    transfers_data_outside_eu,
                    collected_via
                FROM client_facts
                WHERE tenant_id = %s
                LIMIT 1
            """, (tenant_id,))
            row = cur.fetchone()

            if row:
                cols = [d[0] for d in cur.description]
                db_facts = dict(zip(cols, row))
                # Merge DB values over defaults (DB wins for non-None values)
                for k, v in db_facts.items():
                    if v is not None and k in defaults:
                        defaults[k] = v

    except Exception as e:
        logger.warning(f"load_client_facts failed for {tenant_id}: {e} — using defaults")
        try:
            pg_conn.rollback()  # Reset transaction so subsequent queries work
        except Exception:
            pass

    # Map DB column names to ClientFacts field names
    field_map = {
        "processes_personal_data":  "processes_pii",
        "childrens_data":           "processes_children_data",
        "role_controller":          None,   # handled below
        "role_processor":           None,   # handled below
    }

    # Derive role string from boolean flags
    if defaults.get("role_controller") and defaults.get("role_processor"):
        role = "both"
    elif defaults.get("role_processor"):
        role = "processor"
    else:
        role = "controller"

    # Build kwargs for ClientFacts — only include known fields
    kwargs = {"role": role}
    skip = {"role_controller", "role_processor", "collected_via"}
    for k, v in defaults.items():
        if k in skip:
            continue
        mapped = field_map.get(k, k)
        if mapped is None:
            continue
        if mapped in ClientFacts.__dataclass_fields__:
            kwargs[mapped] = v
        elif k in ClientFacts.__dataclass_fields__:
            kwargs[k] = v

    return ClientFacts(**{k: v for k, v in kwargs.items()
                         if k in ClientFacts.__dataclass_fields__})


def _load_db_url() -> str:
    """Load DATABASE_URL from env or .env file."""
    from pathlib import Path
    if not os.getenv("DATABASE_URL"):
        try:
            from dotenv import load_dotenv
            here = Path(__file__).resolve().parent
            for candidate in [here, here.parent, here.parent.parent]:
                env_file = candidate / ".env"
                if env_file.exists():
                    load_dotenv(env_file)
                    logger.info(f"Loaded .env from {env_file}")
                    break
        except ImportError:
            pass
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL not set. Add to .env:\n"
            "  DATABASE_URL=postgresql://arioncomply_app:password"
            "@localhost/arioncomply_compliance"
        )
    return url


def build_pg_conn():
    """
    Build a single Postgres connection. Use for one-off operations.
    For concurrent/multi-request use, prefer build_pg_pool().
    """
    import psycopg2
    return psycopg2.connect(_load_db_url())


def build_pg_pool(minconn: int = 2, maxconn: int = 10):
    """
    Build a psycopg2 connection pool for concurrent use.
    Suitable for multi-tenant SaaS with concurrent users.

    Usage:
        pool = build_pg_pool()
        conn = pool.getconn()
        try:
            # use conn
        finally:
            pool.putconn(conn)

    Or use as context manager with the helper:
        with pool_conn(pool) as conn:
            # use conn
    """
    from psycopg2 import pool as pg_pool
    return pg_pool.SimpleConnectionPool(
        minconn = minconn,
        maxconn = maxconn,
        dsn     = _load_db_url(),
    )


class pool_conn:
    """
    Context manager for clean connection pool usage.

    with pool_conn(pool) as conn:
        do_something(conn)
    """
    def __init__(self, pool):
        self._pool = pool
        self._conn = None

    def __enter__(self):
        self._conn = self._pool.getconn()
        return self._conn

    def __exit__(self, *_):
        if self._conn:
            self._pool.putconn(self._conn)
            self._conn = None


def load_document_alerts(pg_conn, tenant_id: str) -> list[dict]:
    """
    Load document alerts for the tenant — missing files, overdue reviews.
    Used by the pipeline to surface document gaps in answers.
    Returns list of alert dicts ordered by severity.
    """
    try:
        with pg_conn.cursor() as cur:
            # Set RLS context — view enforces isolation via base table RLS
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute("""
                SELECT
                    platform_ref, external_ref, document_title,
                    document_status, alert_type, alert_message,
                    linked_controls, linked_control_refs,
                    linked_findings, worst_finding_score
                FROM document_alerts
                WHERE alert_type IN ('CRITICAL', 'WARNING', 'INFO')
                ORDER BY worst_finding_score NULLS LAST, document_title
            """)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        logger.warning(f"load_document_alerts failed: {e}")
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return []


def load_uploaded_documents(pg_conn, tenant_id: str) -> list[dict]:
    """
    Load documents the tenant has actually delivered, from client_documents.
    Source of truth is client_documents.document_status — the intake pipeline
    transitions it to 'uploaded' once a file is processed against a registered
    entry. document_uploads is an audit log; document_status is the state.

    Used to answer "which documents have we uploaded / submitted" (positive
    polarity); contrast with load_document_alerts which lists registered-but-
    missing docs (document_status='registered').
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            # control_refs is read LIVE from document_findings rather than the
            # cached client_documents.control_refs column. Reason: as new
            # extractors (ISO 27701, GDPR) start writing findings against
            # already-uploaded docs, those new frameworks must surface
            # automatically without re-running intake. The cached column is
            # still populated by intake as a fast-path / fallback.
            cur.execute("""
                SELECT
                    cd.id::text          AS doc_id,
                    cd.platform_ref,
                    cd.external_ref,
                    cd.document_title,
                    cd.filename,
                    cd.document_type     AS doc_type,
                    cd.document_status,
                    cd.uploaded_at::text,
                    cd.page_count,
                    cd.file_size_bytes,
                    cd.mime_type,
                    COALESCE(
                        (
                            SELECT array_agg(s_ref ORDER BY s_ref)
                            FROM (
                                SELECT DISTINCT
                                    df.standard_id || ':' || df.control_ref AS s_ref
                                FROM document_findings df
                                WHERE df.document_id = cd.id
                                  AND df.tenant_id   = cd.tenant_id
                                  AND df.is_active   = TRUE
                            ) sub
                        ),
                        -- Fallback: if findings haven't been written yet,
                        -- the cached column already holds fully-qualified
                        -- STANDARD:VERSION:REF entries (intake writes them
                        -- that way). No framework guesswork here.
                        cd.control_refs
                    ) AS framework_refs
                FROM client_documents cd
                WHERE cd.tenant_id       = %s::uuid
                  AND cd.is_active       = TRUE
                  AND cd.document_status IN ('uploaded', 'processing', 'active')
                ORDER BY cd.uploaded_at DESC NULLS LAST, cd.document_title NULLS LAST
            """, (tenant_id,))
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        logger.warning(f"load_uploaded_documents failed: {e}")
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return []


def load_tenant_context(pg_conn, tenant_id: str) -> dict:
    """
    Load all tenant context in one call:
      posture            — dict of assessed controls
      facts              — ClientFacts dataclass
      scope              — TenantScope (standards + relationships)
      document_alerts    — list of missing/overdue document alerts
      uploaded_documents — list of files actually uploaded to the platform

    Used by chat.py on startup to replace all hardcodes.
    """
    from rag.scope_loader import load_tenant_scope

    posture            = load_posture(pg_conn, tenant_id)
    facts              = load_client_facts(pg_conn, tenant_id)
    scope              = load_tenant_scope(pg_conn, tenant_id)
    document_alerts    = load_document_alerts(pg_conn, tenant_id)
    uploaded_documents = load_uploaded_documents(pg_conn, tenant_id)

    critical = sum(1 for a in document_alerts if a.get("alert_type") == "CRITICAL")
    warning  = sum(1 for a in document_alerts if a.get("alert_type") == "WARNING")

    logger.info(
        f"Tenant context loaded: {len(posture)} posture controls, "
        f"queryable={scope.queryable_standards}, "
        f"gdpr_evaluable={scope.can_evaluate_gdpr}, "
        f"doc_alerts={len(document_alerts)} ({critical} critical, {warning} warning), "
        f"uploaded={len(uploaded_documents)}"
    )
    return {
        "posture":            posture,
        "facts":              facts,
        "scope":              scope,
        "document_alerts":    document_alerts,
        "uploaded_documents": uploaded_documents,
    }
