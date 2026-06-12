"""Stage I — Workbook discovery engine.

Loads canonical YAML mappings from `db/workbook_mappings/`, fingerprints
each sheet in a tenant workbook, and emits proposals. No DB writes; pure
in-memory. Stage II / Stage III consume the proposals.

Engine semantics (locked — see db/workbook_mappings/README.md):
  - Tokenizer: lowercase, split on whitespace/_-/, strip non-alnum, drop
    stopwords, light trailing-s/-ed/-ing stem.
  - Subset match: fingerprint tokens must all appear in target tokens.
  - `coverage: partial` is engine-conservative (MUST counted UNSATISFIED).
  - Multiple required_columns / column_groups binding to same MUST → ANY-of,
    full wins over partial.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

from rag.intake.value_patterns import check_anchor as _check_anchor


# Anchor confidence band: only sheets in this confidence range get
# sample-row anchor checks. Above HIGH_THRESHOLD the fingerprint match
# is already strong; below DROP_THRESHOLD the sheet is filtered before
# anchors would have time to fire. The band is the "ambiguous"
# zone where data-shape disambiguation pays off.
_ANCHOR_BAND_LO   = 0.30
_ANCHOR_BAND_HI   = 0.70
_DROP_THRESHOLD   = 0.30   # post-anchor floor — below this, proposal dropped


# ─────────────────────────────────────────────────────────────────────────────
# Tokenizer
# ─────────────────────────────────────────────────────────────────────────────

_STOPWORDS = frozenset({
    "a", "an", "the",
    "of", "by", "in", "to", "for", "on", "at", "with", "from", "into",
    "and", "or",
    "is", "are", "be",
})

# Trailing-token stem rules. Order matters: longer suffix first.
_STEM_SUFFIXES = ("ies", "ing", "ed", "es", "s")

# Words we don't stem even when they match a suffix (preserves meaning).
_STEM_KEEP = frozenset({
    "access", "address", "assess", "business", "process", "status",
    "class", "loss", "miss", "less", "pass",
    "data", "media",       # plural-looking but treated as singular here
    "ids",                 # don't stem to "id" (we want either to match either)
})

# Doc-shape synonym canonicalisation. A tenant uploading "Access Management
# Process.docx" should match A.5.18's "Access Rights Management Procedure"
# leaf — process and procedure are the same kind of artefact. Mapping
# common doc-shape synonyms to a canonical token at tokenize time lets
# both filename inputs and YAML fingerprints normalise to the same word
# before subset-matching.
#
# Scope: only the shape WORDS (policy / procedure / plan / etc.). Topic
# words (access / supplier / cloud) stay as-is. Adding a new pair here
# must be carefully chosen — the synonym is bidirectional in effect, so
# any leaf TITLE containing the canonical word will match an upload using
# the synonym (and vice versa).
_SHAPE_SYNONYMS = {
    # → procedure
    "process":         "procedure",
    "workflow":        "procedure",
    "wi":              "procedure",   # work instruction
    "sop":             "procedure",   # standard operating procedure
    # → policy
    "standard":        "policy",
    "directive":       "policy",
    "rule":            "policy",
    # → plan
    "programme":       "plan",
    "program":         "plan",
    "roadmap":         "plan",
    # → assessment (doc-shape only; do NOT map "review" — it's also a
    # topic word in many leaf titles e.g. "Compliance Review Schedule")
    "report":          "assessment",
    "evaluation":      "assessment",
    # → register
    "log":             "register",
    "list":            "register",
    "inventory":       "register",
    "tracker":         "register",
    "record":          "register",
}


def _stem(token: str) -> str:
    # Order matters: synonym applies AFTER stemming so plurals reach the
    # table (e.g. "standards" → "standard" → "policy"). For tokens that
    # skip stemming (≤3 chars or _STEM_KEEP-listed), still consult the
    # synonym map — without this, "process" (in _STEM_KEEP to block the
    # -s strip) never gets mapped to "procedure", and "sop"/"wi" don't
    # map either.
    if len(token) <= 3:
        return _SHAPE_SYNONYMS.get(token, token)
    if token in _STEM_KEEP:
        return _SHAPE_SYNONYMS.get(token, token)
    for suf in _STEM_SUFFIXES:
        if token.endswith(suf) and len(token) - len(suf) >= 3:
            stem = token[: -len(suf)]
            if suf == "ies":
                stem += "y"
            return _SHAPE_SYNONYMS.get(stem, stem)
    return _SHAPE_SYNONYMS.get(token, token)


_SPLIT_RE = re.compile(r"[\s_/\-&+,]+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Split text into normalised tokens. Stable for fingerprint matching."""
    if not text:
        return []
    out: list[str] = []
    for raw in _SPLIT_RE.split(text.lower()):
        cleaned = _NON_ALNUM_RE.sub("", raw)
        if not cleaned or cleaned in _STOPWORDS:
            continue
        out.append(_stem(cleaned))
    return out


def _normalise_fingerprint(fp: Iterable[str]) -> list[str]:
    """Apply the same normalisation pipeline to a YAML fingerprint."""
    return [_stem(tok.lower()) for tok in fp if tok and tok.lower() not in _STOPWORDS]


def subset_match(fingerprint: Iterable[str], haystack_tokens: Iterable[str]) -> bool:
    """True when every fingerprint token appears in the haystack tokens."""
    norm_fp = _normalise_fingerprint(fingerprint)
    if not norm_fp:
        return False
    bag = set(haystack_tokens)
    return all(tok in bag for tok in norm_fp)


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# ─────────────────────────────────────────────────────────────────────────────
# YAML loading
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_MAPPINGS_DIR = Path(__file__).resolve().parents[2] / "db" / "workbook_mappings"


def load_mappings(mappings_dir: Path | None = None) -> list[dict]:
    """Load every *.yaml mapping in the directory (sorted, deterministic)."""
    base = mappings_dir or DEFAULT_MAPPINGS_DIR
    out: list[dict] = []
    for path in sorted(base.glob("*.yaml")):
        with path.open() as f:
            doc = yaml.safe_load(f)
        if isinstance(doc, dict):
            doc["__path"] = str(path)
            out.append(doc)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Column matching
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class _ColumnHit:
    """A header cell that matched a fingerprint."""
    header: str                   # raw header text from the sheet
    col_idx: int                  # 1-based
    binds_to: str | None          # MUST id (None for trigger/freshness lookups)
    coverage: str = "full"        # "full" | "partial"


def _find_column(
    fingerprint: list[str],
    alternative_fingerprints: list[list[str]] | None,
    header_tokens: list[list[str]],
    headers: list[str],
) -> tuple[int, str] | None:
    """Return (col_idx 1-based, raw header) for the first matching column.

    Tries the primary fingerprint first, then each alternative in order.
    """
    candidates = [fingerprint] + list(alternative_fingerprints or [])
    for fp in candidates:
        for i, toks in enumerate(header_tokens):
            if subset_match(fp, toks):
                return i + 1, headers[i]
    return None


def _scan_columns(
    pass_block: dict,
    headers: list[str],
    header_tokens: list[list[str]],
) -> dict[str, list[_ColumnHit]]:
    """Return MUST-id → list of column hits (full or partial) for the pass."""
    by_must: dict[str, list[_ColumnHit]] = {}

    def _record(col_spec: dict) -> None:
        bt = col_spec.get("binds_to")
        if not bt:
            return
        hit = _find_column(
            col_spec.get("fingerprint") or [],
            col_spec.get("alternative_fingerprints"),
            header_tokens,
            headers,
        )
        if hit is None:
            return
        col_idx, header = hit
        coverage = col_spec.get("coverage", "full")
        by_must.setdefault(bt, []).append(
            _ColumnHit(header=header, col_idx=col_idx, binds_to=bt, coverage=coverage)
        )

    for col in pass_block.get("required_columns") or []:
        _record(col)
    for col in pass_block.get("optional_columns") or []:
        _record(col)

    for grp in pass_block.get("column_groups") or []:
        bt = grp.get("binds_to")
        if not bt:
            continue
        requires = grp.get("requires", "any")
        group_coverage = grp.get("coverage", "full")
        cols = grp.get("columns") or []
        group_hits: list[_ColumnHit] = []
        for col_spec in cols:
            hit = _find_column(
                col_spec.get("fingerprint") or [],
                col_spec.get("alternative_fingerprints"),
                header_tokens,
                headers,
            )
            if hit is None:
                continue
            col_idx, header = hit
            col_coverage = col_spec.get("coverage", group_coverage)
            group_hits.append(
                _ColumnHit(header=header, col_idx=col_idx, binds_to=bt, coverage=col_coverage)
            )

        if requires == "all":
            satisfied = len(group_hits) == len(cols) and len(cols) > 0
        else:  # "any"
            satisfied = len(group_hits) >= 1

        if not satisfied:
            continue

        # If any contributing column (or group) is partial, the group resolves
        # partial. Conservative rule: any partial → group partial.
        any_partial = group_coverage == "partial" or any(h.coverage == "partial" for h in group_hits)
        effective_coverage = "partial" if any_partial else "full"
        composite_header = " + ".join(h.header for h in group_hits)
        composite_idx = min(h.col_idx for h in group_hits)
        by_must.setdefault(bt, []).append(
            _ColumnHit(
                header=f"[group {grp.get('group_name','?')}: {composite_header}]",
                col_idx=composite_idx,
                binds_to=bt,
                coverage=effective_coverage,
            )
        )

    return by_must


# ─────────────────────────────────────────────────────────────────────────────
# Header row detection
# ─────────────────────────────────────────────────────────────────────────────


def _required_must_ids(pass_block: dict) -> list[str]:
    """MUST ids that appear under required_columns or under requires:all groups."""
    out: list[str] = []
    for col in pass_block.get("required_columns") or []:
        bt = col.get("binds_to")
        if bt and bt not in out:
            out.append(bt)
    for grp in pass_block.get("column_groups") or []:
        if grp.get("requires") == "all":
            bt = grp.get("binds_to")
            if bt and bt not in out:
                out.append(bt)
    return out


def _all_declared_must_ids(pass_block: dict) -> list[str]:
    """Every MUST id this pass attempts to bind (required + optional + groups)."""
    out: list[str] = []
    for col in pass_block.get("required_columns") or []:
        bt = col.get("binds_to")
        if bt and bt not in out:
            out.append(bt)
    for col in pass_block.get("optional_columns") or []:
        bt = col.get("binds_to")
        if bt and bt not in out:
            out.append(bt)
    for grp in pass_block.get("column_groups") or []:
        bt = grp.get("binds_to")
        if bt and bt not in out:
            out.append(bt)
    return out


def _pick_header_row(
    rows: list[list[str]],
    hints: list[int],
    pass_blocks: list[dict],
) -> tuple[int, list[str]] | None:
    """Try each hint; pick the row that subset-matches the most required cols.

    Ties broken by lowest row index. Returns (1-based row index, headers).
    """
    if not rows:
        return None

    # Collect every required-column fingerprint across all passes for scoring.
    required_fps: list[list[str]] = []
    for p in pass_blocks:
        for col in p.get("required_columns") or []:
            fp = col.get("fingerprint")
            if fp:
                required_fps.append(fp)
        for grp in p.get("column_groups") or []:
            if grp.get("requires") == "all":
                for col in grp.get("columns") or []:
                    fp = col.get("fingerprint")
                    if fp:
                        required_fps.append(fp)

    if not required_fps:
        # No required columns to score against; trust the first hint.
        idx = max(1, hints[0]) if hints else 1
        if idx > len(rows):
            return None
        return idx, [str(c or "").strip() for c in rows[idx - 1]]

    best_idx = -1
    best_score = -1
    for hint in hints or [1]:
        if hint < 1 or hint > len(rows):
            continue
        headers = [str(c or "").strip() for c in rows[hint - 1]]
        toks = [tokenize(h) for h in headers]
        score = sum(
            1 for fp in required_fps if any(subset_match(fp, t) for t in toks)
        )
        if score > best_score:
            best_score = score
            best_idx = hint
    if best_idx < 0:
        return None
    headers = [str(c or "").strip() for c in rows[best_idx - 1]]
    return best_idx, headers


# ─────────────────────────────────────────────────────────────────────────────
# Sheet → mapping fingerprint
# ─────────────────────────────────────────────────────────────────────────────


def _best_sheet_name_score(sheet_name: str, mapping: dict) -> float:
    """Max jaccard over all sheet_name_fingerprints. 0.0 if no fingerprint matches."""
    sheet_tokens = tokenize(sheet_name)
    if not sheet_tokens:
        return 0.0
    best = 0.0
    for fp in mapping.get("sheet_name_fingerprints") or []:
        toks = _normalise_fingerprint(fp.get("tokens") or [])
        if not toks:
            continue
        if not subset_match(toks, sheet_tokens):
            continue
        score = _jaccard(toks, sheet_tokens)
        if score > best:
            best = score
    return best


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PassProposal:
    pass_name: str
    target_control: str
    target_evidence_requirement: str
    target_evidence_type: str
    satisfied: list[str] = field(default_factory=list)
    partial: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    matched_columns: dict[str, str] = field(default_factory=dict)  # MUST id → matched header
    warnings: list[str] = field(default_factory=list)
    freshness_column: str | None = None
    freshness_days: int | None = None


@dataclass
class SheetProposal:
    sheet: str
    mapping_id: str
    mapping_path: str
    confidence: float
    header_row: int | None
    headers: list[str]
    row_count: int
    passes: list[PassProposal] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    # Per-anchor telemetry from sample-row inspection. Empty list when
    # the proposal didn't enter the anchor band or the YAML declared
    # no anchors. Each entry: {anchor, pattern, header, ratio, passed,
    # delta, decision}. See _apply_sample_value_anchors.
    anchor_decisions: list[dict] = field(default_factory=list)


def evaluate_pass(
    pass_block: dict,
    headers: list[str],
) -> PassProposal:
    """Run a single pass against the detected header row, return proposal."""
    header_tokens = [tokenize(h) for h in headers]
    hits_by_must = _scan_columns(pass_block, headers, header_tokens)

    declared = _all_declared_must_ids(pass_block)

    prop = PassProposal(
        pass_name=pass_block.get("pass_name", "?"),
        target_control=pass_block.get("target_control", "?"),
        target_evidence_requirement=pass_block.get("target_evidence_requirement", "?"),
        target_evidence_type=pass_block.get("target_evidence_type", "?"),
    )

    for must_id in declared:
        hits = hits_by_must.get(must_id) or []
        if not hits:
            prop.missing.append(must_id)
            continue
        # full wins over partial across all binding sources
        full_hits = [h for h in hits if h.coverage == "full"]
        chosen = full_hits[0] if full_hits else hits[0]
        prop.matched_columns[must_id] = chosen.header
        if chosen.coverage == "full":
            prop.satisfied.append(must_id)
        else:
            prop.partial.append(must_id)

    # Freshness: locate the freshness column if declared (warning if missing).
    freshness = pass_block.get("freshness")
    if freshness:
        prop.freshness_days = freshness.get("days")
        hit = _find_column(
            freshness.get("column_fingerprint") or [],
            freshness.get("alternative_fingerprints"),
            header_tokens,
            headers,
        )
        if hit is None:
            prop.warnings.append(
                f"freshness check skipped: no column matched {freshness.get('column_fingerprint')}"
            )
        else:
            prop.freshness_column = hit[1]

    # Trigger columns: if any are declared, at least one must be present.
    trig = pass_block.get("trigger_columns") or []
    if trig:
        found_any = False
        for col in trig:
            if _find_column(col.get("fingerprint") or [], None, header_tokens, headers):
                found_any = True
                break
        if not found_any:
            prop.warnings.append(
                "no trigger_columns matched — pass will not extract rows"
            )

    return prop


def _apply_sample_value_anchors(
    pass_block:  dict,
    headers:     list[str],
    header_tokens: list[list[str]],
    data_rows:   list[list[str]],
) -> tuple[float, list[dict]]:
    """Apply per-pass sample_value_anchors to verify column data shape.

    Returns (confidence_delta, anchor_decisions). Pure side-effect-free.
    The caller folds delta into the overall sheet confidence.

    Each anchor specifies a `column_fingerprint` (with optional
    `alternative_fingerprints`) — the helper locates the matching
    column directly via `_find_column`, so anchors work even when
    multiple bindings share the same MUST id.

    `anchor_decisions` is a list of telemetry records describing each
    anchor that fired:
      {fingerprint, pattern, header, ratio, passed, delta, decision}.
    """
    anchors = (pass_block or {}).get("sample_value_anchors") or []
    if not anchors or not headers or not data_rows:
        return (0.0, [])

    # First N data rows for sampling. 5 is enough — first rows tend to
    # be representative, and we want to stay cheap.
    SAMPLE_N = 5
    sample_rows = data_rows[:SAMPLE_N]

    delta = 0.0
    decisions: list[dict] = []

    for anchor in anchors:
        fp       = anchor.get("column_fingerprint")
        pat_name = anchor.get("value_pattern")
        if not fp or not pat_name:
            continue
        hit = _find_column(
            fp,
            anchor.get("alternative_fingerprints"),
            header_tokens,
            headers,
        )
        if hit is None:
            # No matching column in this sheet — anchor can't fire.
            continue
        col_idx, header = hit
        sample_values = [r[col_idx] if col_idx < len(r) else "" for r in sample_rows]

        min_ratio = float(anchor.get("min_match_ratio", 0.7))
        passed, ratio = _check_anchor(sample_values, pat_name, min_ratio)

        if passed:
            boost = float(anchor.get("confidence_boost", 0.0))
            decision = "boost"
        else:
            boost = float(anchor.get("confidence_penalty", 0.0))
            decision = "penalty"
        delta += boost

        decisions.append({
            "fingerprint": fp,
            "pattern":     pat_name,
            "header":      header,
            "ratio":       round(ratio, 3),
            "passed":      passed,
            "delta":       boost,
            "decision":    decision,
        })

    return (delta, decisions)


def discover_sheet(
    sheet_name: str,
    rows: list[list[Any]],
    mappings: list[dict],
    *,
    confidence_floor: float = 0.0,
) -> list[SheetProposal]:
    """Match a sheet against every mapping; return proposals above the floor.

    Most sheets will match 0 or 1 mappings; the loop allows hybrid sheets
    (e.g. a workbook author later adds a second YAML matching the same shape).
    """
    proposals: list[SheetProposal] = []
    for mapping in mappings:
        sheet_score = _best_sheet_name_score(sheet_name, mapping)
        if sheet_score <= 0.0:
            continue

        weights = mapping.get("confidence_weights") or {}
        w_sheet = float(weights.get("sheet_name", 0.5))
        w_cols = float(weights.get("required_columns", 0.4))
        w_rows = float(weights.get("row_count", 0.1))

        hints = mapping.get("header_row_hints") or [1]
        passes_yaml = mapping.get("passes") or []

        # Stringify the workbook rows once for header detection + scanning.
        str_rows = [[str(c or "").strip() for c in r] for r in rows]

        sheet_warnings: list[str] = []
        header_pick = _pick_header_row(str_rows, hints, passes_yaml)
        if header_pick is None:
            sheet_warnings.append("could not detect header row from header_row_hints")
            headers: list[str] = []
            header_row: int | None = None
        else:
            header_row, headers = header_pick

        # Data rows = everything after the header row.
        data_rows = str_rows[header_row:] if header_row else []
        # Strip fully-empty rows.
        data_rows = [r for r in data_rows if any(c for c in r)]
        row_count = len(data_rows)

        min_rows = mapping.get("min_data_rows", 1)
        rows_ok = 1.0 if row_count >= min_rows else 0.0
        if not rows_ok:
            sheet_warnings.append(
                f"row count {row_count} below min_data_rows {min_rows}"
            )

        # Required-column coverage for confidence (presence-based, not quality).
        required_must_ids = _required_must_ids(passes_yaml[0]) if passes_yaml else []
        # Use first pass for sheet-level confidence — passes share the same
        # header row so this is representative.
        if headers and passes_yaml:
            hits_by_must = _scan_columns(passes_yaml[0], headers, [tokenize(h) for h in headers])
            present = sum(1 for m in required_must_ids if hits_by_must.get(m))
            col_score = present / len(required_must_ids) if required_must_ids else 1.0
        else:
            col_score = 0.0

        confidence = (w_sheet * sheet_score) + (w_cols * col_score) + (w_rows * rows_ok)
        if confidence < confidence_floor:
            continue

        pass_props = [evaluate_pass(p, headers) for p in passes_yaml] if headers else []

        # Sample-row anchor confirmation: only fire in the ambiguous
        # band where fingerprint match alone could be a false positive.
        # Above _ANCHOR_BAND_HI the match is already strong; below
        # _ANCHOR_BAND_LO we'd drop the proposal anyway. See
        # [[feedback-intake-label-unreliability]] for the broader
        # design framing.
        anchor_decisions_all: list[dict] = []
        if _ANCHOR_BAND_LO <= confidence <= _ANCHOR_BAND_HI:
            header_tokens = [tokenize(h) for h in headers] if headers else []
            for pass_idx in range(len(passes_yaml)):
                delta, decisions = _apply_sample_value_anchors(
                    passes_yaml[pass_idx], headers, header_tokens, data_rows,
                )
                if decisions:
                    anchor_decisions_all.extend(decisions)
                confidence += delta
            confidence = max(0.0, min(1.0, confidence))

        # Drop-threshold gate: after anchors have had their say, if
        # we're below _DROP_THRESHOLD the proposal is too uncertain
        # to be useful; filter it before it lands in the orphan list.
        if confidence < _DROP_THRESHOLD:
            sheet_warnings.append(
                f"proposal dropped: post-anchor confidence {round(confidence, 3)} "
                f"< drop threshold {_DROP_THRESHOLD}"
            )
            continue

        proposals.append(SheetProposal(
            sheet=sheet_name,
            mapping_id=mapping.get("mapping_id", "?"),
            mapping_path=mapping.get("__path", "?"),
            confidence=round(confidence, 3),
            header_row=header_row,
            headers=headers,
            row_count=row_count,
            passes=pass_props,
            warnings=sheet_warnings,
            anchor_decisions=anchor_decisions_all,
        ))

    return proposals


def discover_workbook(
    workbook_rows: dict[str, list[list[Any]]],
    *,
    mappings_dir: Path | None = None,
    confidence_floor: float = 0.0,
) -> list[SheetProposal]:
    """Discover all sheets in a workbook. Caller is responsible for loading rows.

    `workbook_rows` is sheet_name → list of rows (each row a list of cell values).
    """
    mappings = load_mappings(mappings_dir)
    all_proposals: list[SheetProposal] = []
    for sheet_name, rows in workbook_rows.items():
        all_proposals.extend(discover_sheet(sheet_name, rows, mappings, confidence_floor=confidence_floor))
    return all_proposals
