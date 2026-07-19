"""
Unit tests for rag/output/ — the framework-aware output gateway
(Ship 7'.b, 2026-07-19). See
[[ship-7-prime-a-output-audit-2026-07-19]] +
[[ship-7-prime-b-output-gateway-skeleton-2026-07-19]] for the
design.

Coverage:
  - vocab loader (per-framework JSON)
  - each transform (idempotence + expected shape)
  - gateway.humanize surface routing
  - gateway_guard jargon detection
  - the 2 pilot migration sites (external API + notifications)

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_output_gateway.py
"""
from __future__ import annotations

import sys

from rag.output import (
    UnknownSurface,
    format_standard_id,
    format_standard_id_exact,
    gateway_guard,
    humanize,
    humanize_snake_case,
    scrub_leaf_ids,
    scrub_uuids,
)
from rag.output import vocab


def _check(label: str, got, want) -> bool:
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}  got={got!r} want={want!r}")
    return ok


# ── vocab loader ───────────────────────────────────────────────────

def test_vocab_loader() -> int:
    print("\nvocab loader — per-framework JSON files")
    fails = 0
    ids = set(vocab.all_ids())
    fails += 0 if _check(
        "3 frameworks enrolled",
        {"ISO27001:2022", "ISO27701:2019", "GDPR:2016/679"}.issubset(ids),
        True,
    ) else 1
    fails += 0 if _check("ISO27001 display", vocab.display_name("ISO27001:2022"), "ISO 27001:2022") else 1
    fails += 0 if _check("ISO27701 display", vocab.display_name("ISO27701:2019"), "ISO 27701:2019") else 1
    fails += 0 if _check("GDPR display",     vocab.display_name("GDPR:2016/679"), "GDPR (EU 2016/679)") else 1
    fails += 0 if _check("GDPR short",       vocab.short_name("GDPR:2016/679"),   "GDPR") else 1
    fails += 0 if _check("unknown → self",   vocab.display_name("SOC2:2017"),     "SOC2:2017") else 1
    fails += 0 if _check("unknown w/ fallback", vocab.display_name("SOC2:2017", fallback="SOC 2"), "SOC 2") else 1
    return fails


# ── transforms ─────────────────────────────────────────────────────

def test_format_standard_id() -> int:
    print("\ntransforms.format_standard_id — embedded slugs")
    fails = 0
    fails += 0 if _check(
        "one slug in prose",
        format_standard_id("Framework: ISO27001:2022 clause 6.1.2"),
        "Framework: ISO 27001:2022 clause 6.1.2",
    ) else 1
    fails += 0 if _check(
        "two slugs same string",
        format_standard_id("Bridges ISO27001:2022 → GDPR:2016/679 via Art.32"),
        "Bridges ISO 27001:2022 → GDPR (EU 2016/679) via Art.32",
    ) else 1
    fails += 0 if _check(
        "no slug → unchanged",
        format_standard_id("nothing to see here"),
        "nothing to see here",
    ) else 1
    # Idempotence
    once  = format_standard_id("Framework: ISO27001:2022")
    twice = format_standard_id(once)
    fails += 0 if _check("idempotent", once, twice) else 1
    return fails


def test_format_standard_id_exact() -> int:
    print("\ntransforms.format_standard_id_exact — single slug case")
    fails = 0
    fails += 0 if _check("ISO27001",       format_standard_id_exact("ISO27001:2022"),        "ISO 27001:2022") else 1
    fails += 0 if _check("GDPR full",      format_standard_id_exact("GDPR:2016/679"),        "GDPR (EU 2016/679)") else 1
    fails += 0 if _check("GDPR short",     format_standard_id_exact("GDPR:2016/679", short=True), "GDPR") else 1
    fails += 0 if _check("unknown → self", format_standard_id_exact("SOC2:2017"),            "SOC2:2017") else 1
    fails += 0 if _check("empty → empty",  format_standard_id_exact(""),                     "") else 1
    return fails


def test_humanize_snake_case() -> int:
    print("\ntransforms.humanize_snake_case")
    fails = 0
    fails += 0 if _check(
        "two-word slug",
        humanize_snake_case("Expected action: access_review_required"),
        "Expected action: access review required",
    ) else 1
    fails += 0 if _check(
        "multiple slugs",
        humanize_snake_case("policy_revised triggered offboarding_complete"),
        "policy revised triggered offboarding complete",
    ) else 1
    fails += 0 if _check(
        "single-word left alone (indistinguishable from prose)",
        humanize_snake_case("The policy is active"),
        "The policy is active",
    ) else 1
    # Idempotence
    once  = humanize_snake_case("access_review_required")
    twice = humanize_snake_case(once)
    fails += 0 if _check("idempotent", once, twice) else 1
    return fails


def test_scrub_leaf_ids() -> int:
    print("\ntransforms.scrub_leaf_ids")
    fails = 0
    fails += 0 if _check(
        "leaf id scrubbed",
        scrub_leaf_ids("Update req:A.5.15:access_control_policy today"),
        "Update today",
    ) else 1
    fails += 0 if _check(
        "MUST-item id scrubbed",
        scrub_leaf_ids("Include item:A.5.15:policy_document in the pack"),
        "Include in the pack",
    ) else 1
    fails += 0 if _check(
        "no id → unchanged",
        scrub_leaf_ids("Ordinary prose"),
        "Ordinary prose",
    ) else 1
    # Idempotence
    once  = scrub_leaf_ids("req:A.5.15:foo bar")
    twice = scrub_leaf_ids(once)
    fails += 0 if _check("idempotent", once, twice) else 1
    return fails


def test_scrub_uuids() -> int:
    print("\ntransforms.scrub_uuids")
    fails = 0
    fails += 0 if _check(
        "UUID → ellipsis suffix",
        scrub_uuids("Upload not found: 6c6e7102-846c-4aab-87be-91810c4b191b"),
        "Upload not found: …0c4b191b",
    ) else 1
    fails += 0 if _check(
        "no UUID → unchanged",
        scrub_uuids("Regular text"),
        "Regular text",
    ) else 1
    # Idempotence
    once  = scrub_uuids("id 6c6e7102-846c-4aab-87be-91810c4b191b")
    twice = scrub_uuids(once)
    fails += 0 if _check("idempotent", once, twice) else 1
    return fails


# ── gateway.humanize surface routing ───────────────────────────────

def test_surface_routing() -> int:
    print("\ngateway.humanize — surface routing")
    fails = 0
    fails += 0 if _check(
        "notification_title chain",
        humanize("Overdue: A.5.15 requires access_review_required", surface="notification_title"),
        "Overdue: A.5.15 requires access review required",
    ) else 1
    fails += 0 if _check(
        "notification_body scrubs UUID",
        humanize(
            "Failed upload 6c6e7102-846c-4aab-87be-91810c4b191b in ISO27001:2022 review",
            surface="notification_body",
        ),
        "Failed upload …0c4b191b in ISO 27001:2022 review",
    ) else 1
    fails += 0 if _check(
        "stage2_reason scrubs leaf id + humanises slug + formats std",
        humanize(
            "req:A.5.15:policy — expected access_review_required under ISO27001:2022",
            surface="stage2_reason",
        ),
        "— expected access review required under ISO 27001:2022",
    ) else 1

    # Explicit transforms subset (bypass surface default)
    fails += 0 if _check(
        "custom transform subset",
        humanize(
            "Trace 6c6e7102-846c-4aab-87be-91810c4b191b for req:A.5.15:x",
            surface="unregistered_but_ok",
            transforms=["scrub_uuids"],
        ),
        "Trace …0c4b191b for req:A.5.15:x",
    ) else 1

    # Unknown surface without explicit transforms → fail loud
    try:
        humanize("x", surface="not_a_real_surface")
        fails += 1
        print("  [FAIL] unknown surface should raise UnknownSurface")
    except UnknownSurface:
        print("  [PASS] unknown surface raises UnknownSurface")

    # Empty input
    fails += 0 if _check("empty → empty",  humanize("", surface="notification_title"), "") else 1
    fails += 0 if _check("None → None",    humanize(None, surface="notification_title"), None) else 1

    return fails


# ── gateway_guard ──────────────────────────────────────────────────

def test_gateway_guard() -> int:
    print("\ngateway_guard — jargon linter (warn-only)")
    fails = 0
    events = gateway_guard(
        "Overdue: A.5.15 requires access_review_required at req:A.5.15:policy for GDPR:2016/679"
    )
    kinds = sorted(e["kind"] for e in events)
    fails += 0 if _check(
        "detects 3 jargon kinds",
        kinds,
        ["leaf_id", "raw_standard_id", "snake_case_slug"],
    ) else 1
    fails += 0 if _check("clean prose → []",     gateway_guard("Ordinary prose with A.5.15 refs."), []) else 1
    fails += 0 if _check("empty → []",           gateway_guard(""), []) else 1

    # Post-humanize should be clean (round-trip)
    dirty = "Overdue: A.5.15 requires access_review_required"
    clean = humanize(dirty, surface="notification_title")
    fails += 0 if _check(
        "post-humanize guard clean",
        [e["kind"] for e in gateway_guard(clean) if e["kind"] != "raw_standard_id"],
        [],
    ) else 1
    return fails


# ── Pilot integration checks ───────────────────────────────────────

def test_pilot_1_external_api() -> int:
    print("\npilot 1: external API — PostureControl.standard_display")
    from rag.external.endpoints.posture import _standard_display
    fails = 0
    fails += 0 if _check("ISO 27001 display", _standard_display("ISO27001:2022"), "ISO 27001:2022") else 1
    fails += 0 if _check("ISO 27701 display", _standard_display("ISO27701:2019"), "ISO 27701:2019") else 1
    fails += 0 if _check("GDPR display",      _standard_display("GDPR:2016/679"), "GDPR (EU 2016/679)") else 1
    fails += 0 if _check("unknown pass-thru", _standard_display("SOC2:2017"),      "SOC2:2017") else 1
    return fails


def test_evidence_prose_surface() -> int:
    """Ship 7'.c — new `evidence_prose` surface for Evidence Package
    obligation prose. Scrubs leaf ids, humanises snake_case, formats
    standard ids."""
    print("\nsurface: evidence_prose (Ship 7'.c)")
    out = humanize(
        "This obligation lives under ISO27001:2022 A.5.15. See "
        "req:A.5.15:access_control_policy for the artefact map. "
        "It requires access_review_required within 24h.",
        surface="evidence_prose",
    )
    fails = 0
    fails += 0 if _check(
        "evidence_prose chain",
        out,
        # scrubbed leaf id + humanised slug + formatted std
        "This obligation lives under ISO 27001:2022 A.5.15. See "
        "for the artefact map. It requires access review required within 24h.",
    ) else 1
    return fails


def test_cascade_migration() -> int:
    """Ship 7'.c — cascade endpoint fields humanised through gateway."""
    print("\nmigration: cascade endpoint slugs + rationale (Ship 7'.c)")
    fails = 0
    fails += 0 if _check(
        "event_type_display",
        humanize("policy_revised", surface="cascade_rationale"),
        "policy revised",
    ) else 1
    fails += 0 if _check(
        "expected_action_display",
        humanize("access_review_required", surface="cascade_rationale"),
        "access review required",
    ) else 1
    fails += 0 if _check(
        "rationale scrubbed",
        humanize(
            "Triggered by nc_finding on ISO27001:2022 A.5.15; "
            "expected access_review_required within window.",
            surface="cascade_rationale",
        ),
        "Triggered by nc finding on ISO 27001:2022 A.5.15; "
        "expected access review required within window.",
    ) else 1
    return fails


def test_error_uuid_migration() -> int:
    """Ship 7'.c — HTTPException detail with UUID scrubbed."""
    print("\nmigration: error_detail UUID scrub (Ship 7'.c)")
    result = humanize(
        "We couldn't find that upload (6c6e7102-846c-4aab-87be-91810c4b191b) for your tenant.",
        surface="error_detail",
    )
    return 0 if _check(
        "UUID → suffix",
        result,
        "We couldn't find that upload (…0c4b191b) for your tenant.",
    ) else 1


def test_pilot_2_notification_bodies() -> int:
    print("\npilot 2: notifications — action verbs humanised")
    fails = 0
    # Simulate what tick.py builds after the migration.
    title = humanize(
        f"Overdue: A.5.15 requires access_review_required",
        surface="notification_title",
    )
    body = humanize(
        f"A cascade follow-up on A.5.15 is past due. "
        f"Expected action: access_review_required. Depth 2 in the cascade path.",
        surface="notification_body",
    )
    fails += 0 if _check(
        "title humanised",
        title,
        "Overdue: A.5.15 requires access review required",
    ) else 1
    fails += 0 if _check(
        "body humanised",
        body,
        "A cascade follow-up on A.5.15 is past due. "
        "Expected action: access review required. Depth 2 in the cascade path.",
    ) else 1
    # gateway_guard on the migrated output should NOT flag snake_case
    # in these strings.
    events = [e for e in gateway_guard(title) if e["kind"] == "snake_case_slug"]
    fails += 0 if _check("title has no snake_case", events, []) else 1
    return fails


def main() -> int:
    print("─" * 70)
    print("  rag/output — framework-aware output gateway (Ship 7'.b)")
    print("─" * 70)
    fails = (
        test_vocab_loader()
        + test_format_standard_id()
        + test_format_standard_id_exact()
        + test_humanize_snake_case()
        + test_scrub_leaf_ids()
        + test_scrub_uuids()
        + test_surface_routing()
        + test_gateway_guard()
        + test_pilot_1_external_api()
        + test_evidence_prose_surface()
        + test_cascade_migration()
        + test_error_uuid_migration()
        + test_pilot_2_notification_bodies()
    )
    print()
    if fails == 0:
        print("  All tests PASS")
        return 0
    print(f"  {fails} test(s) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
