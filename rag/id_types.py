"""
Typed identifiers — validation at construction time, no silent-fail.

Motivation
==========
Python's duck typing lets `tenant_id: str` mean UUID in one place and
display name in another. That mismatch bit us multiple times during
Ship 2': the eval fixture set `TenantProfile.tenant_id = "arion-networks"`
(slug), `rag/arion_state.py:89` set `state["tenant_id"] = tenant.name`
(display name), and downstream Postgres writers happily accepted either
and silently failed on the `::uuid` cast — often inside "best-effort"
try/except blocks that swallowed the error.

This module defines identifier classes that validate at construction.
An `TenantUUID("Arion Networks")` raises ValueError immediately rather
than trickling into a silent write failure two layers deeper.

Design
======
Each class is a `str` subclass, so:
  - Postgres drivers, JSON serialisers, logs, and format strings work
    unchanged (they still see a `str`).
  - IDE + mypy see the distinct type, catching `tenant_id: TenantUUID`
    being handed a plain str without validation.
  - Zero runtime cost — no wrapping object; the string IS the identifier.

Naming rule (see CLAUDE.md)
============================
When a field is called `X_id`, it MUST be the canonical UUID (unless
its class is one of the composite-ref types below). Slug fields get
`_slug`. Display names get `_name`. Composite refs get `_ref` or a
suffix indicating shape.

Adoption strategy
=================
Introduce here, use in NEW code, migrate old sites opportunistically
when touched. Not a big-bang refactor — a ratchet.
"""
from __future__ import annotations

import re


# ── Tenant identifiers ────────────────────────────────────────────────

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


class TenantUUID(str):
    """A tenant's canonical UUID — the primary key from tenants.id.

    Raises ValueError at construction if the input isn't UUID-shaped.
    Use this for anything that will be cast to ::uuid in SQL or
    compared to a UUID column.

    Example:
        tid = TenantUUID("00000000-0000-0000-0000-000000000001")
        cur.execute("... WHERE tenant_id = %s::uuid", (tid,))
    """
    def __new__(cls, value: str) -> "TenantUUID":
        if value is None:
            raise ValueError("TenantUUID cannot be None")
        s = str(value).strip()
        if not _UUID_RE.match(s):
            raise ValueError(
                f"not a valid tenant UUID: {value!r} "
                "(expected format like '00000000-0000-0000-0000-000000000001')"
            )
        return super().__new__(cls, s.lower())

    @classmethod
    def coerce(cls, value) -> "TenantUUID | None":
        """Best-effort constructor: returns None on invalid input rather
        than raising. Use at boundaries where a silent skip is intentional
        (e.g. logging that shouldn't block on a bad ID)."""
        try:
            return cls(value)
        except (ValueError, TypeError):
            return None


class TenantSlug(str):
    """URL-safe stable tenant identifier from tenants.slug.

    Not currently used on any public URL but kept for consistency —
    external API launch may prefer slugs over UUIDs on paths.
    """
    def __new__(cls, value: str) -> "TenantSlug":
        if value is None:
            raise ValueError("TenantSlug cannot be None")
        s = str(value).strip().lower()
        if not _SLUG_RE.match(s):
            raise ValueError(
                f"not a valid tenant slug: {value!r} "
                "(expected lowercase alphanumeric with hyphens)"
            )
        return super().__new__(cls, s)


# ── Control / node identifiers (composite refs) ───────────────────────

# Bare control ref: "A.5.18" (Annex A), "Art.32" (GDPR), "9.2" (ISMS clause),
# "A.7.2.4" (ISO 27701 Annex A), "B.8.5.6" (ISO 27701 Annex B).
_CONTROL_REF_RE = re.compile(
    r"^(?:"
        r"[AB]\.\d+(?:\.\d+){0,3}"    # Annex A/B controls (A.5.18, A.7.2.4, B.8.5.6)
        r"|Art\.\d+(?:\.\d+)?(?:\([a-z0-9]+\))?"  # GDPR articles (Art.32, Art.5.1, Art.32.1.a)
        r"|\d+\.\d+(?:\.\d+){0,2}"    # ISMS body clauses (9.2, 6.1.2, 10.1)
    r")$"
)


class ControlRef(str):
    """A bare control/article/clause ref — the string that appears in
    a citation like 'ISO 27001 A.5.18' or 'GDPR Art.32'.

    Note: ISMS body clauses (5.1, 6.1.2, 9.2) collide with dotted Annex A
    tokens at 2-dot level. This class does NOT disambiguate — the caller
    is responsible for knowing which flavour it holds. See
    `rag/framework_refs.py` for normalisation.
    """
    def __new__(cls, value: str) -> "ControlRef":
        if value is None:
            raise ValueError("ControlRef cannot be None")
        s = str(value).strip()
        if not _CONTROL_REF_RE.match(s):
            raise ValueError(
                f"not a valid control ref: {value!r} "
                "(expected shapes like 'A.5.18', 'Art.32', '9.2')"
            )
        return super().__new__(cls, s)


# Composite node id: "ISO27001:2022:A.5.18", "GDPR:2016/679:Art.32"
# Format: STANDARD:VERSION:REF where VERSION may contain "/".
_NODE_ID_RE = re.compile(
    r"^(?P<standard>[A-Za-z][A-Za-z0-9]*):"
    r"(?P<version>[A-Za-z0-9./_-]+):"
    r"(?P<ref>.+)$"
)


class NodeId(str):
    """A fully-qualified requirement-node id — the Neo4j primary key
    and ChromaDB document id. Shape: 'STANDARD:VERSION:REF'.

    Provides `.standard_id`, `.version`, `.ref` accessors so callers
    don't need to `.split(":")` inline (14+ sites in the codebase
    today, brittle if a new framework's version tag contains a colon).
    """
    def __new__(cls, value: str) -> "NodeId":
        if value is None:
            raise ValueError("NodeId cannot be None")
        s = str(value).strip()
        m = _NODE_ID_RE.match(s)
        if not m:
            raise ValueError(
                f"not a valid node id: {value!r} "
                "(expected 'STANDARD:VERSION:REF' like 'ISO27001:2022:A.5.18')"
            )
        obj = super().__new__(cls, s)
        # Cache the parsed parts on the instance for cheap repeat access.
        # These are set as attributes on the str subclass — safe because
        # str is immutable, so no aliasing issues.
        object.__setattr__(obj, "_standard", m.group("standard"))
        object.__setattr__(obj, "_version",  m.group("version"))
        object.__setattr__(obj, "_ref",      m.group("ref"))
        return obj

    @property
    def standard_id(self) -> str:
        """The standard-and-version prefix, e.g. 'ISO27001:2022'."""
        return f"{self._standard}:{self._version}"

    @property
    def version(self) -> str:
        return self._version

    @property
    def ref(self) -> str:
        """The bare ref, e.g. 'A.5.18'."""
        return self._ref

    def with_ref(self, new_ref: str) -> "NodeId":
        """Return a sibling NodeId with the same standard/version."""
        return NodeId(f"{self.standard_id}:{new_ref}")


# ── Leaf / checklist item identifiers ─────────────────────────────────

# EvidenceRequirement id: "req:A.5.18:policy_document"
# Schema check enforced at DB level in schema_v50 (external_evidence_source).
_LEAF_ID_RE = re.compile(r"^req:[A-Za-z0-9.]+:[a-z0-9_]+$")


class LeafId(str):
    """An EvidenceRequirement's id — 'req:{control_ref}:{evidence_type}'.

    Matches the regex enforced at Postgres level in schema_v50 for
    external_evidence_source / external_evidence_verification_log.
    """
    def __new__(cls, value: str) -> "LeafId":
        if value is None:
            raise ValueError("LeafId cannot be None")
        s = str(value).strip()
        if not _LEAF_ID_RE.match(s):
            raise ValueError(
                f"not a valid leaf id: {value!r} "
                "(expected 'req:<control_ref>:<evidence_type>')"
            )
        return super().__new__(cls, s)


# ── Predicates for callers that don't want to construct a full type ──

def is_uuid(value) -> bool:
    """True if the string is UUID-shaped. Cheaper than TenantUUID.coerce()
    when the caller only needs the predicate."""
    if not isinstance(value, str):
        return False
    return bool(_UUID_RE.match(value))


def is_node_id(value) -> bool:
    if not isinstance(value, str):
        return False
    return bool(_NODE_ID_RE.match(value))


def is_control_ref(value) -> bool:
    if not isinstance(value, str):
        return False
    return bool(_CONTROL_REF_RE.match(value))


__all__ = [
    "TenantUUID",
    "TenantSlug",
    "ControlRef",
    "NodeId",
    "LeafId",
    "is_uuid",
    "is_node_id",
    "is_control_ref",
]
