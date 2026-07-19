"""
Unit tests for rag/casefile/claim_scan.py — Ship 6'.d passive
claim-scan observability. See
[[ship-6-prime-d-claim-scan-observability-2026-07-19]].

The scanner classifies normative-verb claims in LLM chat prose into
three kinds (direct / prepositional / generic) and enriches each
with `ref_in_digest` + `standard_in_scope` signals. Fully passive
— never blocks a response, never rewrites answer text.

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_claim_scan.py
"""
from __future__ import annotations

import sys
from types import SimpleNamespace

from rag.casefile.claim_scan import (
    ClaimEvent,
    _canonicalise_ref,
    _standard_family,
    claims_to_json,
    scan_claims,
)


def _cf(digest_refs: list[str] | None = None, scope: list[str] | None = None):
    """Minimal duck-typed case-file for the scanner tests."""
    refs = digest_refs or []
    nodes = [SimpleNamespace(ref=r) for r in refs]
    return SimpleNamespace(
        posture_by_ref=lambda: {r: {"finding": "NC"} for r in refs},
        all_nodes=lambda: nodes,
        scope_standards=scope or ["ISO27001:2022", "GDPR:2016/679"],
    )


def _check(label: str, got, want) -> bool:
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}  got={got!r} want={want!r}")
    return ok


def test_canonicalise_ref() -> int:
    print("\n_canonicalise_ref")
    fails = 0
    fails += 0 if _check("'Art. 32' → 'Art.32'",  _canonicalise_ref("Art. 32"),        "Art.32") else 1
    fails += 0 if _check("'Art.  5'  → 'Art.5'",  _canonicalise_ref("Art.  5"),        "Art.5") else 1
    fails += 0 if _check("'A.5.18' stays",         _canonicalise_ref("A.5.18"),        "A.5.18") else 1
    fails += 0 if _check("'ISO   27001' compress", _canonicalise_ref("ISO   27001"),   "ISO 27001") else 1
    return fails


def test_standard_family() -> int:
    print("\n_standard_family")
    fails = 0
    fails += 0 if _check("Art.32 → GDPR",           _standard_family("Art.32"),        "GDPR:2016/679") else 1
    fails += 0 if _check("A.5.18 → ISO27001",       _standard_family("A.5.18"),        "ISO27001:2022") else 1
    fails += 0 if _check("6.1.2 → ISO27001 (ISMS)", _standard_family("6.1.2"),         "ISO27001:2022") else 1
    fails += 0 if _check("ISO 27701 → 27701",       _standard_family("ISO 27701"),     "ISO27701:2019") else 1
    fails += 0 if _check("bare GDPR → GDPR",        _standard_family("GDPR"),          "GDPR:2016/679") else 1
    fails += 0 if _check("nonsense → None",         _standard_family("xyz"),           None) else 1
    return fails


def test_direct_pattern() -> int:
    print("\nscan_claims — direct pattern ('REF requires X')")
    cf = _cf(digest_refs=["Art.32", "A.5.18"])
    text = "Art. 32 requires appropriate technical and organisational measures."
    events = scan_claims(text, cf)
    fails = 0
    fails += 0 if _check("1 event",                 len(events), 1) else 1
    if len(events) == 1:
        ev = events[0]
        fails += 0 if _check("ref canonicalised",   ev.ref,             "Art.32") else 1
        fails += 0 if _check("verb captured",       ev.verb,            "requires") else 1
        fails += 0 if _check("ref_in_digest",       ev.ref_in_digest,   True) else 1
        fails += 0 if _check("standard_in_scope",   ev.standard_in_scope, True) else 1
        fails += 0 if _check("kind='direct'",       ev.kind,            "direct") else 1
    return fails


def test_direct_pattern_ref_not_in_digest() -> int:
    print("\nscan_claims — direct pattern with ref NOT in digest (risky)")
    cf = _cf(digest_refs=["A.5.18"])   # Art.32 NOT present
    text = "Art.32 requires encryption at rest for personal data."
    events = scan_claims(text, cf)
    fails = 0
    fails += 0 if _check("1 event",                 len(events), 1) else 1
    if len(events) == 1:
        ev = events[0]
        fails += 0 if _check("ref_in_digest FALSE", ev.ref_in_digest, False) else 1
        # scope IS present (GDPR is a default enrolled framework in _cf)
        fails += 0 if _check("standard_in_scope TRUE (family in scope)", ev.standard_in_scope, True) else 1
    return fails


def test_prepositional_pattern() -> int:
    print("\nscan_claims — prepositional ('under REF, ...')")
    cf = _cf(digest_refs=["Art.32"])
    text = "Under Art.32, both controllers and processors must implement TOMs."
    events = scan_claims(text, cf)
    fails = 0
    fails += 0 if _check("1 event",                 len(events), 1) else 1
    if len(events) == 1:
        ev = events[0]
        fails += 0 if _check("kind='prepositional'", ev.kind,        "prepositional") else 1
        fails += 0 if _check("verb captures 'under'", ev.verb,       "under") else 1
        fails += 0 if _check("ref_in_digest",        ev.ref_in_digest, True) else 1
    return fails


def test_generic_pattern() -> int:
    print("\nscan_claims — generic ('the standard requires X') — untethered")
    cf = _cf()
    text = "The standard requires quarterly access reviews."
    events = scan_claims(text, cf)
    fails = 0
    fails += 0 if _check("1 event",                 len(events), 1) else 1
    if len(events) == 1:
        ev = events[0]
        fails += 0 if _check("kind='generic'",     ev.kind,          "generic") else 1
        fails += 0 if _check("ref=None (untethered)", ev.ref,         None) else 1
        fails += 0 if _check("ref_in_digest FALSE",  ev.ref_in_digest, False) else 1
    return fails


def test_no_claim_no_events() -> int:
    print("\nscan_claims — non-normative prose fires nothing")
    cf = _cf(digest_refs=["A.5.18", "Art.32"])
    text = "Your posture on A.5.18 is NC-DRAFT. Art.32 was cited in the recent bridge footer."
    # No normative-verb claim here — the LLM is describing tenant state.
    events = scan_claims(text, cf)
    return 0 if _check("0 events on descriptive prose", len(events), 0) else 1


def test_multiple_claims_in_one_answer() -> int:
    print("\nscan_claims — multiple claim styles in one answer")
    cf = _cf(digest_refs=["Art.32", "A.5.18"])
    text = (
        "Art. 32 requires TOMs to ensure a level of security appropriate to risk. "
        "Under A.5.18, access rights must be reviewed. "
        "The regulation mandates a 72-hour breach notification window."
    )
    events = scan_claims(text, cf)
    fails = 0
    fails += 0 if _check("3 events", len(events), 3) else 1
    kinds = sorted(e.kind for e in events)
    fails += 0 if _check("kinds", kinds, ["direct", "generic", "prepositional"]) else 1
    return fails


def test_empty_and_edge_cases() -> int:
    print("\nscan_claims — edge cases")
    cf = _cf()
    fails = 0
    fails += 0 if _check("empty string → []",  scan_claims("", cf),   []) else 1
    fails += 0 if _check("None → []",          scan_claims(None, cf), []) else 1
    return fails


def test_claims_to_json_shape() -> int:
    print("\nclaims_to_json")
    cf = _cf(digest_refs=["Art.32"])
    events = scan_claims("Art. 32 requires technical and organisational measures.", cf)
    js = claims_to_json(events)
    fails = 0
    fails += 0 if _check("1 dict",                    len(js),                    1) else 1
    if js:
        row = js[0]
        fails += 0 if _check("has 'ref'",             row.get("ref"),             "Art.32") else 1
        fails += 0 if _check("has 'verb'",            row.get("verb"),            "requires") else 1
        fails += 0 if _check("has 'kind'",            row.get("kind"),            "direct") else 1
        fails += 0 if _check("has ref_in_digest",     row.get("ref_in_digest"),   True) else 1
        fails += 0 if _check("has standard_in_scope", row.get("standard_in_scope"), True) else 1
        fails += 0 if _check("snippet is a string",   isinstance(row.get("snippet"), str), True) else 1
    return fails


def main() -> int:
    print("─" * 70)
    print("  rag/casefile/claim_scan — passive normative-claim scanner")
    print("─" * 70)
    fails = (
        test_canonicalise_ref()
        + test_standard_family()
        + test_direct_pattern()
        + test_direct_pattern_ref_not_in_digest()
        + test_prepositional_pattern()
        + test_generic_pattern()
        + test_no_claim_no_events()
        + test_multiple_claims_in_one_answer()
        + test_empty_and_edge_cases()
        + test_claims_to_json_shape()
    )
    print()
    if fails == 0:
        print("  All tests PASS")
        return 0
    print(f"  {fails} test(s) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
