"""
Ship 31'.b — loader SELECT column guard.

Regression guard for the "loader blind to a semantic field" bug class
uncovered by Ship 30 + expanded in Ship 31:

  A loader function runs `SELECT c1, c2, ... FROM some_table` and
  returns records to downstream code that does `record.get("field")`
  as a load-bearing check. If SELECT omits the field but the schema
  has it, every record silently gets None and the check defaults to
  the wrong branch.

This test asserts the SELECT literal in a specific loader function
contains the semantic fields it's expected to fetch. It's a static
grep-shape check — it doesn't hit the database. Fails fast when a
future edit drops a required column from a loader SELECT.

If new semantic fields are added to `posture_controls` / `client_facts`
schema, extend the ASSERTIONS below.

See:
- [[ship-30-prime-arc-retrospective-2026-07-25]] — original bug class
- [[ship-31-prime-a-loader-audit-design-2026-07-25]] — expanded audit
"""
from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


# (source file, function name, table, columns that MUST appear in the
#  function's SELECT body)
#
# Each entry says: within the body of `function_name` in `source_file`,
# a SELECT ... FROM `table` must include every column in `columns`. The
# check is grep-shape (substring in the function body); it doesn't
# execute the query. That's enough to catch the specific regression
# class Ship 30/31 uncovered — a whitelist SELECT losing an entry.
_ASSERTIONS = [
    (
        "rag/posture_loader.py",
        "load_posture",
        "posture_controls",
        ["confirmation_status"],
    ),
    (
        "rag/posture_loader.py",
        "_fetch_not_assessed_obligation_rows",
        "posture_controls",
        ["confirmation_status"],
    ),
    (
        "rag/posture_loader.py",
        "load_client_facts",
        "client_facts",
        [
            # 8 fields Ship 31 discovered missing. Each is
            # referenced downstream in applies_when / cascade
            # engine / dataclass invariants — silent None
            # bypasses tenant-scope decisions.
            "uk_data_subjects",
            "role_joint_controller",
            "criminal_conviction_data",
            "automated_decision_making",
            "profiling",
            "systematic_monitoring",
            "employee_count_250_plus",
            "public_authority",
        ],
    ),
]


def _extract_function_source(path: Path, function_name: str) -> str:
    """Return the raw source of a top-level `def function_name(...)`
    block in `path`, stopping at the next top-level `def`/`class` or
    EOF. Naive line-oriented parser — good enough for our loader files
    where each loader is a top-level def with 0-indented header."""
    src = path.read_text().splitlines()
    start = None
    for i, line in enumerate(src):
        if re.match(rf"^def\s+{re.escape(function_name)}\s*\(", line):
            start = i
            break
    if start is None:
        raise AssertionError(
            f"Could not find `def {function_name}(...)` at top level of {path}"
        )
    end = len(src)
    for j in range(start + 1, len(src)):
        line = src[j]
        # Next top-level def/class ends this function
        if re.match(r"^(def|class)\s+\w+", line):
            end = j
            break
    return "\n".join(src[start:end])


def test_loader_selects_include_required_columns():
    """For each entry in _ASSERTIONS, verify the loader's function body
    contains the SELECT-required columns as substrings.

    Substring-match is intentional: the test is not a SQL parser, just
    a "this identifier must appear inside this function" check. Good
    enough to catch a dropped column from a whitelist SELECT.
    """
    failures = []
    for rel_path, func_name, table, required_cols in _ASSERTIONS:
        path = _REPO_ROOT / rel_path
        body = _extract_function_source(path, func_name)
        # Sanity: the function's SELECT must actually touch `table`
        if f"FROM {table}" not in body:
            failures.append(
                f"{rel_path}::{func_name} does not contain "
                f"`FROM {table}` — did the loader change shape?"
            )
            continue
        for col in required_cols:
            if col not in body:
                failures.append(
                    f"{rel_path}::{func_name} SELECT is missing "
                    f"`{col}` (required by downstream semantic checks; "
                    f"Ship 30/31 loader-blindness regression guard)"
                )

    assert not failures, (
        "Loader-blindness regression detected:\n  - "
        + "\n  - ".join(failures)
    )


if __name__ == "__main__":
    test_loader_selects_include_required_columns()
    print("OK — all loader SELECTs contain required columns")
