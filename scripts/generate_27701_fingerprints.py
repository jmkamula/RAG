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
from typing import Optional

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

# Ship 17'.b — topic-anchor tokens injected into every keyword set to
# make family-templated MUST texts leaf-distinctive.
#
# Root cause (Ship 16'.a + 17'.a): program_review + applicable_scope
# families share identical MUST texts across every leaf, so the
# generator's Set-2 (from MUST text) tokenises to the same
# [review, date, planned, interval] on 48 leaves. Injecting a token
# from the leaf's RequirementNode.title (which IS distinctive per
# leaf — "Contracts with PII processors" vs "Retention" etc.)
# collapses the collision.
#
# Generic meta-tokens that appear in most compliance-standard titles
# are stripped — they'd defeat the purpose of the anchor.
_TITLE_META_NOISE = {
    "information", "security", "management", "data",
    "iso", "iec", "ensure", "ensuring", "processing",
    # "processing" is generic across the 27701 privacy family;
    # subject-matter tokens (contracts, retention, disposal,
    # transfers, notification) survive.
}


def _topic_anchor_tokens(title: str, max_tokens: int = 2) -> list[str]:
    """Extract 1-2 distinctive tokens from a RequirementNode.title
    for use as anchor tokens injected into every keyword set on
    that leaf.

    Uses the existing _tokenize helper (stopword + short-token
    filter), then additionally strips meta-tokens that recur
    across compliance titles (information, security, management,
    etc.). Returns up to `max_tokens` non-meta tokens, order-
    preserving so the first substantive word wins."""
    tokens = _tokenize(title)
    anchors = [t for t in tokens if t not in _TITLE_META_NOISE]
    return anchors[:max_tokens]


def _augment_with_anchor(
    kw_set: list[str], anchors: list[str],
) -> list[str]:
    """Return `kw_set` with at least one anchor token appended.
    If the set already contains an anchor (rare but possible when
    the MUST text mentions the leaf topic), it's unchanged.
    Anchors are appended in given order so the first anchor wins.

    Injecting just ONE anchor per set is intentional — makes the
    set LEAF-DISTINCTIVE without narrowing it so much that
    legitimate mentions miss."""
    if not anchors:
        return kw_set
    if any(a in kw_set for a in anchors):
        return kw_set
    return kw_set + [anchors[0]]


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


def _build_keyword_sets(
    must_id: str, must_text: str,
    topic_anchors: Optional[list[str]] = None,
) -> list[list[str]]:
    """Compose up to 2 keyword sets per MUST. Deduplicated and
    filtered to non-trivial sets (≥1 meaningful token).

    Ship 17'.b — when `topic_anchors` is supplied (from the
    leaf's RequirementNode.title), each generated set is augmented
    with one anchor token. Turns family-templated sets into
    leaf-distinctive ones. See `_topic_anchor_tokens` for extraction."""
    sets: list[list[str]] = []
    seen: set[tuple] = set()

    for candidate in (
        _tokens_from_must_id(must_id),
        _tokens_from_must_text(must_text),
    ):
        if not candidate or len(candidate) < _MIN_SET_SIZE:
            continue
        # Ship 17'.b — inject a leaf-topic anchor if provided
        if topic_anchors:
            candidate = _augment_with_anchor(candidate, topic_anchors)
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


def fetch_leaves(driver, standard_id: str) -> dict[str, dict]:
    """Return {leaf_id: {control_ref, control_title, must_items:
    [(must_id, text)...]}} for the requested standard.

    Ship 17'.b — fetches the parent RequirementNode.title alongside
    the ChecklistItem rows. Title feeds `_topic_anchor_tokens`
    which is injected into every keyword set.

    Ship 17'.c — parameterised by `standard_id` so the same
    regenerator can service ISO 27701 (original scope) and
    ISO 27001 (Ship 17'.c target)."""
    with driver.session() as s:
        rows = s.run(
            """
            MATCH (rn:RequirementNode {standard_id: $sid})
            MATCH (er:EvidenceRequirement {control_ref: rn.ref,
                                            standard_id: $sid})
            MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
            RETURN er.id           AS leaf_id,
                   er.control_ref  AS control_ref,
                   rn.title        AS control_title,
                   item.id         AS must_id,
                   item.text       AS must_text
            ORDER BY er.id, item.id
            """,
            sid=standard_id,
        ).data()

    out: dict[str, dict] = {}
    for r in rows:
        lid = r["leaf_id"]
        out.setdefault(lid, {
            "control_ref":   r["control_ref"],
            "control_title": r["control_title"] or "",
            "must_items":    [],
        })
        out[lid]["must_items"].append((r["must_id"], r["must_text"]))
    return out


# Backward-compat alias — external callers use this name today.
def fetch_27701_leaves(driver) -> dict[str, dict]:
    return fetch_leaves(driver, "ISO27701:2019")


# Ship 17'.b — regenerator discipline. Only overwrite files whose
# first-6-line header contains "Auto-generated". Hand-authored files
# (marked with prose like "Reviewed-from-skeleton" or "Hand-authored")
# stay untouched. See Ship 17'.a design memo.
_AUTO_GEN_MARKER = "Auto-generated"


def _is_auto_generated(path: Path) -> bool:
    """Return True if the file's first 6 lines contain the auto-gen
    marker. Missing file → True (safe to write). Any read error →
    False (defensive)."""
    if not path.exists():
        return True
    try:
        head = path.read_text(encoding="utf-8", errors="replace").splitlines()[:6]
    except Exception:
        return False
    return any(_AUTO_GEN_MARKER in ln for ln in head)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be written, don't write.")
    ap.add_argument("--family", default=None,
                    help="Regenerate only leaves whose slug matches "
                         "this substring (Ship 17'.b — e.g. "
                         "'program_review' or 'applicable_scope').")
    ap.add_argument("--standard", default="ISO27701:2019",
                    help="Standard id to regenerate (Ship 17'.c — "
                         "e.g. 'ISO27001:2022'). Default: ISO27701:2019 "
                         "for backward-compat with Ship 17'.b.")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite hand-authored files too. Default: "
                         "only touch files marked '# Auto-generated'. "
                         "USE WITH CAUTION — hand-curated tuning is "
                         "lost on regeneration.")
    args = ap.parse_args()

    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    try:
        leaves = fetch_leaves(driver, args.standard)
    finally:
        driver.close()

    # Family filter — Ship 17'.b runs on program_review + applicable_scope
    # first; 17'.c does the rest.
    if args.family:
        leaves = {
            lid: info for lid, info in leaves.items()
            if args.family in lid
        }

    print(f"Fetched {len(leaves)} leaves with "
          f"{sum(len(v['must_items']) for v in leaves.values())} MUSTs total")

    written  = 0
    skipped  = 0
    empty_sets = 0
    hand_guarded = 0  # Ship 17'.b — skipped because hand-authored
    for leaf_id, info in sorted(leaves.items()):
        # Ship 17'.b — topic anchors from the parent
        # RequirementNode.title. Empty list falls through cleanly:
        # `_augment_with_anchor` no-ops when anchors=[].
        anchors = _topic_anchor_tokens(info.get("control_title", ""))

        fingerprints: list[dict] = []
        for must_id, must_text in info["must_items"]:
            kw_sets = _build_keyword_sets(must_id, must_text,
                                           topic_anchors=anchors)
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

        out_path = _CATALOG_DIR / _yaml_filename(leaf_id)

        # Ship 17'.b — never overwrite hand-authored files unless
        # --force. This is the safety belt that lets bulk
        # regeneration run without losing curator work.
        if not args.force and not _is_auto_generated(out_path):
            hand_guarded += 1
            continue

        yaml_content = _yaml_content(
            leaf_id           = leaf_id,
            target_control    = info["control_ref"] or "",
            target_standard   = args.standard,
            must_fingerprints = fingerprints,
        )
        if args.dry_run:
            print(f"[dry-run] would write {out_path.name} "
                  f"({len(fingerprints)} MUSTs, anchors={anchors})")
        else:
            out_path.write_text(yaml_content)
            written += 1

    print(f"\n✓ wrote {written} fingerprint YAMLs")
    if hand_guarded:
        print(f"  {hand_guarded} leaves skipped (hand-authored — "
              f"use --force to override)")
    if skipped:
        print(f"  {skipped} leaves skipped (all MUSTs produced empty keyword sets)")
    if empty_sets:
        print(f"  {empty_sets} MUSTs produced empty keyword sets (dropped)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
