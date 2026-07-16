"""
Tests for rag/id_types.py — typed identifier classes.

Run: PYTHONPATH=/data/arioncomply python3 tests/test_id_types.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.id_types import (
    TenantUUID, TenantSlug, ControlRef, NodeId, LeafId,
    is_uuid, is_node_id, is_control_ref,
)


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── TenantUUID ────────────────────────────────────────────────────────

def test_tenant_uuid_accepts_valid():
    t = TenantUUID("00000000-0000-0000-0000-000000000001")
    return _ok(str(t) == "00000000-0000-0000-0000-000000000001")


def test_tenant_uuid_is_str_subclass():
    """TenantUUID must be usable anywhere str is expected — Postgres,
    json.dumps, format strings, etc."""
    t = TenantUUID("00000000-0000-0000-0000-000000000001")
    return _ok(isinstance(t, str) and f"tenant={t}" == "tenant=00000000-0000-0000-0000-000000000001")


def test_tenant_uuid_lowercases():
    """Postgres UUID compare is case-insensitive but normalise for
    consistent hash/dict keys."""
    t = TenantUUID("ABCDEF00-0000-0000-0000-000000000001")
    return _ok(str(t) == "abcdef00-0000-0000-0000-000000000001")


def test_tenant_uuid_rejects_display_name():
    try:
        TenantUUID("Arion Networks")
        return _ok(False, "should have raised")
    except ValueError:
        return _ok(True)


def test_tenant_uuid_rejects_slug():
    try:
        TenantUUID("arion-networks")
        return _ok(False, "should have raised")
    except ValueError:
        return _ok(True)


def test_tenant_uuid_rejects_none():
    try:
        TenantUUID(None)
        return _ok(False)
    except ValueError:
        return _ok(True)


def test_tenant_uuid_rejects_empty():
    try:
        TenantUUID("")
        return _ok(False)
    except ValueError:
        return _ok(True)


def test_tenant_uuid_coerce_returns_none_on_bad():
    return _ok(
        TenantUUID.coerce("Arion Networks") is None
        and TenantUUID.coerce(None) is None
        and TenantUUID.coerce(123) is None,
    )


def test_tenant_uuid_coerce_returns_uuid_on_good():
    t = TenantUUID.coerce("00000000-0000-0000-0000-000000000001")
    return _ok(isinstance(t, TenantUUID))


# ── TenantSlug ────────────────────────────────────────────────────────

def test_tenant_slug_accepts_valid():
    s = TenantSlug("arion-networks")
    return _ok(str(s) == "arion-networks")


def test_tenant_slug_rejects_uppercase_after_lower():
    """Slug is lowercase-normalised. Uppercase input becomes lowercase."""
    s = TenantSlug("Arion-Networks")
    return _ok(str(s) == "arion-networks")


def test_tenant_slug_rejects_spaces():
    try:
        TenantSlug("arion networks")
        return _ok(False)
    except ValueError:
        return _ok(True)


# ── ControlRef ────────────────────────────────────────────────────────

def test_control_ref_accepts_annex_a():
    return _ok(str(ControlRef("A.5.18")) == "A.5.18")


def test_control_ref_accepts_iso27701_extended():
    return _ok(
        str(ControlRef("A.7.2.4")) == "A.7.2.4"
        and str(ControlRef("B.8.5.6")) == "B.8.5.6"
    )


def test_control_ref_accepts_gdpr_article():
    return _ok(
        str(ControlRef("Art.32")) == "Art.32"
        and str(ControlRef("Art.5.1")) == "Art.5.1"
        and str(ControlRef("Art.32.1(a)")) == "Art.32.1(a)"
    )


def test_control_ref_accepts_isms_body_clause():
    return _ok(
        str(ControlRef("9.2")) == "9.2"
        and str(ControlRef("6.1.2")) == "6.1.2"
        and str(ControlRef("10.1")) == "10.1"
    )


def test_control_ref_rejects_junk():
    for bad in ["bad", "A5.18", "5", "A."]:
        try:
            ControlRef(bad)
            return _ok(False, f"should have rejected {bad!r}")
        except ValueError:
            pass
    return _ok(True)


# ── NodeId ────────────────────────────────────────────────────────────

def test_node_id_accepts_iso():
    n = NodeId("ISO27001:2022:A.5.18")
    return _ok(
        n.standard_id == "ISO27001:2022"
        and n.version == "2022"
        and n.ref == "A.5.18"
    )


def test_node_id_accepts_gdpr_with_slash_in_version():
    """This is the important one — GDPR:2016/679:Art.32 has a slash in
    the version and 3 colon-separated pieces."""
    n = NodeId("GDPR:2016/679:Art.32")
    return _ok(
        n.standard_id == "GDPR:2016/679"
        and n.version == "2016/679"
        and n.ref == "Art.32",
        f"got standard_id={n.standard_id!r} version={n.version!r} ref={n.ref!r}",
    )


def test_node_id_with_ref_returns_sibling():
    n = NodeId("ISO27001:2022:A.5.18")
    sibling = n.with_ref("A.5.20")
    return _ok(
        isinstance(sibling, NodeId)
        and sibling.ref == "A.5.20"
        and sibling.standard_id == "ISO27001:2022"
    )


def test_node_id_rejects_two_parts():
    try:
        NodeId("ISO27001:A.5.18")
        return _ok(False)
    except ValueError:
        return _ok(True)


def test_node_id_rejects_empty():
    try:
        NodeId("")
        return _ok(False)
    except ValueError:
        return _ok(True)


def test_node_id_is_str_usable():
    n = NodeId("ISO27001:2022:A.5.18")
    return _ok(
        n == "ISO27001:2022:A.5.18"
        and f"{n}" == "ISO27001:2022:A.5.18"
        and hash(n) == hash("ISO27001:2022:A.5.18"),
    )


# ── LeafId ────────────────────────────────────────────────────────────

def test_leaf_id_accepts_valid():
    l = LeafId("req:A.5.18:policy_document")
    return _ok(str(l) == "req:A.5.18:policy_document")


def test_leaf_id_rejects_missing_prefix():
    try:
        LeafId("A.5.18:policy_document")
        return _ok(False)
    except ValueError:
        return _ok(True)


def test_leaf_id_rejects_uppercase_evidence_type():
    """evidence_type slug is lowercase-only."""
    try:
        LeafId("req:A.5.18:PolicyDocument")
        return _ok(False)
    except ValueError:
        return _ok(True)


# ── Predicates ────────────────────────────────────────────────────────

def test_is_uuid_predicate():
    return _ok(
        is_uuid("00000000-0000-0000-0000-000000000001")
        and not is_uuid("Arion Networks")
        and not is_uuid("arion-networks")
        and not is_uuid(None)
        and not is_uuid(123)
    )


def test_is_node_id_predicate():
    return _ok(
        is_node_id("ISO27001:2022:A.5.18")
        and is_node_id("GDPR:2016/679:Art.32")
        and not is_node_id("A.5.18")
        and not is_node_id(None)
    )


def test_is_control_ref_predicate():
    return _ok(
        is_control_ref("A.5.18")
        and is_control_ref("Art.32")
        and is_control_ref("9.2")
        and not is_control_ref("bad")
        and not is_control_ref(None)
    )


TESTS = [
    test_tenant_uuid_accepts_valid,
    test_tenant_uuid_is_str_subclass,
    test_tenant_uuid_lowercases,
    test_tenant_uuid_rejects_display_name,
    test_tenant_uuid_rejects_slug,
    test_tenant_uuid_rejects_none,
    test_tenant_uuid_rejects_empty,
    test_tenant_uuid_coerce_returns_none_on_bad,
    test_tenant_uuid_coerce_returns_uuid_on_good,
    test_tenant_slug_accepts_valid,
    test_tenant_slug_rejects_uppercase_after_lower,
    test_tenant_slug_rejects_spaces,
    test_control_ref_accepts_annex_a,
    test_control_ref_accepts_iso27701_extended,
    test_control_ref_accepts_gdpr_article,
    test_control_ref_accepts_isms_body_clause,
    test_control_ref_rejects_junk,
    test_node_id_accepts_iso,
    test_node_id_accepts_gdpr_with_slash_in_version,
    test_node_id_with_ref_returns_sibling,
    test_node_id_rejects_two_parts,
    test_node_id_rejects_empty,
    test_node_id_is_str_usable,
    test_leaf_id_accepts_valid,
    test_leaf_id_rejects_missing_prefix,
    test_leaf_id_rejects_uppercase_evidence_type,
    test_is_uuid_predicate,
    test_is_node_id_predicate,
    test_is_control_ref_predicate,
]


def main():
    print("─" * 70)
    print("  ID types tests")
    print("─" * 70)
    failures = 0
    for t in TESTS:
        try:
            ok, msg = t()
        except Exception as e:
            import traceback
            ok = False
            msg = f"raised {type(e).__name__}: {e}\n{traceback.format_exc()}"
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {t.__name__}")
        if not ok:
            print(f"         {msg}")
            failures += 1
    print("─" * 70)
    print(f"  {len(TESTS) - failures}/{len(TESTS)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
