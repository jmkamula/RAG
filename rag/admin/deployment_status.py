"""Deployment status probe — Ship 48'.c.

Collects non-sensitive, aggregate telemetry about a running ArionComply
install. Serves /api/v1/admin/deployment/status.

Privacy contract: NEVER returns tenant names / user emails / evidence
text / posture descriptions / raw API keys. Only counts, versions,
health flags, and framework identifiers (which are public compliance
vocabulary, not secrets).

Cross-references the diagnostic bundle (scripts/ops/diagnose.sh) —
the endpoint is the live variant, the bundle is the offline variant.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any


_ARION_ROOT = Path(os.environ.get("ARION_ROOT", "/data/arioncomply"))


def _git_sha() -> str | None:
    """Short git SHA of the running codebase. None if not a git checkout."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(_ARION_ROOT), "rev-parse", "--short=8", "HEAD"],
            stderr=subprocess.DEVNULL, timeout=2,
        )
        return out.decode().strip() or None
    except Exception:
        return None


def _arion_version() -> str:
    """ArionComply version string. Reads deploy/VERSION if present, else
    falls back to git SHA, else '0.0.0-dev'."""
    version_file = _ARION_ROOT / "deploy" / "VERSION"
    if version_file.exists():
        try:
            return version_file.read_text().strip()
        except Exception:
            pass
    sha = _git_sha()
    return f"git-{sha}" if sha else "0.0.0-dev"


def _postgres_status(pool) -> dict[str, Any]:
    """Compliance + sessions DB size, connection count, extensions.
    Non-fatal — degraded fields become None on error."""
    out: dict[str, Any] = {
        "compliance_size_mb": None,
        "sessions_size_mb":   None,
        "connection_count":   None,
        "extensions":         [],
        "reachable":          False,
    }
    if pool is None:
        return out
    try:
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_database_size(current_database())")
                out["compliance_size_mb"] = int(cur.fetchone()[0] / (1024 * 1024))
                cur.execute("SELECT count(*) FROM pg_stat_activity")
                out["connection_count"] = int(cur.fetchone()[0])
                cur.execute("SELECT extname FROM pg_extension ORDER BY extname")
                out["extensions"] = [r[0] for r in cur.fetchall()]
                out["reachable"] = True
        finally:
            pool.putconn(conn)
    except Exception:
        pass

    # Sessions DB is on a separate DSN — probe with a fresh psycopg2 conn.
    sessions_dsn = os.environ.get("SESSIONS_DATABASE_URL")
    if sessions_dsn:
        try:
            import psycopg2
            with psycopg2.connect(sessions_dsn, connect_timeout=2) as s_conn:
                with s_conn.cursor() as cur:
                    cur.execute("SELECT pg_database_size(current_database())")
                    out["sessions_size_mb"] = int(cur.fetchone()[0] / (1024 * 1024))
        except Exception:
            pass
    return out


def _neo4j_status() -> dict[str, Any]:
    """Node + edge counts on the requirement graph. Non-fatal."""
    out: dict[str, Any] = {
        "requirement_nodes": None,
        "checklist_items":   None,
        "bridges":           None,
        "reachable":         False,
    }
    uri = os.environ.get("NEO4J_URI") or "bolt://127.0.0.1:7687"
    user = os.environ.get("NEO4J_USER") or "neo4j"
    pw = os.environ.get("NEO4J_PASSWORD")
    if not pw:
        return out
    try:
        from neo4j import GraphDatabase
        d = GraphDatabase.driver(uri, auth=(user, pw))
        with d.session() as s:
            out["requirement_nodes"] = s.run(
                "MATCH (n:RequirementNode) RETURN count(n) AS c"
            ).single()["c"]
            out["checklist_items"] = s.run(
                "MATCH (n:ChecklistItem) RETURN count(n) AS c"
            ).single()["c"]
            # Count bridge edges — union of IMPLEMENTS / SUPPORTS /
            # DEMONSTRATES / GOVERNANCE / ENABLES.
            out["bridges"] = s.run(
                "MATCH ()-[e]->() "
                "WHERE type(e) IN ['IMPLEMENTS','SUPPORTS','DEMONSTRATES','GOVERNANCE','ENABLES'] "
                "RETURN count(e) AS c"
            ).single()["c"]
            out["reachable"] = True
        d.close()
    except Exception:
        pass
    return out


def _chroma_status() -> dict[str, Any]:
    """Collection count + total docs across all collections. Non-fatal."""
    out: dict[str, Any] = {
        "collections": None,
        "total_docs":  None,
        "reachable":   False,
    }
    host = os.environ.get("CHROMA_HOST") or "127.0.0.1"
    port = int(os.environ.get("CHROMA_PORT") or "8000")
    try:
        import chromadb
        c = chromadb.HttpClient(host=host, port=port)
        cols = c.list_collections()
        out["collections"] = len(cols)
        total = 0
        for col in cols:
            try:
                total += col.count()
            except Exception:
                pass
        out["total_docs"] = total
        out["reachable"] = True
    except Exception:
        pass
    return out


def _tenant_summary(pool) -> dict[str, Any]:
    """Aggregate counts only. No tenant names, no user emails.

    Counts distinct tenant_id from posture_controls (proxy for
    "onboarded tenants" — a tenant with zero posture rows won't be
    counted). Chosen over `SELECT count(*) FROM tenants` because that
    table has RLS restrictions the app pool role can't bypass; the
    proxy metric is more portable and still meaningful.
    """
    out: dict[str, Any] = {
        "count":      None,
        "frameworks": [],
    }
    if pool is None:
        return out
    try:
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT count(DISTINCT tenant_id) FROM posture_controls "
                    "WHERE is_active = TRUE"
                )
                out["count"] = int(cur.fetchone()[0])
                cur.execute(
                    "SELECT DISTINCT standard_id "
                    "FROM posture_controls "
                    "WHERE is_active = TRUE "
                    "ORDER BY standard_id"
                )
                out["frameworks"] = [r[0] for r in cur.fetchall()]
        finally:
            pool.putconn(conn)
    except Exception:
        pass
    return out


def _feature_flags() -> dict[str, Any]:
    """Snapshot of runtime feature flags. Booleans only."""
    return {
        "consensus_extraction": os.environ.get("USE_CONSENSUS_EXTRACTION") == "1",
        "otel_enabled":         os.environ.get("OTEL_ENABLED") == "1",
        "privacy_level":        os.environ.get("OTEL_PRIVACY_LEVEL") or "unknown",
    }


def collect(pg_pool, started_at: float) -> dict[str, Any]:
    """Assemble the full deployment status payload.

    started_at: time.time() captured at app startup (from app.state).
    pg_pool:    the shared psycopg2 pool (nullable).
    """
    now = time.time()
    services = {
        "api":      "healthy",
        "postgres": None,
        "neo4j":    None,
        "chroma":   None,
    }

    pg = _postgres_status(pg_pool)
    services["postgres"] = "healthy" if pg["reachable"] else "unreachable"

    neo = _neo4j_status()
    services["neo4j"] = "healthy" if neo["reachable"] else "unreachable"

    chr_ = _chroma_status()
    services["chroma"] = "healthy" if chr_["reachable"] else "unreachable"

    return {
        "arion_version":  _arion_version(),
        "git_sha":        _git_sha(),
        "started_at":     int(started_at),
        "uptime_sec":     int(now - started_at) if started_at else None,
        "services":       services,
        "postgres":       {k: v for k, v in pg.items() if k != "reachable"},
        "neo4j":          {k: v for k, v in neo.items() if k != "reachable"},
        "chroma":         {k: v for k, v in chr_.items() if k != "reachable"},
        "tenants":        _tenant_summary(pg_pool),
        "features":       _feature_flags(),
    }
