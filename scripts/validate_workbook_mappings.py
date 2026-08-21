"""Validate db/workbook_mappings/*.yaml against curated ChecklistItem ids.

Catches typos in `target_evidence_requirement`, `target_control`, and every
`binds_to` id before they reach the Stage I engine (where they would silently
produce zero satisfaction). Exits non-zero on any unknown id.

Usage:
  python3 scripts/validate_workbook_mappings.py
  python3 scripts/validate_workbook_mappings.py db/workbook_mappings/incident_log.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from enrichment.documents import document_requirements as DR


def _build_id_index() -> tuple[dict[str, "DR.EvidenceRequirement"], dict[str, set[str]]]:
    """Return (req_by_id, items_by_req_id).

    `req_by_id` maps requirement id → EvidenceRequirement (covers
    ALL_EVIDENCE_REQUIREMENTS plus every DerivedSpec.direct_evidence entry).

    `items_by_req_id` maps requirement id → set of ChecklistItem ids
    (must + should). Used to validate binds_to belongs to the declared target.
    """
    reqs: dict[str, DR.EvidenceRequirement] = {}

    def _absorb(r: DR.EvidenceRequirement) -> None:
        if r.id in reqs and reqs[r.id] is not r:
            print(f"  ! duplicate requirement id in curation: {r.id}", file=sys.stderr)
        reqs[r.id] = r

    for r in DR.ALL_EVIDENCE_REQUIREMENTS:
        _absorb(r)

    for name in dir(DR):
        obj = getattr(DR, name)
        if isinstance(obj, DR.DerivedSpec):
            for r in obj.direct_evidence or []:
                _absorb(r)

    items_by_req: dict[str, set[str]] = {}
    for rid, req in reqs.items():
        ids = {ci.id for ci in (req.must_contain or [])}
        ids |= {ci.id for ci in (req.should_contain or [])}
        items_by_req[rid] = ids

    return reqs, items_by_req


def _iter_binds(pass_block: dict):
    """Yield (binds_to_id, source_label) for every binding declared in a pass."""
    for col in pass_block.get("required_columns") or []:
        bt = col.get("binds_to")
        if bt:
            yield bt, f"required_columns[{col.get('fingerprint')}]"

    for col in pass_block.get("optional_columns") or []:
        bt = col.get("binds_to")
        if bt:
            yield bt, f"optional_columns[{col.get('fingerprint')}]"

    for col in pass_block.get("cite_columns") or []:
        bt = col.get("binds_to")
        if bt:
            yield bt, f"cite_columns[{col.get('fingerprint')}]"

    for grp in pass_block.get("column_groups") or []:
        bt = grp.get("binds_to")
        if bt:
            yield bt, f"column_groups[{grp.get('group_name')}]"


# Ship 91'.i — cite_columns discipline validators.
# See docs/curation/cite_columns_criterion.md.

_CITE_DISALLOWED_SUFFIXES = ("_date", "_at", "_owner")
_CITE_DISALLOWED_EXACT = frozenset({"date", "at", "owner"})
_VALID_CITE_KINDS = frozenset({"internal_document", "url", "external_system"})


def _cite_bind_disallowed(must_id: str) -> bool:
    """True if MUST id ends in _date/_at/_owner (data-shape, not cite-shape)."""
    tail = (must_id or "").rsplit(":", 1)[-1]
    if tail in _CITE_DISALLOWED_EXACT:
        return True
    return any(tail.endswith(s) for s in _CITE_DISALLOWED_SUFFIXES)


def _validate_cite_discipline(pass_block: dict, pname: str) -> list[str]:
    """Check every cite_columns entry against the Ship 91'.h criterion.

    Rules:
      - binds_to MUST NOT end in _date / _at / _owner (or be those bare tokens)
      - cite_kind ∈ {internal_document, url, external_system}
      - verification_days is an int in [30, 3650]
      - fingerprint has 1-3 tokens
    """
    errs: list[str] = []
    for i, col in enumerate(pass_block.get("cite_columns") or []):
        label = f"pass[{pname}].cite_columns[{i}]"
        fp = col.get("fingerprint") or []
        bt = col.get("binds_to") or ""
        ck = col.get("cite_kind", "internal_document")
        vd = col.get("verification_days", 365)

        if _cite_bind_disallowed(bt):
            errs.append(
                f"{label}: binds_to={bt!r} — cite must NOT bind to a "
                f"MUST ending in _date/_at/_owner (dates + owner-names are "
                f"data-shape, not cite-shape). See docs/curation/"
                f"cite_columns_criterion.md § anti-pattern binds."
            )
        if ck not in _VALID_CITE_KINDS:
            errs.append(
                f"{label}: cite_kind={ck!r} not in {sorted(_VALID_CITE_KINDS)}"
            )
        if not isinstance(vd, int) or vd < 30 or vd > 3650:
            errs.append(
                f"{label}: verification_days={vd!r} must be int in [30, 3650]"
            )
        if not (1 <= len(fp) <= 3):
            errs.append(
                f"{label}: fingerprint={fp!r} must be 1-3 tokens "
                f"(subset match fails on longer)"
            )
    return errs


def _validate_file(path: Path, reqs, items_by_req) -> list[str]:
    """Return a list of error strings (empty if file is clean)."""
    errs: list[str] = []
    try:
        with path.open() as f:
            doc = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(doc, dict):
        return ["top-level YAML is not a mapping"]

    passes = doc.get("passes") or []
    if not passes:
        errs.append("no passes declared")
        return errs

    for i, p in enumerate(passes):
        pname = p.get("pass_name", f"#{i}")
        target_req = p.get("target_evidence_requirement")
        target_ctrl = p.get("target_control")

        if not target_req:
            errs.append(f"pass[{pname}]: missing target_evidence_requirement")
            continue
        if target_req not in reqs:
            errs.append(
                f"pass[{pname}]: target_evidence_requirement {target_req!r} not in ALL_EVIDENCE_REQUIREMENTS "
                f"or any DerivedSpec.direct_evidence"
            )
            continue

        req_ctrl = reqs[target_req].control_ref
        if target_ctrl and target_ctrl != req_ctrl:
            errs.append(
                f"pass[{pname}]: target_control={target_ctrl!r} but "
                f"{target_req}.control_ref={req_ctrl!r}"
            )

        allowed_items = items_by_req[target_req]
        for bt, src in _iter_binds(p):
            if bt not in allowed_items:
                errs.append(
                    f"pass[{pname}].{src}: binds_to={bt!r} is not a ChecklistItem "
                    f"on {target_req} (allowed: {sorted(allowed_items) or '<none>'})"
                )

        # Ship 91'.i — cite_columns discipline check (per-pass).
        errs.extend(_validate_cite_discipline(p, pname))

    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "paths",
        nargs="*",
        help="YAML files to validate (default: every db/workbook_mappings/*.yaml)",
    )
    args = ap.parse_args()

    if args.paths:
        files = [Path(p) for p in args.paths]
    else:
        files = sorted((_ROOT / "db" / "workbook_mappings").glob("*.yaml"))

    if not files:
        print("no YAML files to validate", file=sys.stderr)
        return 2

    reqs, items_by_req = _build_id_index()
    print(f"loaded {len(reqs)} curated requirements ({sum(len(v) for v in items_by_req.values())} items)")

    def _label(p: Path) -> str:
        try:
            return str(p.relative_to(_ROOT))
        except ValueError:
            return str(p)

    total_errs = 0
    for path in files:
        errs = _validate_file(path, reqs, items_by_req)
        if errs:
            total_errs += len(errs)
            print(f"FAIL {_label(path)}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK   {_label(path)}")

    if total_errs:
        print(f"\n{total_errs} error(s) across {len(files)} file(s)")
        return 1
    print(f"\nall {len(files)} file(s) clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
