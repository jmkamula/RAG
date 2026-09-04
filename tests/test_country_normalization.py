"""
Ship 112'.a — country normalization regression tests.

Reproduces the exact Ship 111'.c PoC deployment bug: Ship 104's
free-text Quickstart form captured `country="Czechia"`. Ship 110'.b's
`_initial_client_facts()` compared against `_EU_EEA_COUNTRIES`
(ISO alpha-2 codes) and the string mismatch silently skipped the
eu_data_subjects derivation.

Locks in the fix: display names and common variants must normalize
to canonical ISO 3166-1 alpha-2 codes before the derivation runs.
"""
from __future__ import annotations
from rag.onboarding.quickstart import (
    _normalize_country,
    _initial_client_facts,
)


def test_normalize_display_name_to_iso_code():
    """The exact Ship 111'.c bug — `"Czechia"` → `"CZ"`."""
    assert _normalize_country("Czechia") == "CZ"
    assert _normalize_country("Czech Republic") == "CZ"
    assert _normalize_country("czech republic") == "CZ"


def test_normalize_uk_variants():
    """`"UK"` is a common 2-letter shortcut but not an ISO code —
    must map to `"GB"`. Regression: if the length-2 shortcut runs
    first, we return `"UK"` verbatim.
    """
    assert _normalize_country("UK") == "GB"
    assert _normalize_country("uk") == "GB"
    assert _normalize_country("United Kingdom") == "GB"
    assert _normalize_country("Great Britain") == "GB"


def test_normalize_us_variants():
    assert _normalize_country("USA") == "US"
    assert _normalize_country("United States") == "US"
    assert _normalize_country("United States of America") == "US"


def test_normalize_iso_codes_passthrough():
    """Already-canonical inputs stay unchanged (up-cased)."""
    assert _normalize_country("CZ") == "CZ"
    assert _normalize_country("cz") == "CZ"
    assert _normalize_country("DE") == "DE"
    assert _normalize_country("US") == "US"


def test_normalize_whitespace_and_case_insensitive():
    assert _normalize_country("  Belgium  ") == "BE"
    assert _normalize_country("BELGIUM") == "BE"
    assert _normalize_country("belgium") == "BE"


def test_normalize_empty_and_null():
    assert _normalize_country("") == ""
    assert _normalize_country(None) == ""
    assert _normalize_country("   ") == ""


def test_normalize_unknown_fails_open():
    """Unknown input passes through unchanged — never crashes."""
    assert _normalize_country("Neverland") == "Neverland"
    assert _normalize_country("Wakanda") == "Wakanda"


def test_initial_client_facts_derives_eu_from_display_name():
    """End-to-end: Ship 111'.c bug scenario. `"Czechia"` from the
    free-text form → CZ stored + eu_data_subjects derived.
    """
    values, sources = _initial_client_facts(
        sector="IT Consulting", country="Czechia", cloud_only=True,
    )
    assert values["country"] == "CZ"
    assert values.get("eu_data_subjects") is True
    assert sources["eu_data_subjects"]["source"] == "derived"
    assert sources["eu_data_subjects"]["from"] == "country"


def test_initial_client_facts_derives_uk_from_display_name():
    values, sources = _initial_client_facts(
        sector=None, country="United Kingdom", cloud_only=False,
    )
    assert values["country"] == "GB"
    assert values.get("uk_data_subjects") is True
    # GB is post-Brexit, NOT in EU/EEA
    assert values.get("eu_data_subjects") is None
    assert sources["uk_data_subjects"]["source"] == "derived"


def test_initial_client_facts_us_no_derivations():
    """US tenant — no EU/UK subject derivations, but country still
    normalizes correctly and gets `declared` source marker.
    """
    values, sources = _initial_client_facts(
        sector="technology", country="USA", cloud_only=True,
    )
    assert values["country"] == "US"
    assert values.get("eu_data_subjects") is None
    assert values.get("uk_data_subjects") is None
    assert sources["country"]["source"] == "declared"


if __name__ == "__main__":
    test_normalize_display_name_to_iso_code()
    test_normalize_uk_variants()
    test_normalize_us_variants()
    test_normalize_iso_codes_passthrough()
    test_normalize_whitespace_and_case_insensitive()
    test_normalize_empty_and_null()
    test_normalize_unknown_fails_open()
    test_initial_client_facts_derives_eu_from_display_name()
    test_initial_client_facts_derives_uk_from_display_name()
    test_initial_client_facts_us_no_derivations()
    print("OK — all country normalization tests pass")
