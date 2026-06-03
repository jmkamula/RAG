"""Audit DerivedSpec references to a given control's items.

Promotions/alignments must preserve any ChecklistItem ids that a DerivedSpec
cites via DerivedFrom.scope_items, otherwise the derivation breaks silently
at load time.

Usage:
  python3 scripts/audit_derived_spec_refs.py A.5.26
  python3 scripts/audit_derived_spec_refs.py Art.15 Art.30
  python3 scripts/audit_derived_spec_refs.py --all

The script imports document_requirements directly and walks every DerivedSpec
in the module — no regex, no AST.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from enrichment.documents import document_requirements as DR


def _iter_derived_specs():
    """Yield (name, spec) for every DerivedSpec defined in the module."""
    for name in sorted(dir(DR)):
        obj = getattr(DR, name)
        if isinstance(obj, DR.DerivedSpec):
            yield name, obj


def _refs_for_control(ref: str):
    """Find every DerivedSpec/DerivedFrom that names items under `ref`.

    Returns a list of dicts: {spec, derives_from_target, scope_items}.
    """
    out = []
    needle = f"item:{ref}:"
    for spec_name, spec in _iter_derived_specs():
        for df in spec.derives_from:
            target = f"{df.target_standard_id}:{df.target_control_ref}"
            if df.target_control_ref != ref:
                continue
            out.append({
                "spec":            spec_name,
                "spec_id":         spec.spec_id,
                "target":          target,
                "role":            df.role,
                "scope_items":     list(df.scope_items) if df.scope_items else None,
            })
    return out


def _all_referenced_controls():
    """Map control_ref → list of (spec_name, scope_items_or_None)."""
    by_ref: dict[str, list] = {}
    for spec_name, spec in _iter_derived_specs():
        for df in spec.derives_from:
            by_ref.setdefault(df.target_control_ref, []).append(
                (spec_name, df.scope_items)
            )
    return by_ref


def _audit_one(ref: str) -> int:
    refs = _refs_for_control(ref)
    print(f"\n── {ref} ──")
    if not refs:
        print("  (no DerivedSpec references — safe to rename items)")
        return 0

    risk = 0
    for r in refs:
        if r["scope_items"]:
            risk += len(r["scope_items"])
            print(f"  {r['spec']:18s} [{r['role']}] scope_items:")
            for item in r["scope_items"]:
                print(f"      - {item}")
        else:
            print(f"  {r['spec']:18s} [{r['role']}] whole-control derivation")
            print(f"      (no specific item-ids cited — rename is safe but watch the role label)")
    if risk:
        print(f"  → {risk} item-id(s) must be preserved across promotion")
    return risk


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("refs", nargs="*", help="Control refs to audit, e.g. A.5.26 Art.15")
    p.add_argument("--all", action="store_true",
                   help="List every control referenced by any DerivedSpec")
    args = p.parse_args()

    if args.all:
        by_ref = _all_referenced_controls()
        print(f"DerivedSpec-referenced controls ({len(by_ref)}):\n")
        for ref in sorted(by_ref):
            specs = by_ref[ref]
            with_items = sum(1 for _, items in specs if items)
            tag = f"[{with_items} item-citing]" if with_items else "[whole-control only]"
            spec_names = ", ".join(sorted({s for s, _ in specs}))
            print(f"  {ref:14s} {tag:22s} {spec_names}")
        return 0

    if not args.refs:
        p.error("supply at least one ref, or use --all")

    total = 0
    for ref in args.refs:
        total += _audit_one(ref)
    print(f"\n{'─' * 60}")
    print(f"Total item-ids that must be preserved across {len(args.refs)} control(s): {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
