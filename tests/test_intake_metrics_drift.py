"""
Ship 74'.c — extraction_metrics producer-drift guard.

Companion to Ship 74'.b (tests/test_intake_tracer_allowlist.py). Together
they close the class of silent-drop bug that Ship 74'.a fixed. Ship 74'.a
had failed at BOTH layers simultaneously:

  Layer 1 (upstream)  : new counter set on `doc.extraction_metrics`
                        but never forwarded to any `tracer.write(...)`
                        call. Ship 74'.c catches this.

  Layer 2 (at tracer) : counter forwarded as kwarg but not in the
                        allowlist. Ship 74'.b catches this.

Guard shape (Ship 74'.c):
  1. AST-collect every `doc.extraction_metrics[K] = ...` (or `.setdefault(K, ...)`)
     assignment across `rag/intake/*.py`.
  2. AST-collect every kwarg passed to any `tracer.write(...)` call.
  3. Assert every producer key is either forwarded OR in the explicit
     `_INTENTIONAL_DEBUG_ONLY` set below.

Adding a new counter requires an explicit choice:
  - forward it to the tracer (add kwarg + allowlist entry + schema column), OR
  - add it to `_INTENTIONAL_DEBUG_ONLY` with a one-line rationale.

Both actions are deliberate. Silent-drop stops being an option.
"""
from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_INTAKE_DIR = _REPO_ROOT / "rag" / "intake"


# Producer keys that are set on `doc.extraction_metrics` but not
# forwarded to `intake_trace_log`. Each name must have a justification.
#
# Two categories:
#
#   (A) Genuinely inline / debug-only — the key exists for a downstream
#       code path to read within the SAME pipeline run. Persisting adds
#       no auditor value. Nested-dict / list payloads live here too:
#       intake_trace_log columns are scalars, not JSONB.
#
#   (B) Not-yet-persisted — arguable observability value if forwarded,
#       but no schema column exists today. Grandfathered here to catch
#       future drift; promote to forwarded in a dedicated arc when the
#       schema and downstream consumers are ready.
_INTENTIONAL_DEBUG_ONLY: set[str] = {
    # ─── (A) Genuinely inline / debug-only ─────────────────────────
    # Nested dict — the _arion_meta hidden sheet payload.
    "templated_xlsx_meta",
    # List — targeted leaf ids, consumed inline by pass-2 planner.
    "target_leaves",
    # Nested dict — structural evidence snapshot for downstream
    # posture writer. Feature payload, not a metric.
    "structural_evidence",
    # Inline scope-method / retrieval sizing signals; feed decisions in
    # the same call chain and are already captured in `candidate_controls`
    # / `primary_candidate_controls` scalars.
    "scope_method", "retrieval_scoped_count",
    "must_prefilter", "musts_before_prefilter", "musts_after_prefilter",
    "leaf_musts_count", "leaf_musts_source",
    "llm_leaves_after_fp_coverage",
    "leaves_narrowed_by_musts",
    "leaf_classifier",

    # ─── (B) Not-yet-persisted (future forwarding arc) ─────────────
    # Templated table-zone counters (Ship 72'.a). Narrow observability
    # value — only fires on tabular templated docs, and the leaf-level
    # yield story is already told by `templated_findings` /
    # `templated_edit_zones_bound` (both promoted Ship 74'.d).
    "templated_table_zones_total", "templated_table_zones_bound",
    "templated_table_zones_empty", "templated_tabular_rows_captured",
    "templated_table_cols_mangled",
    # Templated xlsx per-leaf detail. Deep debugging surface for xlsx
    # round-trip authoring; deferred until someone is actively tuning
    # xlsx templates and needs the per-leaf breakdown persisted.
    "templated_xlsx_leaf_id", "templated_xlsx_source",
    "templated_xlsx_columns", "templated_xlsx_columns_bound",
    "templated_xlsx_register_rows",
    "templated_xlsx_doc_fields", "templated_xlsx_doc_fields_bound",
    # Ship 74'.d promoted 18 category-B keys to persisted columns
    # (schema_v100): critic telemetry (7) + filter drops (2) +
    # fingerprint yield (2) + classifier gate (3) + templated yield (4).
    # They now live as tracer.write kwargs + allowlist entries.
    #
    # Ship 78'.b union-extractor telemetry — grandfathered here
    # temporarily; promote in Ship 78'.d schema migration alongside
    # eval + dogfood work. Union metrics are the canonical Ship 78'
    # observability surface (how much did each path contribute? how
    # many findings deduped?), so they should be persisted.
    "union_from_consensus", "union_from_critic", "union_deduped_count",
}


def _collect_producer_keys() -> dict[str, list[str]]:
    """Return {key: [file:line, ...]} for every producer site."""
    out: dict[str, list[str]] = {}
    for f in sorted(_INTAKE_DIR.glob("*.py")):
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            # `doc.extraction_metrics[K] = ...`
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if not isinstance(tgt, ast.Subscript):
                        continue
                    v = tgt.value
                    if (isinstance(v, ast.Attribute)
                            and v.attr == "extraction_metrics"
                            and isinstance(tgt.slice, ast.Constant)
                            and isinstance(tgt.slice.value, str)):
                        out.setdefault(tgt.slice.value, []).append(
                            f"{f.name}:L{node.lineno}"
                        )
            # `doc.extraction_metrics.setdefault(K, ...)`
            if isinstance(node, ast.Call):
                fn = node.func
                if (isinstance(fn, ast.Attribute) and fn.attr == "setdefault"
                        and isinstance(fn.value, ast.Attribute)
                        and fn.value.attr == "extraction_metrics"
                        and node.args
                        and isinstance(node.args[0], ast.Constant)
                        and isinstance(node.args[0].value, str)):
                    out.setdefault(node.args[0].value, []).append(
                        f"{f.name}:L{node.lineno}"
                    )
    return out


def _collect_forwarded_keys() -> set[str]:
    """Return set of every kwarg passed to any tracer.write() call."""
    out: set[str] = set()
    for f in sorted(_INTAKE_DIR.glob("*.py")):
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            if not (isinstance(fn, ast.Attribute) and fn.attr == "write"):
                continue
            if not (isinstance(fn.value, ast.Name) and fn.value.id == "tracer"):
                continue
            for kw in node.keywords:
                if kw.arg:
                    out.add(kw.arg)
    return out


def test_every_producer_key_is_forwarded_or_declared_debug_only():
    """A new key set on `doc.extraction_metrics` must be either forwarded
    to the tracer or added to `_INTENTIONAL_DEBUG_ONLY`. Prevents the
    Ship 74'.a class of silent-drop upstream of the tracer."""
    producers = _collect_producer_keys()
    forwarded = _collect_forwarded_keys()

    silent: list[str] = []
    for key, sites in producers.items():
        if key in forwarded or key in _INTENTIONAL_DEBUG_ONLY:
            continue
        first_site = sites[0] if sites else "(no site)"
        silent.append(
            f"`{key}` set on doc.extraction_metrics at {first_site} but "
            f"never forwarded to tracer.write and not in "
            f"_INTENTIONAL_DEBUG_ONLY. Either forward it (add kwarg to "
            f"the extract-stage tracer.write in doc_pipeline.py, add the "
            f"name to IntakeTracer.write's allowed set, add the column "
            f"in a schema migration) or add it to "
            f"_INTENTIONAL_DEBUG_ONLY with a rationale."
        )

    assert not silent, (
        "Producer-drift regression detected — extraction_metrics keys "
        "silently discarded upstream of the tracer:\n  - "
        + "\n  - ".join(sorted(silent))
    )


def test_debug_only_set_has_no_stale_entries():
    """A key in `_INTENTIONAL_DEBUG_ONLY` should still be a live producer
    key somewhere in `rag/intake/`. Prevents the set from accumulating
    dead entries when a producer is removed but the debug-only listing
    is forgotten.
    """
    producers = _collect_producer_keys()
    stale = sorted(_INTENTIONAL_DEBUG_ONLY - set(producers))
    assert not stale, (
        "`_INTENTIONAL_DEBUG_ONLY` contains keys that no code emits any "
        "more — clean up:\n  - " + "\n  - ".join(stale)
    )


def test_debug_only_set_does_not_overlap_forwarded():
    """A key can't be both forwarded and debug-only. Overlap indicates
    someone forwarded it but forgot to remove the debug-only entry.
    """
    forwarded = _collect_forwarded_keys()
    overlap = sorted(_INTENTIONAL_DEBUG_ONLY & forwarded)
    assert not overlap, (
        "`_INTENTIONAL_DEBUG_ONLY` overlaps with keys already forwarded "
        "to the tracer — pick one:\n  - " + "\n  - ".join(overlap)
    )


if __name__ == "__main__":
    test_debug_only_set_does_not_overlap_forwarded()
    test_debug_only_set_has_no_stale_entries()
    test_every_producer_key_is_forwarded_or_declared_debug_only()
    print("OK — extraction_metrics producer-drift guard holds")
