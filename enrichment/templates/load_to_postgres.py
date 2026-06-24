#!/usr/bin/env python3
"""
load_to_postgres.py — load template artefacts from db/templates/*.md into
the Postgres templates table.

Behaviour
---------
* Walks db/templates/, parses each file's YAML frontmatter + body
* Validates:
    - leaf_id in frontmatter exists in ALL_EVIDENCE_REQUIREMENTS or any
      DerivedSpec.direct_evidence
    - <<MUST item:X>> markers in body match the leaf's must_contain ids
      1:1 (no missing, no extra)
* Counts <<MUST ...>> and <<SHOULD ...>> markers and persists into
  templates table (upsert by leaf_id)
* Reports written/updated/unchanged/failed counts

Run after `generate_template_scaffolds.py` (or after editing any
template in db/templates/).

Failure modes are loud — a curation change that adds a MUST but
doesn't re-run the generator will fail this loader's build gate.
That's the intended contract: templates evolve with curation.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


REPO_ROOT     = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = REPO_ROOT / "db" / "templates"

_FRONTMATTER_RE  = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# item id shape: item:<control_ref>:<slug>
#   control_ref: alphanumerics + dots (A.5.15 / Art.32 / 4.3)
#   slug:        lowercase + underscores + digits
# Tightened from `item:[^>\s]+` to avoid matching example placeholders
# like `item:X` in instruction prose.
_MUST_MARKER_RE   = re.compile(r"<<MUST\s+(item:[A-Za-z0-9.]+:[a-z0-9_]+)>>")
_SHOULD_MARKER_RE = re.compile(r"<<SHOULD\s+(item:[A-Za-z0-9.]+:[a-z0-9_]+)>>")


@dataclass
class TemplateRow:
    leaf_id:          str
    template_version: int
    body_md:          str
    source_file:      str
    must_count:       int
    should_count:     int


def _parse_frontmatter(body: str) -> dict[str, str]:
    m = _FRONTMATTER_RE.match(body)
    if not m:
        raise ValueError("missing YAML frontmatter (--- ... ---)")
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def _parse_template_file(path: Path, leaf_index: dict[str, "object"]) -> TemplateRow:
    """Returns a TemplateRow or raises ValueError if validation fails."""
    body = path.read_text()
    fm   = _parse_frontmatter(body)

    leaf_id = fm.get("leaf_id")
    if not leaf_id:
        raise ValueError("frontmatter missing leaf_id")

    leaf = leaf_index.get(leaf_id)
    if leaf is None:
        raise ValueError(f"leaf_id {leaf_id!r} not in ALL_EVIDENCE_REQUIREMENTS or DerivedSpec.direct_evidence")

    try:
        template_version = int(fm.get("template_version", "1"))
    except ValueError:
        raise ValueError(f"template_version must be int, got {fm.get('template_version')!r}")
    if template_version < 1:
        raise ValueError(f"template_version must be >= 1, got {template_version}")

    # MUST coverage check
    must_markers   = set(_MUST_MARKER_RE.findall(body))
    should_markers = set(_SHOULD_MARKER_RE.findall(body))
    leaf_must_ids  = {m.id for m in leaf.must_contain}
    leaf_should_ids = {m.id for m in leaf.should_contain}

    missing_musts = leaf_must_ids - must_markers
    extra_musts   = must_markers - leaf_must_ids
    if missing_musts:
        raise ValueError(
            f"template missing required MUST markers: {sorted(missing_musts)}"
        )
    if extra_musts:
        raise ValueError(
            f"template contains unknown MUST markers: {sorted(extra_musts)} "
            f"(curation may have changed; regen the scaffold or update the markers)"
        )

    # SHOULD markers are advisory — log unknown but don't fail
    extra_shoulds = should_markers - leaf_should_ids
    if extra_shoulds:
        print(f"  ⚠ {path.name}: unknown SHOULD markers {sorted(extra_shoulds)} (ignored)")

    return TemplateRow(
        leaf_id          = leaf_id,
        template_version = template_version,
        body_md          = body,
        source_file      = path.name,
        must_count       = len(must_markers),
        should_count     = len(should_markers),
    )


def _build_leaf_index() -> dict[str, "object"]:
    """leaf_id → EvidenceRequirement object."""
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


def _upsert(cur, row: TemplateRow, loaded_by: str) -> str:
    """Upsert one row, return 'inserted' / 'updated' / 'unchanged'."""
    cur.execute(
        "SELECT template_version, body_md FROM templates WHERE leaf_id = %s",
        (row.leaf_id,),
    )
    existing = cur.fetchone()
    if existing is None:
        cur.execute(
            """
            INSERT INTO templates (leaf_id, template_version, body_md,
                                   source_file, must_count, should_count,
                                   last_loaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (row.leaf_id, row.template_version, row.body_md, row.source_file,
             row.must_count, row.should_count, loaded_by),
        )
        return "inserted"
    if existing[0] == row.template_version and existing[1] == row.body_md:
        return "unchanged"
    cur.execute(
        """
        UPDATE templates
           SET template_version = %s,
               body_md          = %s,
               source_file      = %s,
               must_count       = %s,
               should_count     = %s,
               last_loaded_at   = now(),
               last_loaded_by   = %s
         WHERE leaf_id = %s
        """,
        (row.template_version, row.body_md, row.source_file,
         row.must_count, row.should_count, loaded_by, row.leaf_id),
    )
    return "updated"


def _upsert_neo4j(driver, parsed: list[TemplateRow]) -> dict[str, int]:
    """Attach each loaded template to its EvidenceRequirement in Neo4j as a
    thin (:Template) node + [:HAS_TEMPLATE] edge. Body stays in Postgres
    to avoid bloating graph nodes — Neo4j carries only the metadata
    needed for graph queries ("which leaves have hand-refined templates?"
    "find all GDPR Art.X templates"...).

    Schema:
        (er:EvidenceRequirement {id: $leaf_id})
            -[:HAS_TEMPLATE]->
        (t:Template {leaf_id, template_version, must_count, should_count,
                     source_file, last_loaded_at})

    Idempotent via MERGE; re-runs reset properties. Final orphan sweep
    removes any :Template node whose leaf_id is not in the loaded set
    (covers template file deletion or rename).
    """
    counts = {"merged": 0, "swept": 0}
    loaded_leaf_ids = [row.leaf_id for row in parsed]

    with driver.session() as s:
        for row in parsed:
            s.run(
                """
                MATCH (er:EvidenceRequirement {id: $leaf_id})
                MERGE (er)-[:HAS_TEMPLATE]->(t:Template {leaf_id: $leaf_id})
                SET   t.template_version = $template_version,
                      t.must_count       = $must_count,
                      t.should_count     = $should_count,
                      t.source_file      = $source_file,
                      t.last_loaded_at   = datetime()
                """,
                leaf_id          = row.leaf_id,
                template_version = row.template_version,
                must_count       = row.must_count,
                should_count     = row.should_count,
                source_file      = row.source_file,
            )
            counts["merged"] += 1

        # Orphan sweep — any :Template not in the loaded set is stale
        sweep = s.run(
            """
            MATCH (t:Template)
            WHERE NOT t.leaf_id IN $loaded
            DETACH DELETE t
            RETURN count(t) AS swept
            """,
            loaded=loaded_leaf_ids,
        )
        rec = sweep.single()
        counts["swept"] = rec["swept"] if rec else 0

    return counts


def _build_neo4j_driver():
    """Construct a Neo4j driver from env. Returns None on missing config
    so the loader can still run Postgres-only when Neo4j is unreachable."""
    from neo4j import GraphDatabase
    uri      = os.environ.get("NEO4J_URI")
    user     = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    if not (uri and user and password):
        return None
    return GraphDatabase.driver(uri, auth=(user, password))


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument(
        "--db-url",
        default=os.environ.get("DATABASE_URL"),
        help="Postgres connection URL (default: DATABASE_URL env)",
    )
    parser.add_argument(
        "--loaded-by",
        default="load_to_postgres.py",
        help="Provenance string written to last_loaded_by column",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse + validate but don't write to Postgres or Neo4j",
    )
    parser.add_argument(
        "--skip-neo4j", action="store_true",
        help="Postgres-only load; skip the (:Template) attachment step "
             "(useful when Neo4j is unreachable or for fast iteration)",
    )
    args = parser.parse_args(argv)

    if not args.dry_run and not args.db_url:
        print("ERROR: DATABASE_URL not set and --db-url not given", file=sys.stderr)
        return 1

    leaf_index = _build_leaf_index()

    files = sorted(TEMPLATES_DIR.glob("*.md"))
    if not files:
        print(f"WARNING: no template files found in {TEMPLATES_DIR}")
        return 0

    # Parse + validate first (fail fast — no partial DB writes)
    parsed: list[TemplateRow] = []
    failures: list[str] = []
    for fpath in files:
        try:
            parsed.append(_parse_template_file(fpath, leaf_index))
        except ValueError as e:
            failures.append(f"{fpath.name}: {e}")
    if failures:
        print(f"FAILED validation on {len(failures)} template(s):")
        for f in failures[:20]:
            print(f"  ✗ {f}")
        if len(failures) > 20:
            print(f"  ... +{len(failures) - 20} more")
        return 1

    if args.dry_run:
        print(f"[DRY-RUN] {len(parsed)} templates parsed + validated; no DB writes")
        return 0

    # Persist
    import psycopg2
    conn = psycopg2.connect(args.db_url)
    cur  = conn.cursor()

    counts = {"inserted": 0, "updated": 0, "unchanged": 0}
    try:
        for row in parsed:
            action = _upsert(cur, row, args.loaded_by)
            counts[action] += 1
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    print(
        f"templates load (Postgres): inserted={counts['inserted']} "
        f"updated={counts['updated']} unchanged={counts['unchanged']} "
        f"total={len(parsed)}"
    )

    # Neo4j attachment — thin (:Template) node + [:HAS_TEMPLATE] edge per
    # leaf. Body stays in Postgres; Neo4j gets metadata for graph queries.
    if args.skip_neo4j:
        print("templates load (Neo4j): SKIPPED (--skip-neo4j)")
        return 0

    driver = _build_neo4j_driver()
    if driver is None:
        print("templates load (Neo4j): SKIPPED (no NEO4J_URI/USER/PASSWORD)")
        return 0

    try:
        neo_counts = _upsert_neo4j(driver, parsed)
    finally:
        driver.close()
    print(
        f"templates load (Neo4j): merged={neo_counts['merged']} "
        f"orphans_swept={neo_counts['swept']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
