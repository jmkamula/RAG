"""Generate starter leaf-scan catalog YAML for an EvidenceRequirement.

Reads the leaf + its MUST_CONTAIN children from Neo4j and emits a YAML
in the same shape as the hand-authored catalogs in db/must_fingerprints/.

Heuristics for excerpt_keywords:
  1. item_id semantic stem (e.g. 'reg_completion_date' → [completion, date])
  2. high-signal tokens from item description (filter stopwords, prefer
     2-3 word noun phrases)
  3. evidence-type-specific scaffolds (register: row, entry; review: cycle,
     last; revocation: disabled, revoked; etc.)

The output is a STARTING POINT, not a finished catalog. The human reviewer
should:
  - Drop noise patterns ([the], [our], [data])
  - Add tenant-vocabulary synonyms not derivable from MUST text
  - Tighten overly broad single-token sets if they risk false positives

Usage:
  python3 scripts/gen_leaf_scan_catalog.py req:A.5.16:identity_management_register
  python3 scripts/gen_leaf_scan_catalog.py --control A.5.16
  python3 scripts/gen_leaf_scan_catalog.py --control A.5.16 --write

Without --write the YAML is printed to stdout. With --write it lands in
db/must_fingerprints/<filename>.yaml — but only if a file with that name
doesn't already exist (the generator never overwrites hand-curated work).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterable

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(_ROOT / ".env")

_CATALOG_DIR = _ROOT / "db" / "must_fingerprints"

# Tokens to drop when extracting from item descriptions — generic English
# stopwords + register/list-shape words that don't differentiate a MUST.
_STOPWORDS = {
    "a", "an", "the", "of", "to", "in", "on", "at", "by", "for", "from",
    "and", "or", "with", "as", "is", "are", "was", "were", "be", "been",
    "this", "that", "these", "those", "it", "its", "any", "each", "all",
    "per", "row", "entry", "item", "type", "kind", "field", "value",
    "where", "when", "what", "which", "who", "how", "why",
    # filler nouns that appear in many MUSTs and don't anchor a match
    "control", "register", "record", "log", "policy", "procedure",
    "process", "list", "table", "data", "information", "details",
    # description-shape words that fingerprint the MUST template but
    # not the underlying evidence (auto-generated only — humans never
    # want to match on these)
    "drives", "includes", "covers", "captures", "must", "should",
    "exists", "exist", "applicable", "applies", "applied",
    "module", "modules", "system", "systems", "tool", "tools",
    "linked", "links", "link",
}

# Words that suggest evidence-type-specific synonym clusters
_EVIDENCE_TYPE_SYNONYMS: dict[str, list[list[str]]] = {
    "register":         [["row"], ["entry"], ["record"]],
    "review_record":    [["review", "date"], ["last", "review"], ["cycle"]],
    "revocation_record":[["revoked"], ["disabled"], ["deactivated"]],
    "disposal_record":  [["disposed"], ["destroyed"], ["wiped"]],
    "audit_log":        [["timestamp"], ["audit"], ["event"]],
    "policy":           [["policy"], ["approved"], ["effective", "date"]],
    "procedure":        [["procedure"], ["steps"], ["responsible"]],
    "scope_note":       [["scope"], ["applies", "to"], ["excluded"]],
}


def _kebab(s: str) -> str:
    """Normalise to slug — used to derive default catalog filename.
    Preserves case (the convention is req_A_5_18_..., not req_a_5_18_...)."""
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def _tokens_from_item_id(item_id: str) -> list[str]:
    """Pull semantic tokens out of `item:A.6.3:reg_completion_date`.

    Drops the leading prefix (`reg_`, `rev_`, `scope_`, etc.) since those
    are role markers, not semantic content. The remaining parts are the
    keyword candidates.
    """
    # last colon-segment is the bare item name
    tail = item_id.rsplit(":", 1)[-1]
    parts = tail.split("_")
    if not parts:
        return []
    # Common role prefixes — drop them. They're shape markers, not content.
    _ROLE_PREFIXES = {"reg", "rev", "scope", "pol", "proc", "doc", "audit", "rec"}
    if parts[0] in _ROLE_PREFIXES and len(parts) > 1:
        parts = parts[1:]
    return [p for p in parts if p and p not in _STOPWORDS]


_PUNCT_RE = re.compile(r"[^\w\s]")  # strip hyphens too — they split compound words


def _phrases_from_description(text: str) -> list[list[str]]:
    """Pull 1-3 word noun-ish phrases out of an item description.

    Simple heuristic: tokenize on whitespace + hyphens + punctuation, drop
    stopwords, return:
      - each remaining single token
      - each remaining adjacent bigram

    Parentheticals are kept (they often hold examples like "(current /
    overdue / waived)" which are useful match anchors).
    """
    if not text:
        return []
    norm = _PUNCT_RE.sub(" ", text.lower())
    tokens = [t for t in norm.split() if t and t not in _STOPWORDS and len(t) > 2]
    out: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for i, t in enumerate(tokens):
        # singleton
        key = (t,)
        if key not in seen:
            seen.add(key)
            out.append([t])
        # bigram with next
        if i + 1 < len(tokens):
            t2 = tokens[i + 1]
            key2 = (t, t2)
            if key2 not in seen:
                seen.add(key2)
                out.append([t, t2])
    return out


def _evidence_type_scaffold(evidence_type: str) -> list[list[str]]:
    return _EVIDENCE_TYPE_SYNONYMS.get(evidence_type, [])


def _suggest_keywords(
    item_id:       str,
    item_text:     str,
    evidence_type: str,
) -> list[list[str]]:
    """Compose the starter excerpt_keywords list for one MUST item.

    Strategy: id-derived stems first (highest signal), then description
    phrases (medium signal), then evidence-type scaffolds (low signal,
    cross-leaf safety net). Deduped while preserving order.
    """
    suggestions: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()

    def _add(toks: list[str]) -> None:
        if not toks:
            return
        key = tuple(toks)
        if key in seen:
            return
        seen.add(key)
        suggestions.append(toks)

    id_tokens = _tokens_from_item_id(item_id)
    if id_tokens:
        # Full id phrase
        _add(id_tokens)
        # Single tokens
        for t in id_tokens:
            _add([t])

    for phrase in _phrases_from_description(item_text):
        _add(phrase)

    # Evidence-type scaffold sits last so it doesn't drown out id signal
    for scaffold in _evidence_type_scaffold(evidence_type):
        _add(scaffold)

    # Cap at ~8 to keep the human reviewer's eye unburdened — they'll
    # add tenant-vocabulary synonyms manually anyway.
    return suggestions[:8]


def _fetch_leaves(neo, control_ref: str | None, leaf_id: str | None) -> list[dict]:
    """Fetch leaves either by control_ref (all leaves under that control)
    or by exact leaf id (one leaf).
    """
    if leaf_id:
        cypher = """
            MATCH (er:EvidenceRequirement {id: $leaf_id})
            OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
            RETURN er.id           AS leaf_id,
                   er.control_ref  AS control_ref,
                   er.standard_id  AS standard_id,
                   er.evidence_type AS evidence_type,
                   er.title        AS title,
                   collect({id: item.id, text: item.text}) AS items
        """
        params = {"leaf_id": leaf_id}
    else:
        cypher = """
            MATCH (er:EvidenceRequirement {control_ref: $control_ref})
            OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
            RETURN er.id           AS leaf_id,
                   er.control_ref  AS control_ref,
                   er.standard_id  AS standard_id,
                   er.evidence_type AS evidence_type,
                   er.title        AS title,
                   collect({id: item.id, text: item.text}) AS items
            ORDER BY er.id
        """
        params = {"control_ref": control_ref}
    with neo.session() as s:
        return [dict(row) for row in s.run(cypher, **params)]


def _render_yaml(leaf: dict) -> str:
    """Render one leaf's catalog as YAML text. Stays hand-edited-shaped:
    quoted ids, no anchors, comments preserved.
    """
    leaf_id       = leaf["leaf_id"]
    control_ref   = leaf["control_ref"]
    standard_id   = leaf["standard_id"]
    evidence_type = leaf.get("evidence_type", "")
    items         = [it for it in (leaf.get("items") or []) if it.get("id")]

    lines: list[str] = []
    lines.append(f"# Per-MUST fingerprint catalog for {leaf_id}")
    lines.append(f"# Auto-generated skeleton — review and tighten before commit.")
    lines.append("#")
    lines.append("# Used by rag/intake/leaf_driven_scan.py to back-bind existing")
    lines.append("# approved findings to specific MUSTs they semantically satisfy")
    lines.append("# but weren't tagged with at extraction time.")
    lines.append("")
    lines.append(f"schema_version: 1")
    lines.append(f'target_evidence_requirement: "{leaf_id}"')
    lines.append(f'target_control: "{control_ref}"')
    lines.append(f'target_standard: "{standard_id}"')
    lines.append("")
    lines.append("must_fingerprints:")
    if not items:
        lines.append("  # (no MUST_CONTAIN items on this leaf — nothing to scan)")
        return "\n".join(lines) + "\n"

    for it in items:
        item_id   = it["id"]
        item_text = (it.get("text") or "").strip()
        kws       = _suggest_keywords(item_id, item_text, evidence_type)

        lines.append(f'  - must_id: "{item_id}"')
        # description: first sentence of item.text or a fallback
        desc = item_text.split(". ")[0] if item_text else item_id.split(":")[-1].replace("_", " ")
        # YAML-safe single-line description
        desc_clean = desc.replace('"', "'")
        lines.append(f'    description: "{desc_clean[:140]}"')
        lines.append(f"    excerpt_keywords:")
        if kws:
            for kw_set in kws:
                # YAML inline list
                lines.append(f"      - [{', '.join(kw_set)}]")
        else:
            lines.append("      # (no keywords derived — add manually)")
        lines.append("")
    return "\n".join(lines) + "\n"


def _catalog_filename(leaf_id: str) -> str:
    """Mirror the existing naming convention: req_A_5_18_access_rights_register.yaml."""
    return _kebab(leaf_id) + ".yaml"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g  = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--leaf", help="Exact EvidenceRequirement id (req:...)")
    g.add_argument("--control", help="Control ref (e.g. A.5.16) — emits one YAML per leaf")
    ap.add_argument("--write", action="store_true",
                    help="Write to db/must_fingerprints/. Without this, prints to stdout.")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing YAML (default: skip if file exists).")
    args = ap.parse_args()

    uri  = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pw   = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and pw):
        print("ERROR: NEO4J_URI/USER/PASSWORD not set in .env", file=sys.stderr)
        return 1
    neo = GraphDatabase.driver(uri, auth=(user, pw))

    leaves = _fetch_leaves(neo, control_ref=args.control, leaf_id=args.leaf)
    if not leaves:
        target = args.leaf or args.control
        print(f"No leaves found for {target!r}", file=sys.stderr)
        return 1

    if args.write:
        _CATALOG_DIR.mkdir(parents=True, exist_ok=True)

    for leaf in leaves:
        if not leaf.get("leaf_id"):
            continue
        yaml_text = _render_yaml(leaf)
        if not args.write:
            print(yaml_text)
            print("---")
            continue

        path = _CATALOG_DIR / _catalog_filename(leaf["leaf_id"])
        if path.exists() and not args.force:
            print(f"  SKIP (exists): {path.name}", file=sys.stderr)
            continue
        path.write_text(yaml_text)
        n_musts = len([it for it in (leaf.get("items") or []) if it.get("id")])
        verb = "OVERWROTE" if args.force and path.exists() else "WROTE"
        print(f"  {verb}: {path.name} ({n_musts} MUSTs)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
