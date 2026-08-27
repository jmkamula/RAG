"""
Ship 98'.a — Chat-scope diagnostic matrix.

Dogfood every question_type on scoped vs program queries.
Capture: classified type, related_cards count, related_cards refs.

The bloat pattern (Ship 97'.b/c): scoped queries hitting the DEFAULT
plan get top-N NCs across the tenant's program mixed into their
related-cards output — because preservation.required_refs unions
cited + top-N posture + top-N obligation, and digest posture_limit=10.

This diagnostic isolates which (question_type, shape) cells actually
exhibit that bloat. Output is a table the operator can eyeball to
choose between (A) enumerated per-intent gates in _plan_for or
(B) an explicit question_shape enum.

Run against local API. API must be up on port 8080 with
`arion_dev_key_2026` key.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Iterable
from urllib import request as ureq
from urllib.error import URLError


API_URL = "http://localhost:8080/api/v1/chat"
API_KEY = "arion_dev_key_2026"


# Test matrix. Each row: (label, expected_intent_hint, query).
# Two rows per intent: one "scoped" (with cited ref) + one "program"
# (no ref). Some intents skip a shape when it doesn't fit.
QUERIES: list[tuple[str, str, str]] = [
    # ── DEFINITION ────────────────────────────────────────────────────
    ("DEFINITION scoped",  "definition",
     "what does A.5.18 say?"),
    ("DEFINITION topic",   "definition",
     "what is access control?"),

    # ── IMPLEMENTATION (Ship 97'.b/c already scoped) ──────────────────
    ("IMPLEMENTATION scoped", "implementation",
     "how do I remediate 7.2?"),
    ("IMPLEMENTATION topic",  "implementation",
     "how do I implement access controls?"),
    ("IMPLEMENTATION program","implementation",
     "what should I work on next?"),

    # ── GAP_ANALYSIS ─────────────────────────────────────────────────
    ("GAP_ANALYSIS scoped",  "gap_analysis",
     "what are my gaps for 7.2?"),
    ("GAP_ANALYSIS topic",   "gap_analysis",
     "what are our access rights gaps?"),
    ("GAP_ANALYSIS program", "gap_analysis",
     "what are our main compliance gaps?"),

    # ── POSTURE_CHECK ────────────────────────────────────────────────
    ("POSTURE_CHECK scoped",  "posture_check",
     "am I compliant with A.5.18?"),
    ("POSTURE_CHECK topic",   "posture_check",
     "am I compliant with access controls?"),
    ("POSTURE_CHECK program", "posture_check",
     "am I compliant?"),

    # ── CROSS_FRAMEWORK ──────────────────────────────────────────────
    ("CROSS_FRAMEWORK scoped",  "cross_framework",
     "how does A.5.15 relate to GDPR?"),
    ("CROSS_FRAMEWORK topic",   "cross_framework",
     "how does ISO 27001 access relate to GDPR?"),

    # ── FREE_ASSESSMENT ──────────────────────────────────────────────
    ("FREE_ASSESSMENT topic",   "free_assessment",
     "where do I stand on access?"),
    ("FREE_ASSESSMENT program", "free_assessment",
     "where do I stand overall?"),

    # ── DOCUMENT_CONTENT (mostly short-circuits) ─────────────────────
    ("DOCUMENT_CONTENT scoped", "document_content",
     "what must an access control policy contain?"),
]


def _post_chat(query: str, timeout: int = 90) -> dict | None:
    body = json.dumps({"question": query}).encode("utf-8")
    req = ureq.Request(
        API_URL,
        data    = body,
        method  = "POST",
        headers = {
            "X-API-Key":    API_KEY,
            "Content-Type": "application/json",
        },
    )
    try:
        with ureq.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"    !!  request failed: {e}", file=sys.stderr)
        return None


def _extract(resp: dict) -> tuple[str, int, list[str], int, bool]:
    """(question_type, n_related_cards, related_refs, n_starters, has_narrative_refs)."""
    qt = resp.get("type", "")
    structured = resp.get("answer_structured") or {}
    related = structured.get("related") or []
    starters = ((resp.get("templates") or {}).get("leaves") or [])
    intro = structured.get("intro") or {}
    prose_refs = bool((intro.get("text") or "").strip())
    return (
        qt,
        len(related),
        [r.get("ref") for r in related if r.get("ref")],
        len(starters),
        prose_refs,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pause", type=float, default=1.5,
                    help="seconds between requests")
    args = ap.parse_args()

    print(f"{'Label':40} {'qtype':18} {'#cards':>6} {'#starters':>9}  refs")
    print("-" * 120)

    rows: list[dict] = []
    for label, hint, query in QUERIES:
        print(f"  · {label}: {query!r}")
        resp = _post_chat(query)
        if resp is None:
            continue
        qt, n_cards, refs, n_starters, prose_has_intro = _extract(resp)
        rows.append({
            "label": label, "hint": hint, "query": query,
            "qtype": qt, "n_cards": n_cards,
            "refs": refs, "n_starters": n_starters,
        })
        # Show inline
        refs_str = ", ".join(refs[:8]) + ("..." if len(refs) > 8 else "")
        print(f"    → {qt:18} cards={n_cards:>3}  starters={n_starters:>3}  refs=[{refs_str}]")
        time.sleep(args.pause)

    # Summary table
    print()
    print("=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print(f"{'Label':38} {'expected → actual':30} {'#cards':>6} {'#starters':>9}  refs (first 6)")
    print("-" * 120)
    for r in rows:
        expected = r["hint"]
        actual = r["qtype"]
        match = "✓" if actual == expected else "✗"
        flag = f"{expected:14} → {actual:12} {match}"
        refs_str = ", ".join(r["refs"][:6]) + ("..." if len(r["refs"]) > 6 else "")
        print(f"{r['label']:38} {flag:30} {r['n_cards']:>6} {r['n_starters']:>9}  {refs_str}")

    # Bloat heuristic: any query with >3 related cards is a bloat candidate.
    print()
    print("Bloat candidates (>3 related cards):")
    for r in rows:
        if r["n_cards"] > 3:
            print(f"  • {r['label']} ({r['qtype']}): {r['n_cards']} cards — {', '.join(r['refs'])}")

    print()
    print(f"Total rows: {len(rows)}. Bloat candidates: {sum(1 for r in rows if r['n_cards'] > 3)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
