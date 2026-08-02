#!/usr/bin/env python3
"""
load_to_postgres.py — load topic bundles from db/topics/*.yaml into
the Postgres topics + topic_leaves tables.

Ship 54'.a (2026-08-02) — additive overlay on top of per-leaf
templates. Topic bundles group leaves into compliance workflows
(DSR, incident response, risk cycle, etc.) without touching the
per-leaf templates in db/templates/.

Behaviour
---------
* Walks db/topics/*.yaml, one topic per file
* Validates:
    - required top-level fields (slug, title, description,
      primary_framework, leaves)
    - each leaf.leaf_id exists in ALL_EVIDENCE_REQUIREMENTS or
      ALL_DERIVED_SPECS.direct_evidence (canonical catalog union)
    - primary_framework is a known value
    - no duplicate leaf_id within one topic
* Upserts into topics table + replaces topic_leaves for each topic
  (delete-and-insert atomically inside one transaction per topic)
* Orphan sweep: removes topics whose YAML file is no longer present

Failure modes are loud — a curator typo on a leaf_id fails the
build gate. Intended contract: topics evolve with curation.

Pattern mirrors enrichment/templates/load_to_postgres.py.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


REPO_ROOT   = Path(__file__).resolve().parent.parent.parent
TOPICS_DIR  = REPO_ROOT / "db" / "topics"

# Known frameworks — extend when new standards enrolled.
_VALID_FRAMEWORKS = {
    "ISO27001:2022",
    "GDPR:2016/679",
    "ISO27701:2019",
    "multi",
}

_VALID_ROLES = {
    # Primary bundle roles
    "primary_policy",
    "primary_procedure",
    "primary_register",
    # Supporting connections
    "supporting_prerequisite",
    "supporting_iso_mirror",
    "supporting_cross_framework",
    # Instance artefacts
    "form",
    "log",
    "review_record",
    "evidence",
}


@dataclass
class TopicLeaf:
    leaf_id:        str
    role:           str
    workflow_order: int = 100
    role_note:      Optional[str] = None


@dataclass
class Topic:
    slug:              str
    title:             str
    description:       str
    primary_framework: str
    auditor_expects:   Optional[str]
    display_order:     int
    source_file:       str
    leaves:            list[TopicLeaf] = field(default_factory=list)


# ── Parsing + validation ──────────────────────────────────────────────

def _require(d: dict, key: str, context: str):
    if key not in d or d[key] in (None, "", []):
        raise ValueError(f"{context}: missing required field '{key}'")
    return d[key]


def _parse_topic_file(path: Path, leaf_index: dict[str, object]) -> Topic:
    """Read + validate one topic YAML. Raises ValueError on any problem."""
    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parse error: {e}")
    if not isinstance(raw, dict):
        raise ValueError("top-level must be a mapping")

    ctx = f"{path.name}"
    slug              = _require(raw, "slug", ctx)
    title             = _require(raw, "title", ctx)
    description       = _require(raw, "description", ctx)
    primary_framework = _require(raw, "primary_framework", ctx)
    leaves_raw        = _require(raw, "leaves", ctx)

    if primary_framework not in _VALID_FRAMEWORKS:
        raise ValueError(
            f"primary_framework={primary_framework!r} unknown "
            f"(valid: {sorted(_VALID_FRAMEWORKS)})"
        )

    if not isinstance(leaves_raw, list) or not leaves_raw:
        raise ValueError("leaves must be a non-empty list")

    seen: set[str] = set()
    leaves: list[TopicLeaf] = []
    for i, item in enumerate(leaves_raw):
        item_ctx = f"{ctx} leaves[{i}]"
        if not isinstance(item, dict):
            raise ValueError(f"{item_ctx}: must be a mapping")
        leaf_id = _require(item, "leaf_id", item_ctx)
        role    = _require(item, "role", item_ctx)

        if leaf_id in seen:
            raise ValueError(f"{item_ctx}: duplicate leaf_id {leaf_id!r}")
        seen.add(leaf_id)

        if leaf_id not in leaf_index:
            raise ValueError(
                f"{item_ctx}: leaf_id {leaf_id!r} not in the catalog "
                f"(ALL_EVIDENCE_REQUIREMENTS or ALL_DERIVED_SPECS.direct_evidence)"
            )

        if role not in _VALID_ROLES:
            # Warn but don't fail — controlled vocab is aspirational,
            # curator may extend it. Loader accepts; advisory surfaces
            # can filter to known values.
            print(f"  ⚠ {item_ctx}: role {role!r} not in known set — accepted")

        try:
            workflow_order = int(item.get("workflow_order", 100))
        except (TypeError, ValueError):
            raise ValueError(
                f"{item_ctx}: workflow_order must be int, got "
                f"{item.get('workflow_order')!r}"
            )

        role_note = item.get("role_note")
        if role_note is not None:
            role_note = str(role_note).strip()
            if len(role_note) > 500:
                raise ValueError(f"{item_ctx}: role_note > 500 chars")

        leaves.append(TopicLeaf(
            leaf_id        = leaf_id,
            role           = role,
            workflow_order = workflow_order,
            role_note      = role_note,
        ))

    auditor_expects = raw.get("auditor_expects")
    if auditor_expects is not None:
        auditor_expects = str(auditor_expects).strip()

    try:
        display_order = int(raw.get("display_order", 100))
    except (TypeError, ValueError):
        raise ValueError(f"{ctx}: display_order must be int")

    return Topic(
        slug              = slug,
        title             = title,
        description       = description.strip(),
        primary_framework = primary_framework,
        auditor_expects   = auditor_expects,
        display_order     = display_order,
        source_file       = path.name,
        leaves            = leaves,
    )


def _build_leaf_index() -> dict[str, object]:
    """leaf_id → EvidenceRequirement object. Canonical catalog union
    per [[feedback-validate-set-membership]]."""
    sys.path.insert(0, str(REPO_ROOT))
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    idx: dict[str, object] = {}
    for er in ALL_EVIDENCE_REQUIREMENTS:
        idx[er.id] = er
    for spec in ALL_DERIVED_SPECS:
        for er in spec.direct_evidence:
            idx[er.id] = er
    return idx


# ── Upsert ────────────────────────────────────────────────────────────

def _upsert_topic(cur, topic: Topic, loaded_by: str) -> str:
    """Upsert the topic row + replace its topic_leaves atomically.
    Returns 'inserted' / 'updated' / 'unchanged'."""
    cur.execute(
        "SELECT title, description, primary_framework, auditor_expects, "
        "display_order, source_file FROM topics WHERE slug = %s",
        (topic.slug,),
    )
    existing = cur.fetchone()
    is_new = existing is None

    # Fetch current leaves too — determine 'unchanged' status
    if not is_new:
        cur.execute(
            "SELECT leaf_id, role, workflow_order, role_note "
            "FROM topic_leaves WHERE topic_slug = %s "
            "ORDER BY leaf_id",
            (topic.slug,),
        )
        current_leaves = cur.fetchall()
        proposed_leaves = sorted([
            (l.leaf_id, l.role, l.workflow_order, l.role_note)
            for l in topic.leaves
        ])
        header_matches = (
            existing == (topic.title, topic.description,
                         topic.primary_framework, topic.auditor_expects,
                         topic.display_order, topic.source_file)
        )
        leaves_match = list(current_leaves) == proposed_leaves
        if header_matches and leaves_match:
            return "unchanged"

    if is_new:
        cur.execute(
            """
            INSERT INTO topics
              (slug, title, description, primary_framework, auditor_expects,
               display_order, source_file, last_loaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (topic.slug, topic.title, topic.description,
             topic.primary_framework, topic.auditor_expects,
             topic.display_order, topic.source_file, loaded_by),
        )
    else:
        cur.execute(
            """
            UPDATE topics
               SET title              = %s,
                   description        = %s,
                   primary_framework  = %s,
                   auditor_expects    = %s,
                   display_order      = %s,
                   source_file        = %s,
                   last_loaded_at     = now(),
                   last_loaded_by     = %s
             WHERE slug = %s
            """,
            (topic.title, topic.description, topic.primary_framework,
             topic.auditor_expects, topic.display_order, topic.source_file,
             loaded_by, topic.slug),
        )

    # Replace leaves — delete-and-insert. Cheaper than diff for
    # small sets (~5-15 leaves per topic).
    cur.execute(
        "DELETE FROM topic_leaves WHERE topic_slug = %s",
        (topic.slug,),
    )
    for leaf in topic.leaves:
        cur.execute(
            """
            INSERT INTO topic_leaves
              (topic_slug, leaf_id, role, workflow_order, role_note)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (topic.slug, leaf.leaf_id, leaf.role, leaf.workflow_order,
             leaf.role_note),
        )
    return "inserted" if is_new else "updated"


def _sweep_orphans(cur, current_slugs: set[str]) -> int:
    """Delete topics whose YAML file no longer exists."""
    cur.execute("SELECT slug FROM topics")
    existing = {r[0] for r in cur.fetchall()}
    orphans = existing - current_slugs
    if not orphans:
        return 0
    for slug in orphans:
        cur.execute("DELETE FROM topics WHERE slug = %s", (slug,))
    return len(orphans)


# ── Main ──────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument(
        "--db-url",
        default=os.environ.get("DATABASE_URL"),
        help="Postgres connection URL (default: DATABASE_URL env)",
    )
    parser.add_argument(
        "--loaded-by",
        default="topics/load_to_postgres.py",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse + validate but don't write to Postgres",
    )
    args = parser.parse_args(argv)

    if not args.dry_run and not args.db_url:
        print("ERROR: DATABASE_URL not set and --db-url not given", file=sys.stderr)
        return 1

    leaf_index = _build_leaf_index()

    files = sorted(TOPICS_DIR.glob("*.yaml"))
    if not files:
        print(f"WARNING: no topic files found in {TOPICS_DIR}")
        return 0

    # Parse + validate all first — fail fast, no partial DB writes
    parsed: list[Topic] = []
    failures: list[str] = []
    for fpath in files:
        try:
            parsed.append(_parse_topic_file(fpath, leaf_index))
        except ValueError as e:
            failures.append(f"{fpath.name}: {e}")

    if failures:
        print(f"FAILED validation on {len(failures)} topic(s):")
        for f in failures[:20]:
            print(f"  ✗ {f}")
        return 1

    # Check for slug collisions across files
    slug_files: dict[str, list[str]] = {}
    for t in parsed:
        slug_files.setdefault(t.slug, []).append(t.source_file)
    dups = {s: fs for s, fs in slug_files.items() if len(fs) > 1}
    if dups:
        print(f"FAILED: duplicate slug across files:")
        for s, fs in dups.items():
            print(f"  ✗ {s!r} in {fs}")
        return 1

    if args.dry_run:
        print(f"[DRY-RUN] {len(parsed)} topics parsed + validated; no DB writes")
        for t in parsed:
            print(f"  ✓ {t.slug:30s} ({t.primary_framework:15s}) "
                  f"{len(t.leaves)} leaves")
        return 0

    # Persist
    import psycopg2
    conn = psycopg2.connect(args.db_url)
    cur  = conn.cursor()

    counts = {"inserted": 0, "updated": 0, "unchanged": 0}
    try:
        for topic in parsed:
            action = _upsert_topic(cur, topic, args.loaded_by)
            counts[action] += 1
        current_slugs = {t.slug for t in parsed}
        orphans = _sweep_orphans(cur, current_slugs)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    print(
        f"topics load: inserted={counts['inserted']} "
        f"updated={counts['updated']} unchanged={counts['unchanged']} "
        f"orphans_swept={orphans} total={len(parsed)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
