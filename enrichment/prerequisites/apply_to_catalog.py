"""
Resolves per-leaf prerequisites from a flat YAML store and applies
them to EvidenceRequirements in the catalog.

Shipped in Ship 57' (2026-08-07). Same architecture as the Ship 56'
guidance resolver.

Filename convention:
    enrichment/prerequisites/{control_ref}/{evidence_type_slug}.yaml
    keyed by leaf_id (item:{ctrl}:{slug} → req:{ctrl}:{slug} in this
    module's case, since prereqs sit at the leaf level not MUST level).

YAML shape:
    leaf_id: req:A.5.15:access_control_policy
    control_ref: A.5.15
    standard_id: ISO27001:2022
    curation_status: draft
    prerequisites:
      - ref: "4.3"
        standard_id: "ISO27001:2022"
        title: "ISMS Scope Statement"
        category: foundational
        rationale: |
          ...
        good_enough: |
          ...

Mutates EvidenceRequirement.prerequisites in place.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml

from enrichment.documents.document_requirements import Prerequisite


_ROOT = Path(__file__).resolve().parent
_ALLOWED_CATEGORIES = {"foundational", "direct", "cross_role"}
_ALLOWED_STANDARDS  = {"ISO27001:2022", "ISO27701:2019", "GDPR:2016/679"}


@dataclass
class ResolveReport:
    covered:      int = 0
    empty:        int = 0
    total:        int = 0
    yamls_loaded: int = 0
    prereq_count: int = 0   # total prereq items across all authored YAMLs
    by_status:    dict[str, int] = field(default_factory=dict)
    warnings:     list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "covered":      self.covered,
            "empty":        self.empty,
            "total":        self.total,
            "yamls_loaded": self.yamls_loaded,
            "prereq_count": self.prereq_count,
            "by_status":    self.by_status,
            "warnings":     self.warnings,
        }


def _load_yamls(warnings: list[str]) -> tuple[dict[str, tuple[Prerequisite, ...]], dict[str, int], int]:
    """Load every prereq YAML.

    Returns (leaf_id -> tuple of Prerequisite, status -> count, total prereq items).
    """
    out: dict[str, tuple[Prerequisite, ...]] = {}
    by_status: dict[str, int] = {}
    total_items = 0
    if not _ROOT.exists():
        return out, by_status, total_items

    for path in sorted(_ROOT.rglob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            warnings.append(f"{path.relative_to(_ROOT)}: YAML parse error: {e}")
            continue
        if not isinstance(data, dict):
            warnings.append(f"{path.relative_to(_ROOT)}: root must be a mapping")
            continue

        leaf_id  = data.get("leaf_id")
        prereqs  = data.get("prerequisites")
        status   = (data.get("curation_status") or "draft").lower()
        if not leaf_id or not isinstance(leaf_id, str):
            warnings.append(f"{path.relative_to(_ROOT)}: missing/invalid 'leaf_id'")
            continue
        if not isinstance(prereqs, list):
            warnings.append(f"{path.relative_to(_ROOT)}: 'prerequisites' must be a list")
            continue
        if not prereqs:
            warnings.append(f"{path.relative_to(_ROOT)}: empty prerequisites list")
            continue

        resolved: list[Prerequisite] = []
        for i, item in enumerate(prereqs):
            if not isinstance(item, dict):
                warnings.append(f"{path.relative_to(_ROOT)}[{i}]: item must be a mapping")
                continue
            ref = item.get("ref")
            std = item.get("standard_id")
            title = item.get("title")
            cat = item.get("category")
            rat = item.get("rationale") or ""
            ge  = item.get("good_enough") or ""

            if not ref or not isinstance(ref, str):
                warnings.append(f"{path.relative_to(_ROOT)}[{i}]: missing/invalid 'ref'")
                continue
            if not std or std not in _ALLOWED_STANDARDS:
                warnings.append(
                    f"{path.relative_to(_ROOT)}[{i}]: 'standard_id' must be one of "
                    f"{sorted(_ALLOWED_STANDARDS)} (got {std!r})"
                )
                continue
            if not isinstance(title, str) or not title:
                warnings.append(f"{path.relative_to(_ROOT)}[{i}]: missing/invalid 'title'")
                continue
            if cat not in _ALLOWED_CATEGORIES:
                warnings.append(
                    f"{path.relative_to(_ROOT)}[{i}]: 'category' must be one of "
                    f"{sorted(_ALLOWED_CATEGORIES)} (got {cat!r})"
                )
                continue
            if not isinstance(rat, str) or not rat.strip():
                warnings.append(f"{path.relative_to(_ROOT)}[{i}]: 'rationale' must be a non-empty string")
                continue

            resolved.append(Prerequisite(
                ref=ref.strip(),
                standard_id=std,
                title=title.strip(),
                category=cat,
                rationale=rat.strip(),
                good_enough=(ge or "").strip(),
            ))

        if not resolved:
            continue

        if leaf_id in out:
            warnings.append(f"duplicate leaf_id '{leaf_id}' in {path.relative_to(_ROOT)}")
        out[leaf_id] = tuple(resolved)
        total_items += len(resolved)
        by_status[status] = by_status.get(status, 0) + 1

    return out, by_status, total_items


def apply_prerequisites_to_catalog(
    all_evidence_requirements: Iterable,
    all_derived_specs: Iterable = (),
    dry_run: bool = False,
) -> ResolveReport:
    """Walk every EvidenceRequirement in the catalog, resolve prerequisites
    from the YAML store, and (if not dry_run) mutate .prerequisites in place.
    """
    report = ResolveReport()
    lookup, by_status, total_items = _load_yamls(report.warnings)
    report.yamls_loaded = len(lookup)
    report.by_status    = by_status
    report.prereq_count = total_items

    def _walk(req):
        resolved = lookup.get(req.id, ())
        report.total += 1
        if resolved:
            report.covered += 1
        else:
            report.empty += 1
        if not dry_run:
            req.prerequisites = resolved

    for req in all_evidence_requirements:
        _walk(req)
    for ds in all_derived_specs:
        for req in ds.direct_evidence:
            _walk(req)

    return report


def main():
    parser = argparse.ArgumentParser(description="Resolve per-leaf prerequisites from YAML store")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    report = apply_prerequisites_to_catalog(
        ALL_EVIDENCE_REQUIREMENTS,
        ALL_DERIVED_SPECS,
        dry_run=args.dry_run or args.json,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return

    print("Prerequisites resolver report")
    print("=" * 50)
    print(f"  YAMLs loaded:  {report.yamls_loaded}")
    print(f"  Prereq items:  {report.prereq_count}")
    if report.by_status:
        for st, n in sorted(report.by_status.items()):
            print(f"    curation_status={st:<9} {n:>5}")
    print(f"  Covered leaves: {report.covered:>6}")
    print(f"  Empty leaves:   {report.empty:>6}")
    print(f"  Total leaves:   {report.total:>6}")
    if report.warnings:
        print()
        print(f"  Warnings ({len(report.warnings)}):")
        for w in report.warnings[:20]:
            print(f"    ⚠ {w}")


if __name__ == "__main__":
    main()
