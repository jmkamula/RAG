"""
rag/scoping/sectors.py — Ship 113'.a.

Controlled vocabulary for the `sector` field on client_facts. Loosely
based on NIS 2 Annex I (Essential entities) + Annex II (Important
entities), plus a few common commercial sectors that NIS 2 doesn't
directly enumerate but that customers typically pick.

Storage: `client_facts.sector` is a free-text TEXT column. Ship 113'
doesn't add a CHECK constraint yet — customers might have legacy
non-vocabulary values (e.g. Ship 111'.c PoC put "IT Consulting"
there). A future arc can migrate legacy values + add the constraint.

Reading: any consumer wanting to check "does this tenant belong to
NIS 2 essential entities" should compare `sector` against the codes
here — never against display labels, which may change.

Adding a new sector: append to _SECTORS. Order matters (renders in
the dropdown as-is).
"""
from __future__ import annotations

# Each entry: (code, label, tier)
#   code   — machine identifier, stored in client_facts.sector
#   label  — human display in dropdown
#   tier   — group heading in the dropdown UI. One of:
#              "nis2_essential"   — NIS 2 Annex I
#              "nis2_important"   — NIS 2 Annex II
#              "commercial"       — common non-NIS-2 sectors
#              "other"            — catchall
SECTORS: list[tuple[str, str, str]] = [
    # ── NIS 2 Annex I: Essential entities ────────────────────────
    ("energy",              "Energy (electricity, oil, gas, district heating, hydrogen)",         "nis2_essential"),
    ("transport",           "Transport (air, rail, water, road)",                                 "nis2_essential"),
    ("banking",             "Banking",                                                            "nis2_essential"),
    ("finance_markets",     "Financial market infrastructures",                                   "nis2_essential"),
    ("health",              "Healthcare & pharmaceuticals",                                       "nis2_essential"),
    ("water",               "Drinking water & wastewater",                                        "nis2_essential"),
    ("digital_infra",       "Digital infrastructure (data centres, cloud, DNS/CDN, IXPs)",        "nis2_essential"),
    ("ict_services",        "ICT services (managed service providers, IT, cybersecurity)",       "nis2_essential"),
    ("public_admin",        "Public administration",                                              "nis2_essential"),
    ("space",               "Space",                                                              "nis2_essential"),

    # ── NIS 2 Annex II: Important entities ───────────────────────
    ("postal_courier",      "Postal & courier services",                                          "nis2_important"),
    ("waste_management",    "Waste management",                                                   "nis2_important"),
    ("chemicals",           "Chemicals (production, distribution)",                               "nis2_important"),
    ("food",                "Food (production, processing, distribution)",                        "nis2_important"),
    ("manufacturing",       "Manufacturing (machinery, vehicles, electronics)",                   "nis2_important"),
    ("digital_providers",   "Digital providers (online marketplaces, search engines, social)",   "nis2_important"),
    ("research",            "Research",                                                           "nis2_important"),

    # ── Common commercial sectors outside NIS 2 ──────────────────
    ("retail",              "Retail & consumer services",                                         "commercial"),
    ("professional",        "Professional services (legal, accounting, consulting)",             "commercial"),
    ("nonprofit",           "Non-profit / non-governmental",                                     "commercial"),

    # ── Catchall ─────────────────────────────────────────────────
    ("other",               "Other",                                                              "other"),
]

TIER_LABELS: dict[str, str] = {
    "nis2_essential":  "Essential-service sectors",
    "nis2_important":  "Important-service sectors",
    "commercial":      "Other commercial sectors",
    "other":           "Other",
}

VALID_SECTOR_CODES: frozenset[str] = frozenset(code for code, _, _ in SECTORS)


def is_valid_sector_code(value: str | None) -> bool:
    return bool(value) and value in VALID_SECTOR_CODES
