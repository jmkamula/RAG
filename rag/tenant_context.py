"""
ArionComply — TenantContextCache

Replaces module-level globals (ARION_POSTURE, ARION_DOC_ALERTS etc.) in chat.py
with a request-scoped, TTL-cached, thread-safe tenant context.

Design:
  - One TenantContextCache instance per process (singleton)
  - load(tenant_id) returns TenantContext, refreshing if TTL expired
  - Each request gets a snapshot — no shared mutable state
  - Cache invalidation via invalidate(tenant_id) when posture changes
  - Thread-safe via threading.Lock per tenant slot

Multi-tenant flow:
  1. API request arrives with JWT containing tenant_id
  2. Pipeline calls cache.load(tenant_id)
  3. Cache returns TenantContext (from cache or fresh from DB)
  4. Pipeline uses context.profile, context.posture, context.alerts
  5. No globals, no cross-tenant contamination

Single-tenant (current Arion dev):
  cache = TenantContextCache.from_env()
  ctx   = cache.load("00000000-0000-0000-0000-000000000001")
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Cache TTL in seconds — how long before we re-query Postgres
# 60s is a good default: fresh enough for real-time posture, 
# cheap enough for concurrent users
DEFAULT_TTL_SECONDS = 60


@dataclass
class TenantContext:
    """
    Everything the pipeline needs about one tenant.
    Immutable snapshot — safe to share across threads for its TTL lifetime.
    Replaces: ARION_POSTURE, ARION_FACTS_DB, ARION_SCOPE, ARION_DOC_ALERTS globals
    """
    tenant_id:       str
    profile:         object          # TenantProfile (classifier.py)
    posture:         dict            # {node_id: {finding, gap, control_ref, ...}}
    facts:           object          # ClientFacts dataclass
    scope:           object          # TenantScope dataclass
    document_alerts: list            # [{platform_ref, document_title, alert_type, ...}]
    loaded_at:       float           # time.time() when loaded
    ttl_seconds:     int = DEFAULT_TTL_SECONDS

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.loaded_at) > self.ttl_seconds

    @property
    def age_seconds(self) -> int:
        return int(time.time() - self.loaded_at)

    def summary(self) -> str:
        nc  = sum(1 for v in self.posture.values() if v.get("finding") == "NC")
        ofi = sum(1 for v in self.posture.values() if v.get("finding") == "OFI")
        crit = sum(1 for a in self.document_alerts
                   if a.get("alert_type") == "CRITICAL")
        warn = sum(1 for a in self.document_alerts
                   if a.get("alert_type") == "WARNING")
        return (
            f"tenant={self.tenant_id[:8]}... "
            f"posture={len(self.posture)} controls ({nc} NC, {ofi} OFI) "
            f"docs={len(self.document_alerts)} alerts ({crit} critical, {warn} warning) "
            f"age={self.age_seconds}s"
        )


class TenantContextCache:
    """
    Process-level singleton cache for tenant context.
    Thread-safe: one lock per tenant slot, no global lock on reads.

    Usage:
        # At process startup (once)
        cache = TenantContextCache(build_pg_conn)

        # Per request
        ctx = cache.load(tenant_id)
        pipeline.run(query, tenant_context=ctx)

        # After posture update
        cache.invalidate(tenant_id)
    """

    def __init__(
        self,
        pg_conn_factory,            # callable → psycopg2 connection
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ):
        self._factory    = pg_conn_factory
        self._ttl        = ttl_seconds
        self._cache:   dict[str, TenantContext] = {}
        self._locks:   dict[str, threading.Lock] = {}
        self._meta_lock = threading.Lock()   # protects _cache and _locks dicts

    # ── Public API ────────────────────────────────────────────────────────────

    def load(self, tenant_id: str) -> TenantContext:
        """
        Return TenantContext for tenant_id.
        Returns cached version if within TTL, otherwise refreshes from DB.
        Thread-safe: concurrent requests for the same tenant_id will not
        trigger duplicate DB queries (one waits, one loads).
        """
        lock = self._get_lock(tenant_id)

        with lock:
            cached = self._cache.get(tenant_id)
            if cached and not cached.is_expired:
                logger.debug(f"cache hit: {tenant_id[:8]} (age={cached.age_seconds}s)")
                return cached

            logger.info(f"cache miss: {tenant_id[:8]} — loading from DB")
            ctx = self._load_from_db(tenant_id)
            self._cache[tenant_id] = ctx
            return ctx

    def invalidate(self, tenant_id: str) -> None:
        """
        Force cache invalidation for a tenant.
        Call this when posture, documents, or standards change.
        Next load() will fetch fresh from DB.
        """
        lock = self._get_lock(tenant_id)
        with lock:
            self._cache.pop(tenant_id, None)
        logger.info(f"cache invalidated: {tenant_id[:8]}")

    def invalidate_all(self) -> None:
        """Invalidate all cached tenants. Use after bulk data changes."""
        with self._meta_lock:
            self._cache.clear()
        logger.info("cache invalidated: all tenants")

    def status(self) -> list[dict]:
        """Return cache status for all loaded tenants (for /debug endpoint)."""
        with self._meta_lock:
            return [
                {
                    "tenant_id":   tid,
                    "age_seconds": ctx.age_seconds,
                    "expired":     ctx.is_expired,
                    "summary":     ctx.summary(),
                }
                for tid, ctx in self._cache.items()
            ]

    # ── Private ───────────────────────────────────────────────────────────────

    def _get_lock(self, tenant_id: str) -> threading.Lock:
        """Get or create a per-tenant lock. Meta-lock protects the dict."""
        with self._meta_lock:
            if tenant_id not in self._locks:
                self._locks[tenant_id] = threading.Lock()
            return self._locks[tenant_id]

    def _load_from_db(self, tenant_id: str) -> TenantContext:
        """
        Load fresh tenant context from Postgres.
        Builds TenantProfile with all fields populated.
        """
        from rag.posture_loader import load_tenant_context
        from rag.classifier import TenantProfile

        pg = self._factory()
        try:
            ctx_data = load_tenant_context(pg, tenant_id)
        finally:
            pg.close()

        posture            = ctx_data["posture"]
        facts              = ctx_data["facts"]
        scope              = ctx_data["scope"]
        document_alerts    = ctx_data["document_alerts"]
        uploaded_documents = ctx_data.get("uploaded_documents", [])

        # Build TenantProfile with all context fields
        # ClientFacts has sector, role booleans — no company_name field
        tenant_name = tenant_id  # will be overridden by tenants table later
        if facts:
            # Use sector as a proxy for name in dev; real name from tenants table
            tenant_name = getattr(facts, "company_name", None) or "Arion Networks"

        profile = TenantProfile(
            tenant_id            = tenant_id,
            name                 = tenant_name,
            applicable_standards = (
                scope.queryable_standards if scope else ["ISO27001:2022"]
            ),
            role                 = _derive_roles(facts),
            sector               = getattr(facts, "sector", "technology") if facts else "technology",
            jurisdiction         = _derive_jurisdiction(facts),
            has_posture_data     = bool(posture),
            posture_summary      = {
                k: {"finding": v.get("finding")}
                for k, v in posture.items()
            },
            facts                = facts,
            posture_data         = posture,
            document_alerts      = document_alerts,
            uploaded_documents   = uploaded_documents,
        )

        return TenantContext(
            tenant_id       = tenant_id,
            profile         = profile,
            posture         = posture,
            facts           = facts,
            scope           = scope,
            document_alerts = document_alerts,
            loaded_at       = time.time(),
            ttl_seconds     = self._ttl,
        )

    # ── Class-level factory methods ───────────────────────────────────────────

    @classmethod
    def from_env(cls, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> "TenantContextCache":
        """
        Create a TenantContextCache using the DATABASE_URL from environment.
        Convenience method for single-process startup.

        Usage:
            cache = TenantContextCache.from_env()
        """
        from rag.posture_loader import build_pg_conn
        return cls(pg_conn_factory=build_pg_conn, ttl_seconds=ttl_seconds)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _derive_roles(facts) -> list[str]:
    """Derive controller/processor roles from ClientFacts.
    ClientFacts uses role_controller / role_processor boolean fields.
    """
    if facts is None:
        return ["controller"]
    roles = []
    # ClientFacts uses role_controller / role_processor
    if getattr(facts, "role_controller", True):
        roles.append("controller")
    if getattr(facts, "role_processor", False):
        roles.append("processor")
    if getattr(facts, "role_joint_controller", False):
        roles.append("joint_controller")
    return roles or ["controller"]


def _derive_jurisdiction(facts) -> list[str]:
    """Derive jurisdiction from ClientFacts."""
    if facts is None:
        return ["EU"]
    jur = getattr(facts, "jurisdiction", None)
    if isinstance(jur, list):
        return jur
    if isinstance(jur, str):
        return [jur]
    return ["EU"]
