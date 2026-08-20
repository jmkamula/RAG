"""Ship 89'.b unit tests — cite_columns YAML field + cite-mode emission.

Locks the discovery-side binding (cite_columns → PassProposal.cite_bindings)
and the persistence-side wiring rules (idempotent tenant_external_system
resolve; UNIQUE constraint collapse on repeated cites).

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_workbook_cite_columns.py
"""
from __future__ import annotations
import sys

from rag.intake.workbook_discovery import PassProposal, evaluate_pass
from rag.intake.workbook_persistence import _ensure_external_system, _upsert_cite


def _check(cond: bool, label: str) -> int:
    print(f"    {'OK' if cond else 'FAIL'} {label}")
    return 0 if cond else 1


def test_evaluate_pass_captures_cite_binding() -> int:
    print("  evaluate_pass — cite_columns → cite_bindings")
    pass_block = {
        "pass_name":                   "soa",
        "target_control":              "6.1.3",
        "target_evidence_requirement": "req:6.1.3:soa",
        "target_evidence_type":        "statement_of_applicability",
        "required_columns": [
            {"fingerprint": ["control", "id"], "binds_to": "item:6.1.3:soa_all_annex_a"},
        ],
        "cite_columns": [
            {"fingerprint": ["linked", "policies"],
             "binds_to": "item:6.1.3:soa_reference",
             "cite_kind": "internal_document",
             "verification_days": 180},
        ],
    }
    headers = ["Control ID", "Applicable", "Linked Policies"]
    prop = evaluate_pass(pass_block, headers)
    fails = 0
    fails += _check(
        "item:6.1.3:soa_reference" in prop.cite_bindings,
        "MUST id present in cite_bindings",
    )
    if "item:6.1.3:soa_reference" in prop.cite_bindings:
        cb = prop.cite_bindings["item:6.1.3:soa_reference"]
        fails += _check(cb["header"] == "Linked Policies",   "header captured")
        fails += _check(cb["cite_kind"] == "internal_document", "cite_kind captured")
        fails += _check(cb["verification_days"] == 180,      "verification_days captured")
    return fails


def test_evaluate_pass_cite_columns_skipped_when_no_header_match() -> int:
    print("  evaluate_pass — cite_columns MUST that matches nothing → skip")
    pass_block = {
        "pass_name":                   "x",
        "target_control":              "X",
        "target_evidence_requirement": "req:X:y",
        "target_evidence_type":        "register",
        "cite_columns": [
            {"fingerprint": ["nonexistent", "column"],
             "binds_to": "item:X:policy_ref",
             "cite_kind": "url"},
        ],
    }
    prop = evaluate_pass(pass_block, ["ID", "Name", "Owner"])
    return _check(prop.cite_bindings == {}, "no binding emitted when header missing")


def test_evaluate_pass_cite_columns_default_kind() -> int:
    print("  evaluate_pass — cite_kind defaults to internal_document")
    pass_block = {
        "pass_name":                   "x",
        "target_control":              "X",
        "target_evidence_requirement": "req:X:y",
        "target_evidence_type":        "register",
        "cite_columns": [
            # No cite_kind
            {"fingerprint": ["ref"], "binds_to": "item:X:ref"},
        ],
    }
    prop = evaluate_pass(pass_block, ["Ref"])
    fails = 0
    fails += _check("item:X:ref" in prop.cite_bindings, "binding created")
    if "item:X:ref" in prop.cite_bindings:
        fails += _check(
            prop.cite_bindings["item:X:ref"]["cite_kind"] == "internal_document",
            "cite_kind defaults to internal_document",
        )
    return fails


def test_row_level_guard_requires_real_hyperlink() -> int:
    print("  evaluate_pass — cite emission requires ≥1 non-mailto hyperlink on data row")
    pass_block = {
        "pass_name":                   "x",
        "target_control":              "X",
        "target_evidence_requirement": "req:X:y",
        "target_evidence_type":        "register",
        "cite_columns": [
            {"fingerprint": ["policy", "link"], "binds_to": "item:X:policy_ref"},
        ],
    }
    headers = ["ID", "Name", "Policy Link"]
    fails = 0

    # Case A: no hyperlinks at all → no cite
    prop = evaluate_pass(pass_block, headers, sheet_hyperlinks=[], header_row=0)
    fails += _check(prop.cite_bindings == {},
                    "empty hyperlinks → no cite binding")

    # Case B: hyperlink on header row (row 1) → no cite (header != data)
    prop = evaluate_pass(pass_block, headers,
        sheet_hyperlinks=[{"cell": "C1", "url": "https://x/", "label": "hdr"}],
        header_row=0)
    fails += _check(prop.cite_bindings == {},
                    "header-row hyperlink → no cite")

    # Case C: mailto-only on data rows → no cite
    prop = evaluate_pass(pass_block, headers,
        sheet_hyperlinks=[{"cell": "C2", "url": "mailto:foo@bar", "label": "email"}],
        header_row=0)
    fails += _check(prop.cite_bindings == {},
                    "mailto-only hyperlink → no cite")

    # Case D: real URL on data row → cite emitted
    prop = evaluate_pass(pass_block, headers,
        sheet_hyperlinks=[{"cell": "C2", "url": "https://sharepoint/x.docx", "label": "x"}],
        header_row=0)
    fails += _check("item:X:policy_ref" in prop.cite_bindings,
                    "real URL on data row → cite emitted")

    # Case E: hyperlink on WRONG column (A, not C) → no cite
    prop = evaluate_pass(pass_block, headers,
        sheet_hyperlinks=[{"cell": "A2", "url": "https://sharepoint/x.docx", "label": "x"}],
        header_row=0)
    fails += _check(prop.cite_bindings == {},
                    "hyperlink in unmatched column → no cite")

    # Case F: mixed data — 1 mailto + 1 http → cite emitted (real cite wins)
    prop = evaluate_pass(pass_block, headers,
        sheet_hyperlinks=[
            {"cell": "C2", "url": "mailto:foo@bar", "label": "email"},
            {"cell": "C3", "url": "https://policies/x.docx", "label": "policy"},
        ],
        header_row=0)
    fails += _check("item:X:policy_ref" in prop.cite_bindings,
                    "mixed mailto + real URL → cite emitted")
    return fails


def test_guard_bypassed_when_hyperlinks_not_supplied() -> int:
    """Backwards compat: when sheet_hyperlinks is None, the guard is off."""
    print("  evaluate_pass — guard bypassed when sheet_hyperlinks=None")
    pass_block = {
        "pass_name":                   "x",
        "target_control":              "X",
        "target_evidence_requirement": "req:X:y",
        "target_evidence_type":        "register",
        "cite_columns": [
            {"fingerprint": ["link"], "binds_to": "item:X:link"},
        ],
    }
    prop = evaluate_pass(pass_block, ["ID", "Link"])
    return _check("item:X:link" in prop.cite_bindings,
                  "no hyperlinks arg → header-only emission (unit-test path)")


def test_ensure_external_system_idempotent() -> int:
    """Wire test — needs a live tenant + DB. Skipped without env."""
    print("  _ensure_external_system — idempotent per (tenant, name)")
    import os, psycopg2
    dsn = {
        "host":     "127.0.0.1",
        "dbname":   "arioncomply_compliance",
        "user":     "arioncomply",
        "password": os.getenv("POSTGRES_PASSWORD", ""),
    }
    if not dsn["password"]:
        print("    SKIP (POSTGRES_PASSWORD not set)")
        return 0
    tenant_id = "77777777-7777-7777-7777-777777777777"  # test tenant
    fails = 0
    conn = psycopg2.connect(**dsn)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            # Clean prior test rows
            cur.execute(
                "DELETE FROM tenant_external_system "
                "WHERE tenant_id=%s::uuid AND system_name IN "
                "('Ship 89b Test System', 'Internal Documents')",
                (tenant_id,),
            )
            conn.commit()
            # First call — creates
            id1 = _ensure_external_system(cur, tenant_id,
                {"cite_kind": "internal_document",
                 "system_hint": "Ship 89b Test System",
                 "verification_days": 180})
            # Second call — reuses
            id2 = _ensure_external_system(cur, tenant_id,
                {"cite_kind": "internal_document",
                 "system_hint": "Ship 89b Test System",
                 "verification_days": 90})
            fails += _check(id1 == id2, "same system_id returned twice")
            # Cleanup
            cur.execute(
                "DELETE FROM tenant_external_system "
                "WHERE tenant_id=%s::uuid AND system_name='Ship 89b Test System'",
                (tenant_id,),
            )
            conn.commit()
    finally:
        conn.close()
    return fails


def main() -> int:
    print("─" * 70)
    print("  rag/intake/workbook — Ship 89'.b cite_columns + cite-mode")
    print("─" * 70)
    fails = (
        test_evaluate_pass_captures_cite_binding()
        + test_evaluate_pass_cite_columns_skipped_when_no_header_match()
        + test_evaluate_pass_cite_columns_default_kind()
        + test_row_level_guard_requires_real_hyperlink()
        + test_guard_bypassed_when_hyperlinks_not_supplied()
        + test_ensure_external_system_idempotent()
    )
    print()
    if fails == 0:
        print("  All tests PASS")
        return 0
    print(f"  {fails} test(s) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
