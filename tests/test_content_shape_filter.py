"""
Unit tests for _looks_like_field_or_header — Ship 11'.c content-shape
filter that drops table field labels, section headers, and doc
cross-refs from stage-1 extraction findings.

Targets Patterns 1 (field labels) and 3 (fingerprint fragments) from
the Ship 11'.a taxonomy. Distinct from _looks_like_questionnaire
(Y/N checklists) and _looks_like_metadata_block (Owner/Version
boilerplate) — those are already caught upstream.

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_content_shape_filter.py
"""
from __future__ import annotations

import sys

from rag.intake.extractor import _looks_like_field_or_header, _must_prefix


def _check(label, got, want):
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}  got={got!r} want={want!r}")
    return ok


def test_must_prefix_extraction():
    print("\n_must_prefix — semantic prefix from MUST id")
    fails = 0
    cases = [
        ("item:A.7.2.1:rev_coverage_check",         "rev_"),
        ("item:A.7.2.6:rev_subprocessor_audit",     "rev_"),
        ("item:A.7.2.4:proc_record_fields",         "proc_"),
        ("item:A.7.2.8:ropa_activity_id",           "ropa_"),
        ("item:A.7.2.4:reg_lawful_basis_link",      "reg_"),
        ("item:A.5.15:soa_owner",                   "soa_"),
        ("item:A.5.15:scope_general",               "scope_"),
        ("bare_id_no_colon",                        ""),
        (None,                                      ""),
        ("item:A.5.15:MixedCase",                   ""),  # only lowercase prefixes
    ]
    for must_id, want in cases:
        fails += 0 if _check(repr(must_id), _must_prefix(must_id), want) else 1
    return fails


def test_universal_drops():
    """These shapes drop regardless of MUST binding — section headers
    with cited control refs, and doc cross-references."""
    print("\nuniversal drops (any/no MUST)")
    fails = 0

    # Section header with control-ref parenthetical
    r = _looks_like_field_or_header("Return , Transfer or Deletion of PII (A.8.3.2 / B.8.4.2)")
    fails += 0 if _check("section_header_with_ctrl_refs", r,
                         (True, "section_header_with_ctrl_refs")) else 1

    # Same shape with MUST binding — still drops
    r = _looks_like_field_or_header("Return , Transfer or Deletion of PII (A.8.3.2 / B.8.4.2)",
                                    must_id="item:A.7.3.8:proc_direct_transfer")
    fails += 0 if _check("section_header (with MUST)", r,
                         (True, "section_header_with_ctrl_refs")) else 1

    # Doc cross-reference
    r = _looks_like_field_or_header("Data Subject Rights Handling Procedure (DOC051)")
    fails += 0 if _check("doc_cross_ref", r, (True, "doc_cross_ref")) else 1

    r = _looks_like_field_or_header("See section 2.1 (DOC-014)")
    fails += 0 if _check("doc_cross_ref DOC-014", r, (True, "doc_cross_ref")) else 1

    return fails


def test_table_field_label_must_aware():
    """Table-cell-shape excerpts (3+ consecutive whitespace):
    - Bound to rev_/proc_/other MUST — DROP
    - Bound to reg_/scope_/ropa_ MUST — PRESERVE (RoPA field IS the register field)
    - No MUST binding — DROP (unbound field label is noise)"""
    print("\ntable_field_label — MUST-aware")
    fails = 0

    # Ship 10 rejects (rev_ MUSTs)
    r = _looks_like_field_or_header(
        "Subprocessors   Any third parties involved",
        must_id="item:A.7.2.6:rev_subprocessor_audit",
    )
    fails += 0 if _check("table + rev_ MUST → drop", r,
                         (True, "table_field_label")) else 1

    r = _looks_like_field_or_header(
        "Purpose of Processing   Why the data is being processed",
        must_id="item:A.7.2.1:rev_coverage_check",
    )
    fails += 0 if _check("table + rev_ MUST (Ship 10 mistake) → drop", r,
                         (True, "table_field_label")) else 1

    # Register/scope MUST — preserve
    r = _looks_like_field_or_header(
        "Consent Purpose   e.g., newsletter, usage analytics, third-party marketing",
        must_id="item:A.7.2.4:reg_lawful_basis_link",
    )
    fails += 0 if _check("table + reg_ MUST → preserve", r,
                         (False, "prose")) else 1

    r = _looks_like_field_or_header(
        "Client ID   Unique client identifier",
        must_id="item:B.8.2.6:ropa_customer_id",
    )
    fails += 0 if _check("table + ropa_ MUST → preserve", r,
                         (False, "prose")) else 1

    r = _looks_like_field_or_header(
        "Scope: All PII processing activities   across all business units",
        must_id="item:A.5.15:scope_general",
    )
    fails += 0 if _check("table + scope_ MUST → preserve", r,
                         (False, "prose")) else 1

    # No MUST binding — unbound field label drops
    r = _looks_like_field_or_header("International Transfers   Details of transfers outside")
    fails += 0 if _check("table + no MUST → drop", r,
                         (True, "table_field_label")) else 1

    return fails


def test_prose_preserved():
    """Full prose sentences with sentence terminators — always preserve."""
    print("\nprose — always preserved")
    fails = 0

    cases = [
        # Ship 10 approves
        "Consent records are retained for a minimum of 5 years, or longer if required by applicable regulations, and are securely deleted once retention expires.",
        "Arion Networks provides customers with means to fulfill data subject requests.",
        "This procedure defines how Arion Networks maintains its Records of Processing Activities (RoPA) in accordance with GDPR Article 30.",
        # Prose ending with a period is prose even if it mentions a control ref
        "The organization implements A.5.15 by requiring RBAC for all systems.",
        # Bullet with a full sentence in it — preserve
        "- All consent communications must include a clear and accessible opt-out link.",
    ]
    for text in cases:
        r = _looks_like_field_or_header(text)
        fails += 0 if _check(f"prose: {text[:50]}...", r, (False, "prose")) else 1
    return fails


def test_bullet_fragments():
    """Short bullets without sentence terminators drop as fragments."""
    print("\nbullet_fragment — short list items without periods")
    fails = 0

    # Fragment cases — should drop
    r = _looks_like_field_or_header("- Processing purpose")
    fails += 0 if _check("bare bullet stub", r, (True, "bullet_fragment")) else 1

    r = _looks_like_field_or_header("* Access Control")
    fails += 0 if _check("bare bullet with capital", r, (True, "bullet_fragment")) else 1

    # Bullet WITH terminator — NOT a fragment
    r = _looks_like_field_or_header("- Access rights must be reviewed quarterly.")
    fails += 0 if _check("bullet with period → prose", r, (False, "prose")) else 1

    # Long bullet without period — passes (length threshold means it's not a "short" fragment)
    long_bullet = "- " + "x" * 120
    r = _looks_like_field_or_header(long_bullet)
    fails += 0 if _check("long bullet (>=100c) → prose", r, (False, "prose")) else 1

    return fails


def test_ship10_replay():
    """Replay every unique Ship 10 case that Ship 11'.c targets."""
    print("\nreplay: Ship 10 targeted cases")
    fails = 0

    # Cases 11'.c catches
    catches = [
        ("Subprocessors   Any third parties involved",
         "item:A.7.2.6:rev_subprocessor_audit", "table_field_label"),
        ("Retention Period        Timeframe for keeping the data",
         None, "table_field_label"),
        ("Return , Transfer or Deletion of PII (A.8.3.2 / B.8.4.2)",
         "item:A.7.3.8:proc_direct_transfer", "section_header_with_ctrl_refs"),
        ("Data Subject Rights Handling Procedure (DOC051)",
         None, "doc_cross_ref"),
    ]
    for text, must, expected_reason in catches:
        drop, reason = _looks_like_field_or_header(text, must_id=must)
        fails += 0 if _check(
            f"catch: {expected_reason}", (drop, reason), (True, expected_reason),
        ) else 1

    # Cases 11'.c misses (need Ship 11'.d anchor-semantic filter)
    misses = [
        # Single-space separators — my detector requires 3+ consecutive whitespace
        ("International Transfers Details of transfers outside the EU/EEA, if applicable",
         None, False),
        # Parenthetical with non-ref content — passes control-ref regex
        ("Data Flow Description (collection, storage, sharing, retention)",
         None, False),
    ]
    for text, must, expected_drop in misses:
        drop, reason = _looks_like_field_or_header(text, must_id=must)
        fails += 0 if _check(
            f"miss (expected — waits for 11'.d): {text[:50]}",
            drop, expected_drop,
        ) else 1

    return fails


def main():
    print("─" * 70)
    print("  rag/intake/extractor._looks_like_field_or_header (Ship 11'.c)")
    print("─" * 70)
    fails = (
        test_must_prefix_extraction()
        + test_universal_drops()
        + test_table_field_label_must_aware()
        + test_prose_preserved()
        + test_bullet_fragments()
        + test_ship10_replay()
    )
    print()
    if fails == 0:
        print("  All tests PASS")
        return 0
    print(f"  {fails} test(s) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
