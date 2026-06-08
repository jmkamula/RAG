"""Validate every YAML in db/doc_mappings/ against the curated EvidenceRequirement set.

Catches typos in `target_leaves[].leaf_id` and `target_leaves[].control_ref`.
Exits non-zero on any unknown id. Mirror of validate_workbook_mappings.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

import yaml  # noqa: E402

from enrichment.documents.document_requirements import (  # noqa: E402
    ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
)


def _build_req_index() -> dict[str, "EvidenceRequirement"]:
    index = {er.id: er for er in ALL_EVIDENCE_REQUIREMENTS}
    for spec in ALL_DERIVED_SPECS:
        for er in spec.direct_evidence:
            index[er.id] = er
    return index


def main() -> int:
    reqs = _build_req_index()
    print(f"loaded {len(reqs)} curated requirements")

    mappings_dir = _ROOT / "db" / "doc_mappings"
    if not mappings_dir.exists():
        print(f"no doc_mappings dir at {mappings_dir}", file=sys.stderr)
        return 1

    files = sorted(mappings_dir.glob("*.yaml"))
    if not files:
        print("no doc_mappings YAMLs found", file=sys.stderr)
        return 1

    total_errs = 0
    for path in files:
        rel = path.relative_to(_ROOT)
        try:
            data = yaml.safe_load(path.read_text()) or {}
        except Exception as e:
            print(f"FAIL {rel}\n  - YAML parse error: {e}")
            total_errs += 1
            continue

        errs: list[str] = []
        if not data.get("mapping_id"):
            errs.append("missing mapping_id")
        if not data.get("filename_fingerprints"):
            errs.append("missing filename_fingerprints (or empty list)")
        target_leaves = data.get("target_leaves") or []
        if not target_leaves:
            errs.append("missing target_leaves (or empty list)")

        for i, t in enumerate(target_leaves):
            leaf_id = t.get("leaf_id")
            ctrl    = t.get("control_ref")
            if not leaf_id:
                errs.append(f"target_leaves[{i}]: missing leaf_id")
                continue
            if leaf_id not in reqs:
                errs.append(
                    f"target_leaves[{i}].leaf_id={leaf_id!r} not in "
                    f"ALL_EVIDENCE_REQUIREMENTS or any DerivedSpec.direct_evidence"
                )
                continue
            req_ctrl = reqs[leaf_id].control_ref
            if ctrl and str(ctrl) != req_ctrl:
                errs.append(
                    f"target_leaves[{i}]: control_ref={ctrl!r} but "
                    f"{leaf_id}.control_ref={req_ctrl!r}"
                )

        if errs:
            print(f"FAIL {rel}")
            for e in errs:
                print(f"  - {e}")
            total_errs += len(errs)
        else:
            print(f"OK   {rel}")

    print()
    if total_errs:
        print(f"{total_errs} error(s) across {len(files)} file(s)")
        return 1
    print(f"all {len(files)} file(s) clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
