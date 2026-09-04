"""
rag/scoping/regions.py — Ship 113'.a.

Two canonical maps for the 6 region buckets on client_facts:
  · ISO alpha-2 country code → region key (used by _initial_client_facts
    to derive the *_data_subjects boolean when Quickstart tells us
    where the tenant itself is registered)
  · region key → (client_facts column name, human label) used by the
    Profile scoping section renderer to build the multi-select

Region keys are the middle segment of the column name so
`_REGION_COLUMN["eu"] == "eu_data_subjects"`. Adding a new region
means: append to _REGION_LABELS + add a column via a new migration.

Not every country needs to be listed — unknown countries fall into
`other` at derivation time.
"""
from __future__ import annotations

# ── Region metadata ─────────────────────────────────────────────────

REGION_LABELS: list[tuple[str, str]] = [
    ("eu",    "European Union / European Economic Area"),
    ("uk",    "United Kingdom"),
    ("us",    "United States"),
    ("ca",    "Canada"),
    ("apac",  "Asia-Pacific"),
    ("other", "Latin America, Africa, Middle East, or other"),
]

REGION_KEYS: tuple[str, ...] = tuple(k for k, _ in REGION_LABELS)

REGION_COLUMN: dict[str, str] = {k: f"{k}_data_subjects" for k in REGION_KEYS}

# ── ISO country code → region key ───────────────────────────────────
#
# Coverage:
#   · EU (27) + EEA (3)                                → "eu"
#   · United Kingdom                                    → "uk"
#   · United States                                     → "us"
#   · Canada                                            → "ca"
#   · Asia-Pacific major economies + AU/NZ              → "apac"
#   · Everything else (LatAm, Africa, Middle East, ...)  → "other"
#     via fallback: any country not listed here.

_EU_EEA = {
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
    "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT",
    "NL", "PL", "PT", "RO", "SE", "SI", "SK",
    "IS", "LI", "NO",   # EEA additions
}
_APAC = {
    "AU", "NZ", "JP", "SG", "IN", "KR", "TW", "HK", "MO",
    "TH", "VN", "PH", "MY", "ID", "CN", "BD", "PK", "LK",
}

COUNTRY_TO_REGION: dict[str, str] = {}
for _c in _EU_EEA:  COUNTRY_TO_REGION[_c] = "eu"
COUNTRY_TO_REGION["GB"] = "uk"
COUNTRY_TO_REGION["US"] = "us"
COUNTRY_TO_REGION["CA"] = "ca"
for _c in _APAC:    COUNTRY_TO_REGION[_c] = "apac"


def region_of_country(iso_alpha2: str | None) -> str | None:
    """Return region key for an ISO alpha-2 country code.

    Returns None on empty/None input so caller can decide whether to
    treat that as "unknown" (skip derivation) or "other" (declare).
    """
    if not iso_alpha2:
        return None
    code = iso_alpha2.strip().upper()
    if not code:
        return None
    return COUNTRY_TO_REGION.get(code, "other")
