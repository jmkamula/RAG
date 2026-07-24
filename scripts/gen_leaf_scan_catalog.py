"""Generate leaf-scan catalog YAML for an EvidenceRequirement.

Reads the leaf + its MUST_CONTAIN children from Neo4j and emits a YAML
in the same shape as the hand-authored catalogs in db/must_fingerprints/.

Heuristics for excerpt_keywords:
  1. item_id semantic stem (e.g. 'reg_completion_date' → [completion, date])
  2. high-signal tokens from item description (filter stopwords, prefer
     2-3 word noun phrases)
  3. evidence-type-specific scaffolds (register: row, entry; review: cycle,
     last; revocation: disabled, revoked; etc.)
  4. topic-anchor token from RequirementNode.title, appended to every
     keyword set to make family-templated MUST texts leaf-distinctive
     (Ship 17'.b/c → Ship 29 consolidation)

The output is a STARTING POINT, not a finished catalog. The human reviewer
should:
  - Drop noise patterns ([the], [our], [data])
  - Add tenant-vocabulary synonyms not derivable from MUST text
  - Tighten overly broad single-token sets if they risk false positives

Usage:
  # Single-leaf / single-control (prints to stdout unless --write)
  python3 scripts/gen_leaf_scan_catalog.py --leaf req:A.5.16:identity_management_register
  python3 scripts/gen_leaf_scan_catalog.py --control A.5.16 --write

  # Bulk modes (always write; --dry-run reports without touching disk)
  python3 scripts/gen_leaf_scan_catalog.py --standard ISO27701:2019
  python3 scripts/gen_leaf_scan_catalog.py --standard ISO27001:2022 --family program_review
  python3 scripts/gen_leaf_scan_catalog.py --all-auto-generated --dry-run

Behaviour of --write and --force (consistent across modes):
  - Default (no --force): overwrite auto-generated files (marked
    '# Auto-generated' in header); skip hand-authored files.
  - --force: overwrite everything, including hand-authored. Use with
    care — curator tuning is lost on regeneration.
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

# Ship 17'.b — regenerator discipline. Only overwrite files whose
# first-6-line header contains "# Auto-generated". Hand-authored
# files use different header prose (e.g. "Reviewed-from-skeleton")
# and stay untouched unless --force is passed.
_AUTO_GEN_MARKER = "# Auto-generated"

# Ship 17'.b — topic-anchor tokens injected into every keyword set to
# make family-templated MUST texts leaf-distinctive.
#
# Root cause (Ship 16'.a + 17'.a): program_review + applicable_scope
# families share identical MUST texts across every leaf, so the
# generator's description-derived tokens collapse to the same
# [review, date, planned, interval] on 48 leaves. Injecting a token
# from the leaf's RequirementNode.title (which IS distinctive per
# leaf — "Contracts with PII processors" vs "Retention" etc.)
# breaks the collision.
#
# Generic meta-tokens that appear in most compliance-standard titles
# are stripped — they'd defeat the purpose of the anchor.
_TITLE_META_NOISE = {
    "information", "security", "management", "data",
    "iso", "iec", "ensure", "ensuring", "processing",
}

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

# Evidence-shape patterns: multi-token sets that imply per-record/per-row
# evidence rather than policy prose. Generic singletons like [row] or
# [disabled] match policy text too easily — they were removed after the
# A.5.16 review pass that surfaced these false positives.
_EVIDENCE_TYPE_SYNONYMS: dict[str, list[list[str]]] = {
    "register":         [["per", "row"], ["each", "entry"], ["column", "header"]],
    "review_record":    [["review", "findings"], ["audit", "outcomes"], ["last", "reviewed"]],
    "revocation_record":[["revocation", "entry"], ["per", "revoked"], ["was", "revoked"]],
    "disposal_record":  [["disposal", "entry"], ["per", "disposed"], ["each", "disposed"]],
    "audit_log":        [["audit", "event"], ["per", "audit"]],
    "policy":           [["approved", "by"], ["effective", "date"]],
    "procedure":        [["procedure", "step"], ["responsibility", "of"]],
    "scope_note":       [["in", "scope"], ["scope", "includes"], ["excluded", "from"]],
    "register_record":  [["per", "record"], ["each", "record"]],
}

# Role-prefix safety nets — multi-token sets that imply per-record evidence
# shape for common item-id prefixes (reg_, rev_, scope_, pol_, proc_).
# Appended as a low-priority backup if the description didn't yield enough
# distinctive patterns.
_ROLE_PREFIX_HINTS: dict[str, list[list[str]]] = {
    "reg":   [["per", "row"], ["each", "row"], ["column", "containing"]],
    "rev":   [["per", "revocation"], ["per", "revoked", "identity"], ["revocation", "record"]],
    "scope": [["in", "scope"], ["scope", "includes"], ["applicable", "to"]],
    "pol":   [["policy", "clause"], ["approved", "by"]],
    "proc":  [["procedure", "step"], ["process", "step"]],
    "audit": [["audit", "event"], ["audit", "entry"]],
    "doc":   [["document", "id"], ["per", "document"]],
}

# Tokens we never emit as singletons — they're too generic and reliably
# match policy/procedure text rather than per-record evidence. Reviewer
# can still hand-add them with explicit context (e.g. [account, status]).
_NEVER_EMIT_SINGLETON = {
    "user", "users", "account", "accounts", "identity", "identities",
    "id", "ids", "name", "names", "owner", "status", "type", "role",
    "date", "time", "timestamp", "record", "entry", "row", "field",
    "column", "value", "data", "system", "module", "service", "credential",
    "credentials", "password", "passwords", "token", "tokens",
    "policy", "procedure", "process", "review", "audit", "report",
    "active", "disabled", "enabled", "revoked", "removed", "added",
    "created", "modified", "updated", "deleted", "approved", "rejected",
    "yes", "no", "true", "false", "high", "medium", "low",
    "person", "people", "individual", "individuals",
    "trigger", "triggers", "step", "steps",
    "level", "levels", "scope", "scopes",
    # Numeric units
    "days", "hours", "minutes", "weeks", "months", "years",
    # Connector/adjective noise seen in v2 generator output
    "shared", "non", "last", "cross", "reference", "phase",
    "human", "stated", "named", "unique", "valid", "expired",
    "termination", "creation", "modification", "suspension",
    "reviewer", "ownership", "lifecycle", "deactivation",
    "verification", "authn", "actual",
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

    Tokenize on whitespace + hyphens + punctuation, drop stopwords,
    return:
      - each remaining single token (UNLESS it's in _NEVER_EMIT_SINGLETON)
      - each remaining adjacent bigram
      - each remaining adjacent trigram

    The singleton suppression for high-risk tokens is the lesson from
    the A.5.16 review: words like 'user', 'disabled', 'status' match
    policy text far too easily on their own. Reviewer can still add
    them manually with surrounding context.
    """
    if not text:
        return []
    norm = _PUNCT_RE.sub(" ", text.lower())
    tokens = [t for t in norm.split() if t and t not in _STOPWORDS and len(t) > 2]
    out: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for i, t in enumerate(tokens):
        # singleton (suppressed for high-risk generic tokens)
        if t not in _NEVER_EMIT_SINGLETON:
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
        # trigram with next two
        if i + 2 < len(tokens):
            t2, t3 = tokens[i + 1], tokens[i + 2]
            key3 = (t, t2, t3)
            if key3 not in seen:
                seen.add(key3)
                out.append([t, t2, t3])
    return out


def _evidence_type_scaffold(evidence_type: str) -> list[list[str]]:
    return _EVIDENCE_TYPE_SYNONYMS.get(evidence_type, [])


def _suggest_keywords(
    item_id:       str,
    item_text:     str,
    evidence_type: str,
    control_title: str = "",
) -> list[list[str]]:
    """Compose the starter excerpt_keywords list for one MUST item.

    Strategy: id-derived stems first (highest signal), then description
    phrases (medium signal), then evidence-type scaffolds (low signal,
    cross-leaf safety net). Deduped while preserving order.

    Ship 29'.b — when `control_title` is provided, a topic-anchor
    token is appended to every keyword set (see `_title_anchor_tokens`).
    This absorbs the leaf-distinctiveness work Ship 17'.b/c delivered
    via the specialized generator; consolidation applies anchors to
    every auto-generated file rather than only 6 family × standard
    combos.
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
        # Full id phrase (multi-token only — single-token id stems like
        # 'trigger' or 'reviewer' are too generic on their own)
        if len(id_tokens) >= 2:
            _add(id_tokens)
        # Singles only if not high-risk
        for t in id_tokens:
            if t not in _NEVER_EMIT_SINGLETON:
                _add([t])

    for phrase in _phrases_from_description(item_text):
        _add(phrase)

    # Role-prefix safety net (e.g. reg_* → [per, row]; rev_* → [revocation, record])
    role_prefix = _role_prefix(item_id)
    for hint in _ROLE_PREFIX_HINTS.get(role_prefix, []):
        _add(hint)

    # Evidence-type scaffold sits last so it doesn't drown out id signal
    for scaffold in _evidence_type_scaffold(evidence_type):
        _add(scaffold)

    # Ship 28'.b — suppress redundant singletons. When the item has
    # 2+ token alternatives available, drop all single-token variants
    # (they're covered by the more-specific bigram/trigram sets and
    # only create false-positive matches). Preserve singletons as
    # last-resort safety net when NO multi-token alternative exists.
    # See ship_28_prime_a_singleton_fix_design_2026_07_24 memo.
    has_multi = any(len(s) >= 2 for s in suggestions)
    if has_multi:
        suggestions = [s for s in suggestions if len(s) >= 2]

    # Ship 29'.b — topic-anchor injection. Consolidated from the
    # specialized `generate_27701_fingerprints.py` (Ship 17'.b/c).
    # Anchors run AFTER singleton suppression so a legitimate single-
    # token set (only path when no multi-token exists) gets promoted
    # to a distinctive multi-token set.
    anchors = _title_anchor_tokens(control_title)
    if anchors:
        suggestions = [
            _augment_with_anchor(kw, anchors) for kw in suggestions
        ]

    # Cap at ~8 to keep the human reviewer's eye unburdened — they'll
    # add tenant-vocabulary synonyms manually anyway.
    return suggestions[:8]


def _role_prefix(item_id: str) -> str:
    """Pull the role prefix from an item id (e.g. reg_/rev_/scope_/pol_)."""
    tail = item_id.rsplit(":", 1)[-1]
    head = tail.split("_", 1)[0] if "_" in tail else ""
    return head if head in _ROLE_PREFIX_HINTS else ""


def _title_anchor_tokens(title: str, max_tokens: int = 2) -> list[str]:
    """Extract 1-2 distinctive tokens from a RequirementNode.title
    for use as anchor tokens injected into every keyword set on
    that leaf.

    Filters generic English stopwords, catalog-shape words, and
    meta-tokens that recur across compliance titles. Returns up to
    `max_tokens` tokens in title order so the first substantive
    word wins.

    Ported from `generate_27701_fingerprints.py::_topic_anchor_tokens`
    in Ship 29'.b."""
    if not title:
        return []
    norm = _PUNCT_RE.sub(" ", title.lower())
    tokens = [
        t for t in norm.split()
        if t
        and t not in _STOPWORDS
        and t not in _TITLE_META_NOISE
        and len(t) > 2
        and not t.isdigit()
    ]
    return tokens[:max_tokens]


def _augment_with_anchor(
    kw_set: list[str], anchors: list[str],
) -> list[str]:
    """Return `kw_set` with one anchor token appended. If the set
    already contains an anchor (rare — happens when the MUST text
    mentions the leaf topic), it's unchanged. Only the first anchor
    is used so sets don't grow unboundedly.

    Ported from `generate_27701_fingerprints.py::_augment_with_anchor`
    in Ship 29'.b."""
    if not anchors:
        return kw_set
    if any(a in kw_set for a in anchors):
        return kw_set
    return kw_set + [anchors[0]]


def _is_auto_generated(path: Path) -> bool:
    """Return True if `path` has the '# Auto-generated' marker in
    its first 6 lines. Missing file → True (safe to write). Read
    errors → False (defensive)."""
    if not path.exists():
        return True
    try:
        head = path.read_text(encoding="utf-8", errors="replace").splitlines()[:6]
    except Exception:
        return False
    return any(_AUTO_GEN_MARKER in ln for ln in head)


def _target_from_yaml(path: Path) -> str | None:
    """Pull `target_evidence_requirement` from a YAML file's header
    by direct string parse (faster than yaml.safe_load and tolerant
    of non-strict YAML)."""
    try:
        with open(path, "r") as f:
            for _ in range(30):
                line = f.readline()
                if not line:
                    break
                if line.startswith("target_evidence_requirement:"):
                    val = line.split(":", 1)[1].strip().strip('"').strip("'")
                    return val or None
    except Exception:
        return None
    return None


_RETURN_FIELDS = """
    er.id            AS leaf_id,
    er.control_ref   AS control_ref,
    er.standard_id   AS standard_id,
    er.evidence_type AS evidence_type,
    er.title         AS title,
    rn.title         AS control_title,
    collect({id: item.id, text: item.text}) AS items
"""


def _fetch_leaves(
    neo,
    control_ref: str | None = None,
    leaf_id:     str | None = None,
    standard_id: str | None = None,
    leaf_ids:    list[str] | None = None,
) -> list[dict]:
    """Fetch leaves in one of four modes:
      * `leaf_id`     — one specific leaf
      * `control_ref` — every leaf under a control
      * `standard_id` — every leaf in a standard (bulk)
      * `leaf_ids`    — an explicit list of leaves (bulk, from
                        `--all-auto-generated` walk)

    All modes include `RequirementNode.title` (as `control_title`)
    so `_suggest_keywords` can inject a leaf-distinctive anchor.
    """
    if leaf_id:
        cypher = f"""
            MATCH (er:EvidenceRequirement {{id: $leaf_id}})
            OPTIONAL MATCH (rn:RequirementNode {{
                ref: er.control_ref, standard_id: er.standard_id}})
            OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
            RETURN {_RETURN_FIELDS}
        """
        params = {"leaf_id": leaf_id}
    elif control_ref:
        cypher = f"""
            MATCH (er:EvidenceRequirement {{control_ref: $control_ref}})
            OPTIONAL MATCH (rn:RequirementNode {{
                ref: er.control_ref, standard_id: er.standard_id}})
            OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
            RETURN {_RETURN_FIELDS}
            ORDER BY er.id
        """
        params = {"control_ref": control_ref}
    elif standard_id:
        cypher = f"""
            MATCH (er:EvidenceRequirement {{standard_id: $standard_id}})
            OPTIONAL MATCH (rn:RequirementNode {{
                ref: er.control_ref, standard_id: er.standard_id}})
            OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
            RETURN {_RETURN_FIELDS}
            ORDER BY er.id
        """
        params = {"standard_id": standard_id}
    elif leaf_ids:
        cypher = f"""
            MATCH (er:EvidenceRequirement) WHERE er.id IN $leaf_ids
            OPTIONAL MATCH (rn:RequirementNode {{
                ref: er.control_ref, standard_id: er.standard_id}})
            OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
            RETURN {_RETURN_FIELDS}
            ORDER BY er.id
        """
        params = {"leaf_ids": list(leaf_ids)}
    else:
        raise ValueError(
            "one of leaf_id / control_ref / standard_id / leaf_ids required")
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
    control_title = leaf.get("control_title") or ""
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
        kws       = _suggest_keywords(
            item_id, item_text, evidence_type,
            control_title=control_title,
        )

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


def _walk_auto_generated_leaf_ids() -> list[str]:
    """Walk `db/must_fingerprints/` and return the leaf_ids of files
    whose header carries the `# Auto-generated` marker. Files that
    fail to parse (no target_evidence_requirement in first 30 lines)
    are silently skipped."""
    ids: list[str] = []
    if not _CATALOG_DIR.exists():
        return ids
    for path in sorted(_CATALOG_DIR.glob("*.yaml")):
        if not _is_auto_generated(path):
            continue
        leaf_id = _target_from_yaml(path)
        if leaf_id:
            ids.append(leaf_id)
    return ids


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g  = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--leaf",
                   help="Exact EvidenceRequirement id (req:...)")
    g.add_argument("--control",
                   help="Control ref (e.g. A.5.16) — emits one YAML per leaf.")
    g.add_argument("--standard",
                   help="Standard id (e.g. ISO27001:2022) — bulk-regenerates "
                        "every leaf in the standard.")
    g.add_argument("--all-auto-generated", action="store_true",
                   dest="all_auto_generated",
                   help="Walk db/must_fingerprints/ and regenerate every file "
                        "whose header carries the '# Auto-generated' marker. "
                        "Hand-authored files are skipped.")
    ap.add_argument("--family",
                    help="Filter leaves by leaf_id substring (e.g. "
                         "'program_review'). Combines with --standard or "
                         "--all-auto-generated.")
    ap.add_argument("--write", action="store_true",
                    help="Write to db/must_fingerprints/. Single-leaf modes "
                         "default to stdout; bulk modes always write.")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite hand-authored files too. Default: only "
                         "touch files marked '# Auto-generated'. USE WITH "
                         "CAUTION — curator tuning is lost on regeneration.")
    ap.add_argument("--dry-run", action="store_true", dest="dry_run",
                    help="Report what would change without touching disk.")
    args = ap.parse_args()

    uri  = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pw   = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and pw):
        print("ERROR: NEO4J_URI/USER/PASSWORD not set in .env", file=sys.stderr)
        return 1
    neo = GraphDatabase.driver(uri, auth=(user, pw))

    bulk_mode = bool(args.standard or args.all_auto_generated)

    try:
        if args.leaf:
            leaves = _fetch_leaves(neo, leaf_id=args.leaf)
        elif args.control:
            leaves = _fetch_leaves(neo, control_ref=args.control)
        elif args.standard:
            leaves = _fetch_leaves(neo, standard_id=args.standard)
        elif args.all_auto_generated:
            ids = _walk_auto_generated_leaf_ids()
            if not ids:
                print("No auto-generated files found in "
                      f"{_CATALOG_DIR}", file=sys.stderr)
                return 1
            leaves = _fetch_leaves(neo, leaf_ids=ids)
        else:
            print("ERROR: no mode specified", file=sys.stderr)
            return 1
    finally:
        neo.close()

    if args.family:
        leaves = [
            l for l in leaves
            if args.family in (l.get("leaf_id") or "")
        ]

    if not leaves:
        target = (args.leaf or args.control or args.standard
                  or "(all-auto-generated)")
        extra  = f" family={args.family!r}" if args.family else ""
        print(f"No leaves matched {target!r}{extra}", file=sys.stderr)
        return 1

    print(f"Fetched {len(leaves)} leaves"
          + (f" (family={args.family!r})" if args.family else ""))

    # For single-leaf modes, default is stdout unless --write.
    # For bulk modes, default is write (that's the whole point).
    write_to_disk = args.write or bulk_mode
    if write_to_disk:
        _CATALOG_DIR.mkdir(parents=True, exist_ok=True)

    n_written  = 0
    n_unchanged = 0
    n_hand_guarded = 0
    n_stdout   = 0

    for leaf in leaves:
        if not leaf.get("leaf_id"):
            continue
        yaml_text = _render_yaml(leaf)

        if not write_to_disk:
            print(yaml_text)
            print("---")
            n_stdout += 1
            continue

        path = _CATALOG_DIR / _catalog_filename(leaf["leaf_id"])
        # Skip hand-authored files unless --force.
        if path.exists() and not args.force and not _is_auto_generated(path):
            n_hand_guarded += 1
            continue

        existing = path.read_text() if path.exists() else ""
        if existing == yaml_text:
            n_unchanged += 1
            continue

        n_musts = len([it for it in (leaf.get("items") or []) if it.get("id")])
        if args.dry_run:
            print(f"  [dry-run] would write: {path.name} ({n_musts} MUSTs)")
        else:
            path.write_text(yaml_text)
            print(f"  WROTE: {path.name} ({n_musts} MUSTs)")
        n_written += 1

    print()
    if write_to_disk:
        verb = "would write" if args.dry_run else "wrote"
        print(f"  {verb}:      {n_written}")
        print(f"  unchanged:      {n_unchanged}")
        if n_hand_guarded:
            print(f"  hand-guarded:   {n_hand_guarded}  "
                  f"(--force to override)")
    else:
        print(f"  emitted to stdout: {n_stdout}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
