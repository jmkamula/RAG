"""
Resolves per-MUST guidance from a flat YAML store and applies it to
ChecklistItems in the catalog.

Shipped in Ship 56'.a (2026-08-05). Replaces the tier-based resolver
from Ship 55' with a flat one-YAML-per-MUST model.

Filename convention:
    enrichment/guidance/{control_ref}/{slug}.yaml
    where slug is the trailing segment of must_id (item:{ctrl}:{slug}).

Storage shape (YAML):
    must_id: item:5.2:owner
    control_ref: 5.2
    standard_id: ISO27001:2022
    must_text: "Named owner of the policy (ISMS Manager)"
    category: must                  # or "should"
    curation_status: draft          # draft | reviewed | approved
    guidance:
      - <imperative step 1>
      - <imperative step 2>
      ...

Mutates ChecklistItem.guidance in place. Call BEFORE loading Neo4j so
the write picks up resolved values.

Usage:
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    from enrichment.guidance.apply_to_catalog import apply_guidance_to_catalog

    report = apply_guidance_to_catalog(
        ALL_EVIDENCE_REQUIREMENTS,
        ALL_DERIVED_SPECS,
    )

CLI:
    python3 -m enrichment.guidance.apply_to_catalog --dry-run --json
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml


_GUIDANCE_ROOT = Path(__file__).resolve().parent


@dataclass
class ResolveReport:
    covered:       int = 0
    empty:         int = 0
    total:         int = 0
    warnings:      list[str] = field(default_factory=list)
    yamls_loaded:  int = 0
    by_status:     dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "covered":      self.covered,
            "empty":        self.empty,
            "total":        self.total,
            "yamls_loaded": self.yamls_loaded,
            "by_status":    self.by_status,
            "warnings":     self.warnings,
        }


def _load_guidance_yamls(warnings: list[str]) -> tuple[dict[str, tuple[str, ...]], dict[str, int]]:
    """Load every guidance YAML under enrichment/guidance/{ctrl}/{slug}.yaml.

    Returns:
      (must_id -> guidance tuple, status -> count)
    """
    out: dict[str, tuple[str, ...]] = {}
    by_status: dict[str, int] = {}
    if not _GUIDANCE_ROOT.exists():
        return out, by_status

    for path in sorted(_GUIDANCE_ROOT.rglob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            warnings.append(f"{path.relative_to(_GUIDANCE_ROOT)}: YAML parse error: {e}")
            continue
        if not isinstance(data, dict):
            warnings.append(f"{path.relative_to(_GUIDANCE_ROOT)}: root must be a mapping")
            continue
        must_id = data.get("must_id")
        guidance = data.get("guidance")
        status = (data.get("curation_status") or "draft").lower()
        if not must_id or not isinstance(must_id, str):
            warnings.append(f"{path.relative_to(_GUIDANCE_ROOT)}: missing/invalid 'must_id'")
            continue
        if not isinstance(guidance, list) or not all(isinstance(g, str) for g in guidance):
            warnings.append(f"{path.relative_to(_GUIDANCE_ROOT)}: 'guidance' must be a list of strings")
            continue
        if not guidance:
            warnings.append(f"{path.relative_to(_GUIDANCE_ROOT)}: empty guidance list")
            continue
        if must_id in out:
            warnings.append(f"duplicate must_id '{must_id}' in {path.relative_to(_GUIDANCE_ROOT)}")
        out[must_id] = tuple(guidance)
        by_status[status] = by_status.get(status, 0) + 1
    return out, by_status


def apply_guidance_to_catalog(
    all_evidence_requirements: Iterable,
    all_derived_specs: Iterable = (),
    dry_run: bool = False,
) -> ResolveReport:
    """Walk every ChecklistItem in the catalog, resolve guidance from the
    flat YAML store, and (if not dry_run) mutate item.guidance in place.
    """
    report = ResolveReport()
    lookup, by_status = _load_guidance_yamls(report.warnings)
    report.yamls_loaded = len(lookup)
    report.by_status = by_status

    def _walk(req):
        for item in list(req.must_contain) + list(req.should_contain):
            resolved = lookup.get(item.id, ())
            report.total += 1
            if resolved:
                report.covered += 1
            else:
                report.empty += 1
            if not dry_run:
                item.guidance = resolved

    for req in all_evidence_requirements:
        _walk(req)
    for ds in all_derived_specs:
        for req in ds.direct_evidence:
            _walk(req)

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Resolve per-MUST guidance from flat YAML store"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Report without mutating the catalog")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON summary (implies --dry-run)")
    args = parser.parse_args()

    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    report = apply_guidance_to_catalog(
        ALL_EVIDENCE_REQUIREMENTS,
        ALL_DERIVED_SPECS,
        dry_run=args.dry_run or args.json,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return

    print("Guidance resolver report")
    print("=" * 50)
    print(f"  YAMLs loaded:  {report.yamls_loaded}")
    if report.by_status:
        for status, n in sorted(report.by_status.items()):
            print(f"    curation_status={status:<9} {n:>5}")
    print(f"  Covered items: {report.covered:>6}")
    print(f"  Empty items:   {report.empty:>6}")
    print(f"  Total items:   {report.total:>6}")
    if report.warnings:
        print()
        print(f"  Warnings ({len(report.warnings)}):")
        for w in report.warnings:
            print(f"    ⚠ {w}")


if __name__ == "__main__":
    main()
