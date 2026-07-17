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
# Captured groups: (control_ref, evidence_type).
_LEAF_ID_RE = re.compile(r"^req:(?P<control_ref>[A-Za-z0-9.]+):(?P<evidence_type>[a-z0-9_]+)$")


class LeafId(str):
    """An EvidenceRequirement's id — 'req:{control_ref}:{evidence_type}'.

    Matches the regex enforced at Postgres level in schema_v50 for
    external_evidence_source / external_evidence_verification_log.

    Accessors (Ship 2'.p):
      .control_ref    — the middle segment (e.g. 'A.5.18')
      .evidence_type  — the trailing slug (e.g. 'policy_document')
    """
    def __new__(cls, value: str) -> "LeafId":
        if value is None:
            raise ValueError("LeafId cannot be None")
        s = str(value).strip()
        m = _LEAF_ID_RE.match(s)
        if not m:
            raise ValueError(
                f"not a valid leaf id: {value!r} "
                "(expected 'req:<control_ref>:<evidence_type>')"
            )
        obj = super().__new__(cls, s)
        object.__setattr__(obj, "_control_ref",   m.group("control_ref"))
        object.__setattr__(obj, "_evidence_type", m.group("evidence_type"))
        return obj

    @property
    def control_ref(self) -> str:
        """The control this leaf belongs to (e.g. 'A.5.18')."""
        return self._control_ref

    @property
    def evidence_type(self) -> str:
        """The evidence-type slug (e.g. 'policy_document')."""
        return self._evidence_type


# ChecklistItem id: "item:{control_ref}:{slug}"
# Ship 2'.p: added type + accessors, previously handled by inline split.
_ITEM_ID_RE = re.compile(r"^item:(?P<control_ref>[A-Za-z0-9.]+):(?P<slug>[A-Za-z0-9_]+)$")


class ItemId(str):
    """A ChecklistItem's id — 'item:{control_ref}:{slug}'.

    Accessors:
      .control_ref  — the middle segment (e.g. 'A.5.18')
      .slug         — the trailing checklist-item slug (e.g. 'access_matrix')
    """
    def __new__(cls, value: str) -> "ItemId":
        if value is None:
            raise ValueError("ItemId cannot be None")
        s = str(value).strip()
        m = _ITEM_ID_RE.match(s)
        if not m:
            raise ValueError(
                f"not a valid item id: {value!r} "
                "(expected 'item:<control_ref>:<slug>')"
            )
        obj = super().__new__(cls, s)
        object.__setattr__(obj, "_control_ref", m.group("control_ref"))
        object.__setattr__(obj, "_slug",        m.group("slug"))
        return obj

    @property
    def control_ref(self) -> str:
        return self._control_ref

    @property
    def slug(self) -> str:
        return self._slug


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


# ── Node-id accessor helpers (Ship 2'.m migration target) ─────────────
#
# These replace inline `node_id.split(":")` patterns across the
# codebase. NodeId(...) itself validates strictly and raises on
# malformed input; these helpers add a fallback for callers that
# historically used `if ':' in node_id` guards.
#
# Use these when the caller doesn't want the shape-validation
# strictness (e.g. legacy posture keys, edge ids from historical
# writes). For NEW code, prefer `NodeId(value)` directly so
# malformed inputs raise loudly.

def ref_of(node_id: str) -> str:
    """Return the ref part of a node_id.

    Fallback: last colon-segment. Empty string on unparseable input.
    Matches the legacy `node_id.split(":")[-1]` behavior.
    """
    try:
        return NodeId(node_id).ref
    except (ValueError, TypeError):
        if isinstance(node_id, str) and ":" in node_id:
            return node_id.split(":")[-1]
        return str(node_id) if node_id else ""


def standard_of(node_id: str) -> str:
    """Return the STANDARD:VERSION prefix of a node_id.

    Fallback: first two colon-segments joined. Empty string on
    unparseable input. Matches the legacy
    `":".join(node_id.split(":")[:2])` behavior.
    """
    try:
        return NodeId(node_id).standard_id
    except (ValueError, TypeError):
        if isinstance(node_id, str) and ":" in node_id:
            parts = node_id.split(":")
            if len(parts) >= 2:
                return ":".join(parts[:2])
        return ""


# ── Leaf/item safe helpers (Ship 2'.p migration target) ─────────────

def leaf_control_ref(leaf_id: str) -> str:
    """Return the control_ref part of a leaf_id (`req:X:Y` → `X`).

    Fallback: parts[1] of a colon-split. Empty string on unparseable
    input. Matches the legacy inline patterns retired in Ship 2'.p.
    """
    try:
        return LeafId(leaf_id).control_ref
    except (ValueError, TypeError):
        if isinstance(leaf_id, str) and leaf_id.startswith("req:"):
            parts = leaf_id.split(":")
            if len(parts) >= 2:
                return parts[1]
        return ""


def leaf_evidence_type(leaf_id: str) -> str:
    """Return the evidence-type slug of a leaf_id (`req:X:Y` → `Y`).

    Fallback: parts[-1] of a colon-split. Empty on unparseable.
    """
    try:
        return LeafId(leaf_id).evidence_type
    except (ValueError, TypeError):
        if isinstance(leaf_id, str) and ":" in leaf_id:
            parts = leaf_id.split(":")
            if len(parts) >= 3:
                return parts[-1]
        return ""


def item_control_ref(item_id: str) -> str:
    """Return the control_ref part of an item_id (`item:X:Y` → `X`)."""
    try:
        return ItemId(item_id).control_ref
    except (ValueError, TypeError):
        if isinstance(item_id, str) and item_id.startswith("item:"):
            parts = item_id.split(":")
            if len(parts) >= 2:
                return parts[1]
        return ""


def item_slug(item_id: str) -> str:
    """Return the slug part of an item_id (`item:X:Y` → `Y`)."""
    try:
        return ItemId(item_id).slug
    except (ValueError, TypeError):
        if isinstance(item_id, str) and ":" in item_id:
            parts = item_id.split(":")
            if len(parts) >= 3:
                return parts[-1]
        return ""


__all__ = [
    "TenantUUID",
    "TenantSlug",
    "ControlRef",
    "NodeId",
    "LeafId",
    "ItemId",
    "is_uuid",
    "is_node_id",
    "is_control_ref",
    "ref_of",
    "standard_of",
    "leaf_control_ref",
    "leaf_evidence_type",
    "item_control_ref",
    "item_slug",
]
