"""
ArionComply — Auto-generate MUST fingerprint YAMLs for ISO 27701

Fills the curation gap flagged 2026-07-06: fingerprint catalog covers
310 leaves for ISO 27001 but ZERO for ISO 27701's 196 leaves. Without
27701 fingerprints, the LLM-free stage 4-5 classifier can't produce
direct 27701 findings — those still fall through to the LLM (which
biases to ISO 27001 for privacy content).

Generator strategy:
  Two keyword sets per MUST, both derived deterministically from the
  catalog:

  Set 1: Tokens from the MUST id
    'item:A.7.2.1:scope_activities' → [scope, activities]
  Set 2: Multi-word phrase from the MUST text (first meaningful
    tokens after stopword removal, capped at 4)
    'In-scope processing activities enumerated' → [scope, processing,
     activities, enumerated]

  These are intentionally NOT tuned for the specific policy language
  a tenant might use. Auto-generated fingerprints WILL produce false
  positives + miss synonym-only mentions; that's the trade-off for
  coverage vs hand-authored precision. Hand-refinement per leaf can
  follow as a separate curation pass.

Idempotent: overwrites existing 27701 fingerprint YAMLs on each run.

Usage:
  PYTHONPATH=/data/arioncomply python3 scripts/generate_27701_fingerprints.py
  PYTHONPATH=/data/arioncomply python3 scripts/generate_27701_fingerprints.py --dry-run
"""
from __future__ import annotations
import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv("/data/arioncomply/.env")

_CATALOG_DIR = Path("/data/arioncomply/db/must_fingerprints")

# Tokens NOT meaningful as fingerprint keywords. Auto-generated sets
# with these stripped tend to match too loosely.
_STOP = {
    "the", "a", "an", "and", "or", "but", "of", "for", "in", "on",
    "at", "to", "from", "with", "by", "as", "is", "are", "was",
    "were", "be", "been", "being", "this", "that", "these", "those",
    "it", "its", "which", "who", "whom", "whose", "what", "when",
    "where", "why", "how", "each", "every", "any", "all", "some",
    "no", "not", "will", "would", "should", "could", "may", "might",
    "must", "shall", "can", "have", "has", "had", "do", "does", "did",
    "per", "eg", "e", "g", "ie", "vs", "than", "then", "if", "so",
    "such", "into", "onto", "over", "under", "before", "after",
    "during", "while", "since", "until", "against", "between",
    "through", "without", "within", "along", "across", "toward",
    "against", "using", "used", "use",
    # Common English function words specific to catalog language
    "including", "included", "includes", "including", "provide",
    "provides", "provided", "provider", "given", "give",
}

# Minimum token length after stop-word removal. Single letters like
# "p" or "e" match too many things.
_MIN_TOKEN_LEN = 3

# Common MUST-id prefixes that are semantic noise (they classify the
# SHAPE of the MUST — procedure/register/review/etc — not its content).
# Stripped before token-set assembly.
_ID_PREFIX_NOISE = {
    "proc", "rev", "reg", "cite", "req", "item",
    "must", "should", "shall", "ind", "op",
}

# Minimum tokens per keyword set. Single-token sets match too broadly
# (e.g. [update] matches any doc discussing any kind of update).
_MIN_SET_SIZE = 2


def _tokenize(text: str) -> list[str]:
    """Normalize + tokenize a string. Returns lowercased word tokens
    with stopwords + short tokens removed."""
    if not text:
        return []
    # Replace non-word chars with space so hyphenated words split
    normalized = re.sub(r"[^\w]", " ", str(text).lower())
    tokens = [t for t in normalized.split() if t]
    return [
        t for t in tokens
        if t not in _STOP and len(t) >= _MIN_TOKEN_LEN and not t.isdigit()
    ]


def _tokens_from_must_id(must_id: str) -> list[str]:
    """`item:A.7.2.1:scope_activities` → [scope, activities].
    Strips id-prefix noise (proc/rev/reg/etc — shape markers, not
    content)."""
    parts = must_id.split(":")
    if len(parts) < 3:
        return []
    slug = parts[-1]
    tokens = _tokenize(slug.replace("_", " "))
    return [t for t in tokens if t not in _ID_PREFIX_NOISE]


def _tokens_from_must_text(text: str, max_tokens: int = 4) -> list[str]:
    """First meaningful phrase from the MUST description text. Caps at
    `max_tokens` to keep the ANDed keyword set tight."""
    if not text:
        return []
    # Take the first phrase before em-dash / hyphen / parenthesis
    first_phrase = re.split(r"[—–\-\(]", text, maxsplit=1)[0].strip()
    tokens = _tokenize(first_phrase)
    return tokens[:max_tokens]


def _build_keyword_sets(must_id: str, must_text: str) -> list[list[str]]:
    """Compose up to 2 keyword sets per MUST. Deduplicated and
    filtered to non-trivial sets (≥1 meaningful token)."""
    sets: list[list[str]] = []
    seen: set[tuple] = set()

    for candidate in (
        _tokens_from_must_id(must_id),
        _tokens_from_must_text(must_text),
    ):
        if not candidate or len(candidate) < _MIN_SET_SIZE:
            continue
        key = tuple(sorted(candidate))
        if key in seen:
            continue
        seen.add(key)
        sets.append(candidate)

    return sets


def _yaml_filename(leaf_id: str) -> str:
    """`req:A.7.2.1:applicable_scope` → `req_A_7_2_1_applicable_scope.yaml`."""
    slug = leaf_id.replace("req:", "").replace(".", "_").replace(":", "_")
    return f"req_{slug}.yaml"


def _yaml_content(
    leaf_id: str, target_control: str, target_standard: str,
    must_fingerprints: list[dict],
) -> str:
    lines: list[str] = []
    lines.append(f"# Per-MUST fingerprint catalog for {leaf_id}")
    lines.append("#")
    lines.append("# Auto-generated 2026-07-06 by scripts/generate_27701_fingerprints.py")
    lines.append("# from catalog MUST ids + text. Suitable for coarse coverage;")
    lines.append("# hand-refinement per leaf recommended for tight precision.")
    lines.append("")
    lines.append("schema_version: 1")
    lines.append(f'target_evidence_requirement: "{leaf_id}"')
    lines.append(f'target_control: "{target_control}"')
    lines.append(f'target_standard: "{target_standard}"')
    lines.append("")
    lines.append("must_fingerprints:")

    for m in must_fingerprints:
        lines.append(f'  - must_id: "{m["must_id"]}"')
        desc = m.get("description") or ""
        # YAML-safe quoting
        desc_esc = desc.replace('"', '\\"')
        if len(desc) > 100:
            desc_esc = desc_esc[:97] + "..."
        lines.append(f'    description: "{desc_esc}"')
        lines.append("    excerpt_keywords:")
        for kw_set in m["excerpt_keywords"]:
            tokens_yaml = ", ".join(kw_set)
            lines.append(f"      - [{tokens_yaml}]")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def fetch_27701_leaves(driver) -> dict[str, dict]:
    """Return {leaf_id: {control_ref, must_items: [(must_id, text)...]}}."""
    with driver.session() as s:
        rows = s.run("""
            MATCH (er:EvidenceRequirement)-[:MUST_CONTAIN]->(item:ChecklistItem)
            WHERE er.standard_id = 'ISO27701:2019'
            RETURN er.id           AS leaf_id,
                   er.control_ref  AS control_ref,
                   item.id         AS must_id,
                   item.text       AS must_text
            ORDER BY er.id, item.id
        """).data()

    out: dict[str, dict] = {}
    for r in rows:
        lid = r["leaf_id"]
        out.setdefault(lid, {
            "control_ref": r["control_ref"],
            "must_items":  [],
        })
        out[lid]["must_items"].append((r["must_id"], r["must_text"]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be written, don't write.")
    args = ap.parse_args()

    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    try:
        leaves = fetch_27701_leaves(driver)
    finally:
        driver.close()

    print(f"Fetched {len(leaves)} leaves with "
          f"{sum(len(v['must_items']) for v in leaves.values())} MUSTs total")

    written = 0
    skipped = 0
    empty_sets = 0
    for leaf_id, info in sorted(leaves.items()):
        fingerprints: list[dict] = []
        for must_id, must_text in info["must_items"]:
            kw_sets = _build_keyword_sets(must_id, must_text)
            if not kw_sets:
                empty_sets += 1
                continue
            fingerprints.append({
                "must_id":          must_id,
                "description":      must_text or "",
                "excerpt_keywords": kw_sets,
            })

        if not fingerprints:
            skipped += 1
            continue

        yaml_content = _yaml_content(
            leaf_id           = leaf_id,
            target_control    = info["control_ref"] or "",
            target_standard   = "ISO27701:2019",
            must_fingerprints = fingerprints,
        )

        out_path = _CATALOG_DIR / _yaml_filename(leaf_id)
        if args.dry_run:
            print(f"[dry-run] would write {out_path.name} "
                  f"({len(fingerprints)} MUSTs)")
        else:
            out_path.write_text(yaml_content)
            written += 1

    print(f"\n✓ wrote {written} fingerprint YAMLs")
    if skipped:
        print(f"  {skipped} leaves skipped (all MUSTs produced empty keyword sets)")
    if empty_sets:
        print(f"  {empty_sets} MUSTs produced empty keyword sets (dropped)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
