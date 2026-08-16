"""
Ship 74'.b — intake tracer allowlist regression guard.

Ship 74'.a closed this bug: `IntakeTracer.write()` filters its **kwargs
through an explicit `allowed` set. A kwarg NOT in that set is silently
dropped from the persisted trace row — even though the kwarg was passed
explicitly at a call site and the underlying DB column exists.

Ship 72'.a introduced 6 metric kwargs; none were in the allowlist. Silent-
drop went unnoticed until the Ship 73' dogfood proved the columns were
always NULL — despite the retro claiming they persisted "automatically."

This test asserts symmetry between the tracer's allowlist and every
`tracer.write(...)` call site. If a call site passes a kwarg the
allowlist doesn't recognise, the test fails fast at CI time with the
name of the dropped kwarg, before it reaches production.

Guard shape is static (AST-based, no DB, no runtime). Fast to run.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TARGET = _REPO_ROOT / "rag" / "intake" / "doc_pipeline.py"

# Framework kwargs that are declared explicitly in the tracer.write
# signature (not merged via **metrics) — they always land regardless of
# the allowlist and must not be treated as candidates for it.
_FRAMEWORK_KWARGS = {"status", "error_type", "error_detail"}


def _load_allowed_set(src: str) -> set[str]:
    """Extract the `allowed = {...}` set literal inside IntakeTracer.write.

    We parse the module AST and find the specific Assign node whose target
    name is `allowed` and whose value is a Set literal. Returns the set of
    string constants.
    """
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if not (isinstance(tgt, ast.Name) and tgt.id == "allowed"):
            continue
        if not isinstance(node.value, ast.Set):
            continue
        names: set[str] = set()
        for elt in node.value.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                names.add(elt.value)
        if names:
            return names
    raise AssertionError(
        "Could not locate `allowed = {...}` string-set literal inside "
        f"{_TARGET}. Did the tracer's filter shape change? Update this "
        "test to match."
    )


def _collect_tracer_write_kwargs(src: str) -> dict[str, set[str]]:
    """Return {call_context: set_of_kwarg_names} for every `tracer.write(...)`
    call in the file.

    call_context is a "stage:line" string so failures point back at the
    exact site. kwarg names are the ones passed to `write()`; positional
    args (stage, stage_ms) are ignored.
    """
    tree = ast.parse(src)
    out: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        # Match `tracer.write(...)` — attribute access on Name "tracer".
        f = node.func
        if not (isinstance(f, ast.Attribute) and f.attr == "write"):
            continue
        if not (isinstance(f.value, ast.Name) and f.value.id == "tracer"):
            continue
        # Best-effort: first positional arg is the stage name (Constant str).
        stage = "<unknown>"
        if node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str):
            stage = node.args[0].value
        key = f"{stage}:L{node.lineno}"
        out[key] = {kw.arg for kw in node.keywords if kw.arg is not None}
    if not out:
        raise AssertionError(
            f"No `tracer.write(...)` call sites found in {_TARGET}. "
            "Did the pipeline restructure? Update this test."
        )
    return out


def test_tracer_write_kwargs_are_all_allowlisted():
    """Every kwarg passed to `tracer.write()` in doc_pipeline.py must be in
    `IntakeTracer.write.allowed` (or a framework kwarg like `status`).

    Fails with a targeted message naming the dropped kwarg + call site so
    the fix is unambiguous: add the name to the `allowed` set.
    """
    src = _TARGET.read_text()
    allowed = _load_allowed_set(src)
    call_sites = _collect_tracer_write_kwargs(src)

    failures: list[str] = []
    for site, kwargs in call_sites.items():
        for kw in kwargs:
            if kw in _FRAMEWORK_KWARGS or kw in allowed:
                continue
            failures.append(
                f"tracer.write @ {site}: kwarg `{kw}` is not in the "
                f"allowlist and will be silently dropped. Add it to "
                f"the `allowed` set in IntakeTracer.write (Ship 74'.a "
                f"regression class)."
            )

    assert not failures, (
        "Intake tracer silent-drop regression detected:\n  - "
        + "\n  - ".join(sorted(failures))
    )


def test_allowlist_shape_sanity():
    """Sanity: the parsed allowlist must contain a known-persisted column
    (schema_v98's `contract_skip_empty_text`), proving the AST parse
    landed on the right node. Prevents a silent test-side false negative
    where the parser returns an empty set and every call site trivially
    passes.
    """
    src = _TARGET.read_text()
    allowed = _load_allowed_set(src)
    assert "contract_skip_empty_text" in allowed, (
        "Ship 74'.a landmark (`contract_skip_empty_text`) missing from "
        "parsed allowlist — the AST parse is probably reading the wrong "
        "assign node. Update _load_allowed_set."
    )
    # Also expect a schema_v35 landmark to be there — proves we haven't
    # accidentally locked onto a nested scope.
    assert "dropped_low_conf" in allowed, (
        "schema_v35 landmark `dropped_low_conf` missing — same failure "
        "mode as above."
    )


if __name__ == "__main__":
    test_allowlist_shape_sanity()
    test_tracer_write_kwargs_are_all_allowlisted()
    print("OK — intake tracer allowlist symmetry holds")
