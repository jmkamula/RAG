"""
ArionComply — Relationship Catalog Validator

Static checks on ALL_EDGES in `enrichment/relationships/
relationship_catalog.py`. Run before any commit that touches the
catalog; CI will run this on every change.

Checks:
  1. Format — source_ref / target_ref + standard_id known
  2. Edge type — in MANAGED_EDGE_TYPES
  3. Catalog membership — source + target controls exist in the
     canonical union (ALL_EVIDENCE_REQUIREMENTS + DerivedSpec
     direct_evidence + RequirementNode-only refs)
  4. Citation present (warn-only — reviewers verify)
  5. Symmetric edges authored once (no manual a→b + b→a duplicates)
  6. No self-loops
  7. No duplicate (source, target, edge_type) triples

Usage:
    python3 scripts/validate_relationship_catalog.py
    python3 scripts/validate_relationship_catalog.py --strict   # exit 1 on warnings

See: docs/relationship_model_design_2026_06_29.md §9
"""
from __future__ import annotations
import argparse, os, re, sys
from collections import Counter
from typing import Iterable

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from enrichment.relationships.relationship_catalog import (
    ALL_EDGES,
    MANAGED_EDGE_TYPES,
    SYMMETRIC_EDGE_TYPES,
    KNOWN_STANDARD_IDS,
    RelationshipEdge,
)

REF_PATTERNS = {
    "ISO27001:2022": re.compile(r"^(A\.\d+\.\d+|\d+(\.\d+){1,2})$"),
    # A.5.16 / A.8.2 / 4.1 / 6.1.2
    "GDPR:2016/679": re.compile(r"^Art\.\d+(\.\d+)*(\.[a-z])?$"),
    # Art.32 / Art.5.1.f / Art.14.5
}


def _build_catalog_ref_set() -> set[str]:
    """Canonical set of (standard_id, ref) tuples — union of ALL_EVIDENCE_
    REQUIREMENTS leaves + DerivedSpec.direct_evidence leaves + DerivedSpec
    targets + ISMS clauses derivable from leaf refs. Mirrors the catalog-
    membership predicate from [[feedback-validate-set-membership]].

    Returned shape: set of "STANDARD_ID:ref" strings.
    """
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )

    refs: set[str] = set()
    # ── EvidenceRequirement leaves
    for er in list(ALL_EVIDENCE_REQUIREMENTS):
        refs.add(f"{er.standard_id}:{er.control_ref}")
    # ── DerivedSpec direct_evidence
    for ds in ALL_DERIVED_SPECS:
        for er in ds.direct_evidence:
            refs.add(f"{er.standard_id}:{er.control_ref}")
    # ── DerivedSpec controls themselves (Art.32 etc.)
    for ds in ALL_DERIVED_SPECS:
        refs.add(f"{ds.standard_id}:{ds.control_ref}")
    # ── DerivedFrom targets (ISO controls referenced from GDPR specs)
    for ds in ALL_DERIVED_SPECS:
        for df in ds.derives_from:
            refs.add(f"{df.target_standard_id}:{df.target_control_ref}")
    return refs


def validate(edges: Iterable[RelationshipEdge]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    catalog_refs = _build_catalog_ref_set()

    # ── 6. No self-loops + 7. no duplicates
    seen_triples = Counter()
    seen_pairs_with = set()  # for symmetric duplicate detection

    for i, e in enumerate(edges):
        prefix = f"edge #{i} ({e.source_standard_id}:{e.source_ref} -[{e.edge_type}]-> {e.target_standard_id}:{e.target_ref})"

        # ── 1. Format
        if e.source_standard_id not in KNOWN_STANDARD_IDS:
            errors.append(f"{prefix}: unknown source standard_id")
        if e.target_standard_id not in KNOWN_STANDARD_IDS:
            errors.append(f"{prefix}: unknown target standard_id")

        for ref, std in [(e.source_ref, e.source_standard_id), (e.target_ref, e.target_standard_id)]:
            pat = REF_PATTERNS.get(std)
            if pat and not pat.match(ref):
                errors.append(f"{prefix}: ref {ref!r} doesn't match {std} pattern")

        # ── 2. Edge type
        if e.edge_type not in MANAGED_EDGE_TYPES:
            errors.append(f"{prefix}: edge_type {e.edge_type!r} not in MANAGED_EDGE_TYPES")

        # ── 3. Catalog membership
        src_node = f"{e.source_standard_id}:{e.source_ref}"
        tgt_node = f"{e.target_standard_id}:{e.target_ref}"
        if src_node not in catalog_refs:
            errors.append(f"{prefix}: source {src_node} not in catalog")
        if tgt_node not in catalog_refs:
            errors.append(f"{prefix}: target {tgt_node} not in catalog")

        # ── 4. Citation present (warn)
        if not e.citation:
            warnings.append(f"{prefix}: no citation — reviewer should verify")

        # ── 5. Symmetric duplicate detection
        if e.edge_type in SYMMETRIC_EDGE_TYPES:
            # Canonical pair = sorted endpoints
            key = (e.edge_type,) + tuple(sorted([src_node, tgt_node]))
            if key in seen_pairs_with:
                errors.append(
                    f"{prefix}: symmetric edge {e.edge_type} authored twice "
                    f"(reverse direction also present) — author once, loader inverts"
                )
            seen_pairs_with.add(key)

        # ── 6. Self-loop
        if src_node == tgt_node:
            errors.append(f"{prefix}: self-loop forbidden")

        # ── 7. Duplicate triple
        triple = (src_node, tgt_node, e.edge_type)
        seen_triples[triple] += 1

    for triple, count in seen_triples.items():
        if count > 1:
            errors.append(f"duplicate edge x{count}: {triple[0]} -[{triple[2]}]-> {triple[1]}")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description="Validate relationship_catalog.py")
    ap.add_argument("--strict", action="store_true",
                    help="Exit 1 on warnings as well as errors")
    args = ap.parse_args()

    print(f"Validating {len(ALL_EDGES)} edges...")
    errors, warnings = validate(ALL_EDGES)

    if errors:
        print(f"\n[ERROR x{len(errors)}]")
        for e in errors:
            print(f"  {e}")
    if warnings:
        print(f"\n[WARN x{len(warnings)}]")
        for w in warnings[:20]:
            print(f"  {w}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more warnings")

    if not errors and not warnings:
        print("OK — catalog is clean")

    if errors:
        sys.exit(1)
    if warnings and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
