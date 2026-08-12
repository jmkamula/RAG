"""Ship 63' — snapshot tests for Evidence Package rendering.

Run: PYTHONPATH=/data/arioncomply python3 tests/test_evidence_package.py

Exercises the Ship 61'.a + 62' hybrid: SSoT for coverage state,
`document_findings` for verbatim excerpts, bridge attribution with
per-package excerpt dedup.

Runs against the Arion demo tenant (SSoT + findings both populated
via periodic sweep + intake). Skips cleanly when Postgres isn't
reachable (dev laptop without the demo DB).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    if (_ROOT / ".env").exists():
        load_dotenv(_ROOT / ".env")
except ImportError:
    pass


# Arion demo tenant — populated with full SSoT + doc_findings on the
# reference deployment.
ARION_TENANT = "00000000-0000-0000-0000-000000000001"
FRESH_TENANT = "99999999-9999-9999-9999-999999999999"


def _open_pg():
    """Real Postgres connection scoped to Arion. Returns None if
    the DB isn't reachable — the caller skips the whole suite in
    that case."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host     = os.getenv("PGHOST",     "127.0.0.1"),
            dbname   = os.getenv("PGDATABASE", "arioncomply_compliance"),
            user     = os.getenv("PGUSER",     "arioncomply"),
            password = os.getenv("PGPASSWORD", os.getenv("POSTGRES_PASSWORD", "")),
        )
    except Exception as e:
        print(f"skip: postgres unreachable — {e}")
        return None
    with conn.cursor() as c:
        c.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (ARION_TENANT,))
    return conn


def test_bridged_leaf_shows_cross_framework_header(pg):
    """Art.32:program_review has 1 direct + 4 bridged MUSTs on Arion.
    Header must expose the cross-framework count and rolled-up source
    standards; each ↗ element must render `Covered via` + source
    excerpt from the actual ISO evidence."""
    from rag.posture.evidence_package import build_evidence_package
    md = build_evidence_package(pg, ARION_TENANT, "req:Art.32:program_review")
    assert md is not None, "expected markdown, got None"

    assert "**Status:** Partially covered" in md
    assert "**Cross-framework coverage:**" in md
    assert "ISO 27001:2022" in md
    assert "controls (see below)." in md

    required = md.split("## Required elements")[1].split("## ")[0]
    assert required.count("- ✓") >= 1, "expected at least one ✓ MUST"
    assert required.count("- ↗") >= 1, "expected at least one ↗ MUST"
    assert "(cross-framework coverage)" in required
    assert "↳ Covered via _" in required


def test_bridged_leaf_dedupes_source_excerpts(pg):
    """Ship 62' — first bridged MUST that references A.5.18 shows the
    excerpt; subsequent references collapse to a pointer. The excerpt
    should appear exactly once for a given (std, source_ref) pair,
    replaced by `source excerpt shown under ... above` on later
    references within the same package."""
    from rag.posture.evidence_package import build_evidence_package
    md = build_evidence_package(pg, ARION_TENANT, "req:Art.32:program_review")
    assert md is not None

    a518_covered_via = md.count("Covered via _ISO 27001:2022 A.5.18_")
    a518_above = md.count("source excerpt shown under _ISO 27001:2022 A.5.18_ above")
    assert a518_covered_via >= 2, (
        f"A.5.18 should appear under multiple bridged MUSTs "
        f"(got {a518_covered_via})"
    )
    assert a518_above == a518_covered_via - 1, (
        f"expected {a518_covered_via - 1} 'shown ... above' pointers "
        f"for A.5.18, got {a518_above}"
    )


def test_fully_satisfied_leaf_renders_no_bridge_header(pg):
    """A.5.15:management_approval is fully-satisfied on Arion (3/3
    direct). No cross-framework line should render; every MUST is ✓."""
    from rag.posture.evidence_package import build_evidence_package
    md = build_evidence_package(pg, ARION_TENANT, "req:A.5.15:management_approval")
    assert md is not None

    assert "**Status:** Fully covered" in md
    assert "3 of 3 required elements covered (100%)" in md
    assert "**Cross-framework coverage:**" not in md

    required = md.split("## Required elements")[1].split("## ")[0]
    assert required.count("- ✓") == 3
    assert required.count("- ↗") == 0
    assert required.count("- ✗") == 0


def test_fresh_tenant_fallback(pg):
    """SSoT-empty fallback: no crash. Unmet MUSTs render as ✗ via the
    pre-Ship-61'.a findings-only heuristic. Cross-framework header
    is suppressed (bridge attribution requires SSoT)."""
    from rag.posture.evidence_package import build_evidence_package
    md = build_evidence_package(pg, FRESH_TENANT, "req:A.5.15:management_approval")
    assert md is not None

    assert "**Status:** Not yet covered" in md
    assert "0 of 3 required elements covered (0%)" in md
    assert "**Cross-framework coverage:**" not in md

    required = md.split("## Required elements")[1].split("## ")[0]
    assert required.count("- ✗") == 3
    assert required.count("- ↗") == 0


def test_missing_leaf_returns_none(pg):
    """A leaf id that isn't in the catalog returns None (not empty
    markdown, not a crash)."""
    from rag.posture.evidence_package import build_evidence_package
    md = build_evidence_package(pg, ARION_TENANT, "req:not-a-real-leaf:nonexistent")
    assert md is None


CASES = [
    test_bridged_leaf_shows_cross_framework_header,
    test_bridged_leaf_dedupes_source_excerpts,
    test_fully_satisfied_leaf_renders_no_bridge_header,
    test_fresh_tenant_fallback,
    test_missing_leaf_returns_none,
]


def main() -> int:
    pg = _open_pg()
    if pg is None:
        print("SKIP — postgres unavailable")
        return 0
    failed = 0
    try:
        for fn in CASES:
            name = fn.__name__
            try:
                fn(pg)
                print(f"PASS  {name}")
            except AssertionError as e:
                failed += 1
                print(f"FAIL  {name}: {e}")
            except Exception as e:
                failed += 1
                print(f"ERROR {name}: {type(e).__name__}: {e}")
    finally:
        pg.close()
    if failed:
        print(f"\n{failed} of {len(CASES)} cases failed.")
        return 1
    print(f"\n{len(CASES)} of {len(CASES)} cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
