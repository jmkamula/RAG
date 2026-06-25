#!/usr/bin/env python3
"""
generate_template_scaffolds.py — emit markdown template scaffolds for every
EvidenceRequirement leaf in the curation.

Behaviour
---------
* Reads ALL_EVIDENCE_REQUIREMENTS + every DerivedSpec.direct_evidence
  (pure-derived specs without direct_evidence are SKIPPED — they resolve
  transitively via derives_from, no template needed).
* For each leaf, writes db/templates/{leaf_kebab}.md containing:
    - YAML frontmatter binding to the leaf (id, control_ref, standard_id,
      template_version, must/should counts)
    - Title + leaf description
    - One section per MUST item: header + <<MUST item:X>> marker + the
      item's text as the section guidance + a <<TEXT>> placeholder for
      tenant content
    - "Recommended additions" sub-section per SHOULD item (same shape,
      <<SHOULD item:X>> marker)
* Preserves hand-refined templates — any existing file with frontmatter
  `template_version >= 2` is left untouched and reported as skipped.

Auto-generated scaffolds are template_version=1.

Per the architecture decisions captured in
[[curation-document-templates-idea]] + the 2026-06-24 session — the
canonical artefact is markdown with structured `<<MUST item:X>>` section
markers enabling deterministic (no-LLM) extraction on roundtrip.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional


# Resolve repo root assuming this script lives in scripts/
REPO_ROOT     = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "db" / "templates"


def _kebab(leaf_id: str) -> str:
    """req:A.5.15:access_control_policy → req__A_5_15__access_control_policy.md

    Two colons → two pairs of underscores so the leaf prefix stays
    visually distinct from the leaf slug. Dots in control_ref → single
    underscore to remain filesystem-safe.
    """
    return leaf_id.replace(":", "__").replace(".", "_") + ".md"


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _extract_template_version(body: str) -> Optional[int]:
    """Parse `template_version: N` from frontmatter; None if no frontmatter."""
    m = _FRONTMATTER_RE.match(body)
    if not m:
        return None
    fm = m.group(1)
    for line in fm.splitlines():
        if line.strip().startswith("template_version:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except (IndexError, ValueError):
                return None
    return None


_TABULAR_EVIDENCE_SUFFIXES = ("_register", "_record", "_matrix", "_log", "_inventory")
_TABULAR_EVIDENCE_EXACT = {
    "register",
    "statement_of_applicability",
    "records_of_processing",
    "review_record",
    "responsibility_matrix",
    "segregation_matrix",
    "communication_record",
    "monitoring_record",
    "test_log",
    "data_flow_inventory",
    "lawful_basis_register",
    "revocation_record",
    "approval_record",
    "audit_record",
    "configuration_record",
    "publication_record",
    "change_record",
    "discovery_record",
    "risk_assessment_record",
    "risk_treatment_record",
    "decision_record",
    "contact_register",
    "asset_register",
}


def _is_tabular_evidence(evidence_type: str) -> bool:
    """Classify the leaf's shape — tabular evidence types render as one
    table + per-column guidance (registers, records, matrices, logs).
    Narrative types render as per-MUST sections (policies, procedures,
    scope notes, etc.).
    """
    if not evidence_type:
        return False
    if evidence_type in _TABULAR_EVIDENCE_EXACT:
        return True
    return any(evidence_type.endswith(s) for s in _TABULAR_EVIDENCE_SUFFIXES)


def _column_header_from_item(item) -> str:
    """Derive a short column header from the MUST item slug.

    item.id format: 'item:A.5.9:owner_per_asset' → 'Owner Per Asset'
    """
    slug = item.id.split(":")[-1] if item.id else ""
    return slug.replace("_", " ").title() or "Field"


def _render_template_tabular(leaf) -> str:
    """Compose markdown for a tabular leaf (register / record / matrix /
    log / inventory). Single edit-zone wraps the table; per-MUST
    guidance lives in a separate Column guidance section.

    Schema markers:
      <!-- TABLE-COLUMNS leaf:<leaf_id> -->
      <!-- column: <item_id> -->
      ...
      <!-- /TABLE-COLUMNS -->

      <!-- EDIT-ZONE-START leaf:<leaf_id> -->
      | <header> | <header> | ... |
      |---|---|---|
      |          |          |     |
      <!-- EDIT-ZONE-END leaf:<leaf_id> -->

    The extractor reads the metadata block to map column index →
    item_id, parses the table, and binds per-column MUST satisfaction
    (any non-empty cell in a column → that MUST is present).
    """
    must_count   = len(leaf.must_contain)
    should_count = len(leaf.should_contain)
    desc         = (leaf.description or "").strip()
    freshness    = leaf.freshness_days if leaf.freshness_days else None
    headers      = [_column_header_from_item(item) for item in leaf.must_contain]

    lines: list[str] = []
    lines.append("---")
    lines.append(f"leaf_id: {leaf.id}")
    lines.append(f"control_ref: {leaf.control_ref}")
    lines.append(f"standard_id: {leaf.standard_id}")
    lines.append(f"evidence_type: {leaf.evidence_type}")
    lines.append(f"trigger_type: {leaf.trigger_type or 'universal'}")
    if freshness:
        lines.append(f"freshness_days: {freshness}")
    lines.append(f"template_version: 1")
    lines.append(f"must_count: {must_count}")
    lines.append(f"should_count: {should_count}")
    lines.append("table_shape: true")
    lines.append("---")
    lines.append("")
    lines.append(f"# {leaf.title}")
    lines.append("")
    if desc:
        for d_line in desc.splitlines():
            lines.append(f"> {d_line}" if d_line else ">")
        lines.append("")

    # Column metadata block — tells the extractor which column maps to
    # which checklist_item_id. Order in this block = column order in
    # the table.
    lines.append(f"<!-- TABLE-COLUMNS leaf:{leaf.id} -->")
    for item in leaf.must_contain:
        lines.append(f"<!-- column: {item.id} -->")
    lines.append("<!-- /TABLE-COLUMNS -->")
    lines.append("")

    lines.append("## Register")
    lines.append("")
    lines.append(
        "Fill one row per record. Each column maps to a MUST item the "
        "auditor will check — empty columns count as unsatisfied. "
        "Add as many rows as you need."
    )
    lines.append("")

    # The editable table inside the EDIT-ZONE.
    header_row    = "| " + " | ".join(headers) + " |"
    separator_row = "|" + "|".join(["---"] * len(headers)) + "|"
    blank_row     = "|" + "|".join([" " * 10] * len(headers)) + "|"
    lines.append(f"<!-- EDIT-ZONE-START leaf:{leaf.id} -->")
    lines.append(header_row)
    lines.append(separator_row)
    for _ in range(3):
        lines.append(blank_row)
    lines.append(f"<!-- EDIT-ZONE-END leaf:{leaf.id} -->")
    lines.append("")

    lines.append("## Column guidance — what to fill in")
    lines.append("")
    for i, item in enumerate(leaf.must_contain):
        header = headers[i]
        lines.append(f"### {header}")
        lines.append("")
        lines.append(f"<<MUST {item.id}>>")
        if item.rationale:
            lines.append(f"_Why: {item.rationale}_")
        lines.append("")
        lines.append(f"> _Standard text:_ {item.text}")
        lines.append("")

    # SHOULDs — recommended additional columns
    if leaf.should_contain:
        lines.append("---")
        lines.append("")
        lines.append("## Recommended additional columns")
        lines.append("")
        lines.append(
            "_These columns strengthen the register but are not strictly "
            "required for the MUST checks. Add them to the table if they "
            "apply to your environment._"
        )
        lines.append("")
        for j, item in enumerate(leaf.should_contain, start=1):
            header = _column_header_from_item(item)
            lines.append(f"### {header}")
            lines.append("")
            lines.append(f"<<SHOULD {item.id}>>")
            if item.rationale:
                lines.append(f"_Why: {item.rationale}_")
            lines.append("")
            lines.append(f"> _Standard text:_ {item.text}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _render_template(leaf) -> str:
    """Compose the markdown body for one leaf's scaffold.

    Dispatches by evidence_type:
      - tabular (register / record / matrix / log / inventory) →
        single-table layout with per-column guidance
      - narrative (policy / procedure / scope_note / plan / ...) →
        per-MUST sections (existing default)
    """
    if _is_tabular_evidence(leaf.evidence_type):
        return _render_template_tabular(leaf)
    return _render_template_narrative(leaf)


def _render_template_narrative(leaf) -> str:
    """Compose the markdown body for a narrative-shape leaf (existing
    default — per-MUST sections)."""
    must_count   = len(leaf.must_contain)
    should_count = len(leaf.should_contain)
    desc         = (leaf.description or "").strip()
    freshness    = leaf.freshness_days if leaf.freshness_days else None

    lines: list[str] = []
    lines.append("---")
    lines.append(f"leaf_id: {leaf.id}")
    lines.append(f"control_ref: {leaf.control_ref}")
    lines.append(f"standard_id: {leaf.standard_id}")
    lines.append(f"evidence_type: {leaf.evidence_type}")
    lines.append(f"trigger_type: {leaf.trigger_type or 'universal'}")
    if freshness:
        lines.append(f"freshness_days: {freshness}")
    lines.append(f"template_version: 1")
    lines.append(f"must_count: {must_count}")
    lines.append(f"should_count: {should_count}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {leaf.title}")
    lines.append("")
    if desc:
        # Indent description as blockquote to render as guidance
        for d_line in desc.splitlines():
            lines.append(f"> {d_line}" if d_line else ">")
        lines.append("")

    lines.append(
        "> **Replace each blank fill-in marker with your content. Leave the "
        "MUST and SHOULD heading markers untouched — "
        "they bind this document to the checklist when you upload it back.**"
    )
    lines.append("")

    # MUSTs
    for i, item in enumerate(leaf.must_contain, start=1):
        lines.append(f"## {i}. {item.text}")
        lines.append("")
        lines.append(f"<<MUST {item.id}>>")
        if item.rationale:
            lines.append(f"_Why: {item.rationale}_")
        lines.append("")
        lines.append("<<TEXT>>")
        lines.append("")

    # SHOULDs (recommended additions)
    if leaf.should_contain:
        lines.append("---")
        lines.append("")
        lines.append("## Recommended additions")
        lines.append("")
        lines.append(
            "_The items below strengthen the artefact but are not "
            "strictly required for the MUST checks. Fill in any that "
            "apply to your environment._"
        )
        lines.append("")
        for j, item in enumerate(leaf.should_contain, start=1):
            lines.append(f"### {j}. {item.text}")
            lines.append("")
            lines.append(f"<<SHOULD {item.id}>>")
            if item.rationale:
                lines.append(f"_Why: {item.rationale}_")
            lines.append("")
            lines.append("<<TEXT>>")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be written without touching the filesystem",
    )
    parser.add_argument(
        "--force-overwrite", action="store_true",
        help="Overwrite even hand-refined (template_version >= 2) templates",
    )
    args = parser.parse_args(argv)

    # Ensure import path before importing curation
    sys.path.insert(0, str(REPO_ROOT))

    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )

    # Collect every leaf — both top-level ERs and DerivedSpec.direct_evidence.
    # Pure DerivedSpecs (no direct_evidence) resolve transitively via
    # derives_from chains; they don't need their own template.
    leaves = list(ALL_EVIDENCE_REQUIREMENTS)
    for spec in ALL_DERIVED_SPECS:
        leaves.extend(spec.direct_evidence)

    # Dedup on id (rare but possible)
    seen: set[str] = set()
    unique_leaves = []
    for leaf in leaves:
        if leaf.id in seen:
            continue
        seen.add(leaf.id)
        unique_leaves.append(leaf)

    if not args.dry_run:
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    written  = 0
    skipped  = 0
    skipped_refined: list[str] = []

    for leaf in unique_leaves:
        fname = _kebab(leaf.id)
        fpath = TEMPLATES_DIR / fname

        # Preserve hand-refined templates
        if fpath.exists() and not args.force_overwrite:
            existing_version = _extract_template_version(fpath.read_text())
            if existing_version is not None and existing_version >= 2:
                skipped += 1
                skipped_refined.append(f"{leaf.id} (v{existing_version})")
                continue

        body = _render_template(leaf)
        if args.dry_run:
            print(f"[DRY-RUN] would write {fpath.relative_to(REPO_ROOT)} "
                  f"({len(body)} bytes, must={len(leaf.must_contain)} "
                  f"should={len(leaf.should_contain)})")
        else:
            fpath.write_text(body)
        written += 1

    action = "would write" if args.dry_run else "wrote"
    print(f"\n{action} {written} templates; preserved {skipped} hand-refined")
    if skipped_refined:
        print("Hand-refined templates preserved:")
        for s in skipped_refined[:10]:
            print(f"  {s}")
        if len(skipped_refined) > 10:
            print(f"  ... +{len(skipped_refined) - 10} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
