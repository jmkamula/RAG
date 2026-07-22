"""
FastAPI path/body/query parameter types with automatic shape validation.

Motivation
==========
Every API endpoint that takes an identifier via URL / body used to
type it as `str`. That string then flowed unchanged into a Postgres
`%s::uuid` cast. If the caller sent the wrong shape (a slug instead
of a UUID, junk instead of a control ref), the cast raised
`InvalidTextRepresentation` — surfacing as a 500 with a generic
error to the tenant, no field-level rejection at the door.

Ship 2'.k moves the validation to the FastAPI layer: bad shapes now
return 400 with a clean error message before any Postgres call. This
is the pre-external-API-launch prerequisite from the ID-discipline
audit (2026-07-16).

Usage
=====
Import the Annotated type alias and use it as the endpoint param
type. FastAPI + Pydantic will validate + coerce + produce a 400 on
mismatch — no application code needed.

    from rag.api_types import PostureIdParam

    @app.post("/api/v1/posture/{posture_id}/confirm")
    async def confirm_posture(posture_id: PostureIdParam, ...):
        # posture_id is guaranteed to be a valid UUID string here
        ...

For refs / composite IDs where regex validation is the right
guarantee (control_ref, leaf_id), use the corresponding *Param
type — Pydantic's `pattern` on `Path()` enforces the shape.

Design notes
============
- These are FastAPI-facing aliases. Python-facing typed IDs live in
  `rag/id_types.py` (TenantUUID, ControlRef, NodeId, LeafId as str
  subclasses that validate at construction). The two coexist.
- We use `str` for UUID params rather than the `uuid.UUID` type
  because downstream SQL casts to `::uuid` expect a string; using
  the UUID type would force `str(uuid_value)` at every call site.
  Pydantic's UUID validation still fires — the resulting string
  IS UUID-shaped.
- Regex patterns match `rag/id_types.py` — kept in sync manually.
  If either is edited, update both.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Path


# ── UUID params (regex-validated string) ──────────────────────────────
# We keep UUID params as `str` (not `uuid.UUID`) because:
#   1. psycopg2 doesn't auto-adapt uuid.UUID to the SQL ::uuid cast —
#      would need `psycopg2.extras.register_uuid()` at startup.
#   2. Every downstream SQL site already expects a string.
# Validation via a regex pattern on FastAPI's Path() achieves the
# same "reject at the door" behavior without changing the downstream
# type. Accepts any UUID version (Arion's fixture predates v4).
_UUID_PATTERN = (
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

TenantIdParam    = Annotated[str, Path(pattern=_UUID_PATTERN, description="Tenant UUID")]
PostureIdParam   = Annotated[str, Path(pattern=_UUID_PATTERN, description="Posture record UUID")]
ProposalIdParam  = Annotated[str, Path(pattern=_UUID_PATTERN, description="Proposal UUID")]
OverrideIdParam  = Annotated[str, Path(pattern=_UUID_PATTERN, description="Override UUID")]
UploadIdParam    = Annotated[str, Path(pattern=_UUID_PATTERN, description="Upload UUID")]
SystemIdParam    = Annotated[str, Path(pattern=_UUID_PATTERN, description="External-system UUID")]
NotifIdParam     = Annotated[str, Path(pattern=_UUID_PATTERN, description="Notification UUID")]
ImplicationIdParam = Annotated[str, Path(pattern=_UUID_PATTERN, description="Cascade-implication UUID")]
SeriesIdParam    = Annotated[str, Path(pattern=_UUID_PATTERN, description="Series UUID")]
RiskIdParam      = Annotated[str, Path(pattern=_UUID_PATTERN, description="Risk UUID (Ship 14'.c — risks table)")]


# ── Composite / regex-validated params ────────────────────────────────

# Bare control refs: "A.5.18" (Annex A), "Art.32" (GDPR),
# "9.2" (ISMS body clause), "A.7.2.4" (ISO 27701).
_CONTROL_REF_PATTERN = (
    r"^(?:"
        r"[AB]\.\d+(?:\.\d+){0,3}"
        r"|Art\.\d+(?:\.\d+)?(?:\([a-z0-9]+\))?"
        r"|\d+\.\d+(?:\.\d+){0,2}"
    r")$"
)
ControlRefParam = Annotated[
    str,
    Path(
        pattern=_CONTROL_REF_PATTERN,
        description="Control ref like A.5.18, Art.32, 9.2, or A.7.2.4",
    ),
]

# EvidenceRequirement id: "req:{control_ref}:{evidence_type}"
_LEAF_ID_PATTERN = r"^req:[A-Za-z0-9.]+:[a-z0-9_]+$"
LeafIdParam = Annotated[
    str,
    Path(
        pattern=_LEAF_ID_PATTERN,
        description="Leaf id like req:A.5.18:policy_document",
    ),
]

# Cascade event kinds — enum of known kinds. Extend when adding new
# cascade sources. Keeps `/cascade-event/{kind}/{eid}` from accepting
# arbitrary URL segments.
_CASCADE_KIND_PATTERN = r"^[a-z_]+$"
CascadeKindParam = Annotated[
    str,
    Path(
        pattern=_CASCADE_KIND_PATTERN,
        description="Cascade event kind (lowercase snake_case)",
    ),
]

# Fact key — snake_case identifier for a tenant fact.
_FACT_KEY_PATTERN = r"^[a-z0-9_]+$"
FactKeyParam = Annotated[
    str,
    Path(
        pattern=_FACT_KEY_PATTERN,
        description="Fact key (lowercase snake_case)",
    ),
]


# ── Session identifiers ───────────────────────────────────────────────
# Ship 2'.l: session_id is caller-provided. Constrain to a safe shape
# so it can't smuggle SQL fragments, path traversal, or bytes that
# would break the LangGraph checkpoint key format
# `f"{tenant_id}:{session_id}"`. Length cap prevents pathological
# checkpoint-key sizes; character class matches the RFC 8446-ish
# alphanum + underscore + hyphen convention used by URL-safe tokens.
_SESSION_ID_PATTERN = r"^[A-Za-z0-9_-]{1,64}$"


def build_thread_id(tenant_id: str, session_id: str) -> str:
    """Compose the LangGraph checkpoint thread_id from tenant + session.

    Ship 2'.l: uses the FULL tenant UUID as the prefix (was
    `tenant_id[:8]`). The 8-char truncation had a 2^32 collision
    space — with N tenants past ~65k, birthday-collision risk exists
    that could let a crafted session_id read another tenant's
    checkpoint. Full UUID puts collision at 2^128 — practically zero.
    """
    return f"{tenant_id}:{session_id}"


def validate_session_id_shape(sid: str) -> bool:
    """True when sid conforms to _SESSION_ID_PATTERN. Callers use
    this at the request boundary to fail loudly on malformed shapes
    (path traversal, SQL fragments, etc.)."""
    if not sid or not isinstance(sid, str):
        return False
    import re
    return bool(re.match(_SESSION_ID_PATTERN, sid))


__all__ = [
    "TenantIdParam",
    "PostureIdParam",
    "ProposalIdParam",
    "OverrideIdParam",
    "UploadIdParam",
    "SystemIdParam",
    "NotifIdParam",
    "ImplicationIdParam",
    "SeriesIdParam",
    "ControlRefParam",
    "LeafIdParam",
    "CascadeKindParam",
    "FactKeyParam",
    "build_thread_id",
    "validate_session_id_shape",
]
