"""Stage I doc discovery: match an uploaded document to its canonical
shape via db/doc_mappings/*.yaml.

Doc-side analog of rag/intake/workbook_discovery.py. Same tokenizer,
same subset-match primitive — different signals. Where workbook
discovery fingerprints SHEET NAME + COLUMN HEADERS, doc discovery
fingerprints FILENAME + BODY first-N-tokens.

Output: list of DocProposal{mapping_id, confidence, target_leaves,
target_controls}. The extractor consumes this to scope its LLM call.

Soft fallback: when no mapping matches, the caller falls back to the
legacy DOC_TYPE_CLAUSE_MAP path in ref_normalizer — older docs and
mapping-less doc types continue to work.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from .workbook_discovery import tokenize, _normalise_fingerprint, subset_match

logger = logging.getLogger(__name__)


_DEFAULT_MAPPINGS_DIR = Path(__file__).resolve().parents[2] / "db" / "doc_mappings"
_BODY_TOKEN_SAMPLE_CHARS = 5000   # first N chars of body sampled for fingerprinting


@dataclass
class DocProposal:
    """One canonical-shape match for an uploaded document.

    target_controls is the union of target_leaves[].control_ref, deduped —
    the list the LLM extractor will scope its candidate set to.
    """
    mapping_id:        str
    mapping_path:      str
    confidence:        float
    filename_score:    float
    body_score:        float
    target_leaves:     list[dict] = field(default_factory=list)
    target_controls:   list[str]  = field(default_factory=list)
    cross_links:       list[str]  = field(default_factory=list)
    warnings:          list[str]  = field(default_factory=list)


def load_doc_mappings(mappings_dir: Optional[Path] = None) -> list[dict]:
    """Load every *.yaml under mappings_dir into memory.

    Each loaded mapping dict is augmented with `_path: <full path str>`
    so DocProposal can carry it through for traceability.
    """
    d = mappings_dir or _DEFAULT_MAPPINGS_DIR
    if not d.exists():
        return []
    out: list[dict] = []
    for f in sorted(d.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text()) or {}
        except Exception as e:
            logger.warning("doc_mapping %s failed to load: %s", f.name, e)
            continue
        data["_path"] = str(f)
        out.append(data)
    return out


def _best_fp_score(fingerprints: list[dict], target_tokens: list[str]) -> float:
    """OR-combined: return the BEST single-fingerprint match score
    against the target token bag. Each fingerprint is a token bag; a
    bag scores 1.0 when fully subset of target tokens, else 0.0. Same
    binary semantics as workbook fingerprint matching."""
    if not fingerprints:
        return 0.0
    target = set(target_tokens)
    best = 0.0
    for fp in fingerprints:
        fp_tokens = _normalise_fingerprint(fp.get("tokens") or [])
        if not fp_tokens:
            continue
        if all(t in target for t in fp_tokens):
            best = 1.0
            break
    return best


def discover_doc(
    filename:    str,
    body_text:   str,
    mappings:    Optional[list[dict]] = None,
    *,
    confidence_floor: float = 0.5,
) -> list[DocProposal]:
    """Match a doc against all canonical doc-shape mappings; return any
    proposals at or above confidence_floor.

    Scoring:
      - filename fingerprint match → weight defaulting to 0.6
      - body fingerprint match     → weight defaulting to 0.3
      - explicit_refs / min_body_chars → small adjustments (later)
    Per-mapping `confidence_weights` overrides the defaults.

    Multiple mappings can match a single doc (e.g. an "Information
    Security and Data Management Policy" may match the ISP + privacy
    mappings). All passing proposals are returned; the extractor unions
    their target_leaves.
    """
    if mappings is None:
        mappings = load_doc_mappings()
    if not mappings:
        return []

    filename_tokens = tokenize(Path(filename).stem)
    body_sample = (body_text or "")[:_BODY_TOKEN_SAMPLE_CHARS]
    body_tokens = tokenize(body_sample)

    proposals: list[DocProposal] = []
    for m in mappings:
        weights = m.get("confidence_weights") or {}
        w_filename = float(weights.get("filename", 0.6))
        w_body     = float(weights.get("body",     0.3))

        filename_score = _best_fp_score(m.get("filename_fingerprints") or [], filename_tokens)
        body_score     = _best_fp_score(m.get("body_fingerprints")     or [], body_tokens)

        confidence = filename_score * w_filename + body_score * w_body

        warnings: list[str] = []
        # min_body_chars cap: dock 20% if body is too short for the mapping's
        # expectation (suggests a stub/empty file).
        min_body = int(m.get("min_body_chars") or 0)
        if min_body and len(body_sample) < min_body:
            confidence *= 0.8
            warnings.append(
                f"body length {len(body_sample)} below min_body_chars={min_body}"
            )

        if confidence < confidence_floor:
            continue

        target_leaves   = list(m.get("target_leaves") or [])
        target_controls = sorted({t.get("control_ref") for t in target_leaves if t.get("control_ref")})
        cross_links     = [c.get("control") for c in (m.get("cross_control_links") or []) if c.get("control")]

        proposals.append(DocProposal(
            mapping_id      = m.get("mapping_id", "?"),
            mapping_path    = m.get("_path", ""),
            confidence      = round(confidence, 3),
            filename_score  = round(filename_score, 3),
            body_score      = round(body_score, 3),
            target_leaves   = target_leaves,
            target_controls = target_controls,
            cross_links     = cross_links,
            warnings        = warnings,
        ))

    # Best match first
    proposals.sort(key=lambda p: -p.confidence)
    return proposals


def union_target_controls(proposals: list[DocProposal]) -> list[str]:
    """Flatten the target_controls across all proposals into a deduped
    sorted list. The extractor scopes its LLM candidate set to this."""
    out: set[str] = set()
    for p in proposals:
        out.update(p.target_controls)
    return sorted(out)
