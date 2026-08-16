"""rag/intake/finding_contract.py — Ship 72'.a (2026-08-16).

Single source of truth for what constitutes a valid tenant finding at
extract time. Every extractor path (templated edit zones, LLM-driven
prose extraction, workbook per-cell, xlsx tabular, tabular-column
metadata) emits raw `ExtractedCandidate` objects. `FindingContract.bind`
applies the domain rules — valid checklist_item_id, non-scaffolding
excerpt text, resolvable control_ref + standard_id — and either
constructs a `DocumentFinding` or logs + skips with a reason code.

Motivation (from Ship 72' arc opener):
  The extractor-side rules "what is a valid finding?" were scattered
  across ~5 call sites. Task #603 (empty edit zones by default)
  exposed a pre-existing hole: `_is_pure_scaffolding` in the templated
  path didn't recognize the reader-reconstructed docx scaffolding
  shape (`*Standard text:*`, `_Behavioural principle_`, `✓ Good:`,
  `__Best practice__`). Fixing it in the one call site would have
  perpetuated the scatter — next month someone adds a new marker and
  three sites need to know about it.

  The rule "text X is scaffolding, text Y is tenant evidence" is a
  domain concept that spans every extractor. It lives here, once.

Codified lesson 44 (Ship 72'.a) — domain rules at the highest layer,
not the call site.

Design:
  - `ExtractedCandidate` is a lightweight dataclass — item_id +
    excerpt text + source context (extractor name, zone id, etc)
    for logs.
  - `FindingContract.bind(candidate) -> Optional[DocumentFinding]`
    runs every check + emits a `DocumentFinding` on success, or
    logs the skip reason + increments a metric on failure.
  - `SkipReason` enum makes the reject reasons observable in
    `intake_trace_log` (Ship 72'.d consolidates the ad-hoc metrics
    onto this).
  - Predicates (`_catalog_recognises`, `is_scaffolding`) exposed as
    module-level functions so tests can pin them directly.

Public surface:
  is_scaffolding(text)      -> bool
  _catalog_recognises(id)   -> bool   (re-exported from extractor)
  ExtractedCandidate        -> dataclass
  SkipReason                -> enum
  FindingContract           -> class with .bind()
  FINDING_CONTRACT          -> default module-level singleton
"""
from __future__ import annotations

import enum
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from .models import DocumentFinding

logger = logging.getLogger(__name__)


# ── Scaffolding recognition ──────────────────────────────────────────
#
# A tenant-authored excerpt must contain SOMETHING that isn't part of
# our own template scaffolding. Ship 72'.a's predicate strips every
# scaffolding shape our renderers emit + checks whether anything
# substantive remains.
#
# The shapes covered here match what:
#   - rag/templates/renderer.py emits into markdown template body
#   - rag/templates/docx_renderer.py emits into .docx runs
#   - rag/intake/readers.py::_arion_docx_to_edit_zones reconstructs
#     back into markdown on re-upload
#
# When adding a new scaffolding pattern (e.g. a new callout style),
# add its regex here and every extractor picks it up automatically.

# Placeholder tokens the renderer emits when there's no tenant text
_SCAFFOLDING_PLACEHOLDER_RES = (
    re.compile(r"<<\s*TEXT\s*>>", re.IGNORECASE),
    re.compile(r"<<\s*NAME\s*>>", re.IGNORECASE),
    re.compile(
        r"\[\s*Click to enter your evidence here\s*\]", re.IGNORECASE,
    ),
)

# Comments the renderer inserts for prefill provenance
_SCAFFOLDING_PROVENANCE_RES = (
    re.compile(r"<!--\s*prefilled from [^>]+-->", re.IGNORECASE),
    re.compile(r"<!--\s*EDIT-ZONE-(?:START|END)\s+item:[^>]+-->", re.IGNORECASE),
    re.compile(r"<!--\s*TABLE-COLUMNS[^>]*-->", re.IGNORECASE),
    re.compile(r"<!--\s*column:\s*item:[^>]+-->", re.IGNORECASE),
)

# Reader-reconstructed scaffolding lines. Mammoth wraps bold with `__`
# and italics with `*`; both wrappings escaped by mammoth's own
# markdown emitter.  Every pattern here matches a WHOLE LINE (^…$
# with MULTILINE) so stripping is line-precise.
_SCAFFOLDING_LINE_RES = (
    # "◆ Required element — <slug>" / "◆ Recommended addition — <slug>"
    # These are the visible labels the reader keys off of but they're
    # scaffolding, not tenant evidence.
    re.compile(
        r"^\s*(?:__|\*\*)?\s*◆\s*(?:Required element|Recommended addition)\s*—[^\n]*$",
        re.MULTILINE,
    ),
    # "*Do not edit — system id*: <<MUST item:X:Y>>" (renderer.py:1026)
    re.compile(
        r"^\s*\*?Do not edit — system id\*?:\s*[`]?<<(?:MUST|SHOULD)\s+item:[^>]+>>[`]?\s*$",
        re.MULTILINE,
    ),
    # "*Standard text:* <prose>" — the standard obligation label
    re.compile(
        r"^\s*[>]?\s*\*?Standard text:\*?\s*[^\n]*$",
        re.MULTILINE,
    ),
    # "*Why: ...*" standalone italic Why line (Ship 57' prereq guidance)
    re.compile(r"^\s*\*?Why:\s[^\n]*\*?\s*$", re.MULTILINE),
    # "*Good enough: ...*" prereq acceptance line
    re.compile(r"^\s*\*?Good enough:\s[^\n]*\*?\s*$", re.MULTILINE),
    # "__✓ Good__:" / "__✓ Good (…)__:" example blocks header
    re.compile(
        r"^\s*(?:__|\*\*)?\s*[✓✗]\s*(?:Good|Not good)(?:\s*\([^)]+\))?(?:__|\*\*)?:\s*$",
        re.MULTILINE,
    ),
    # "__Best practice(...):__" header — Ship 56'.a + tick indicator
    re.compile(
        r"^\s*(?:__|\*\*)?\s*Best practice(?:\s*[✓◐])?[^:]*:(?:__|\*\*)?\s*$",
        re.MULTILINE,
    ),
    # Task #577 iteration marks — ☑/☐ per-bullet guidance lines
    re.compile(
        r"^\s*[-*]\s*[☑☐]\s+[^\n]*$",
        re.MULTILINE,
    ),
    # "▽ Enter your evidence for X below ▽" / "△ End of X △" rails
    re.compile(r"^\s*[▽△][^\n]*$", re.MULTILINE),
    # Horizontal rules the renderer inserts as section separators
    re.compile(r"^\s*[-─═]{3,}\s*$", re.MULTILINE),
    # "[Not applicable to your scope — no evidence required.]" — the
    # N/A callout inserted when a MUST is out of scope for the tenant.
    re.compile(
        r"^\s*\[Not applicable[^\]]*\]\s*$",
        re.MULTILINE,
    ),
    # Prereq category headers ("Foundational" / "Direct upstream" /
    # "Cross-framework") emitted as bold single-word paragraphs.
    re.compile(
        r"^\s*(?:__|\*\*)\s*(?:Foundational|Direct upstream|Cross-framework)\s*(?:__|\*\*)\s*$",
        re.MULTILINE,
    ),
)


def is_scaffolding(text: str) -> bool:
    """Return True when `text` contains only template scaffolding — no
    tenant-authored evidence.

    Algorithm: sequentially strip every scaffolding pattern our
    renderers can emit; if the remainder is empty (modulo whitespace),
    it's pure scaffolding.

    This is the app-wide canonical answer to "should this text produce
    a document_findings row?" — every extractor path consumes it.

    A `None`/empty input is trivially scaffolding.
    """
    if not text or not text.strip():
        return True
    residual = text
    for rx in _SCAFFOLDING_PLACEHOLDER_RES:
        residual = rx.sub("", residual)
    for rx in _SCAFFOLDING_PROVENANCE_RES:
        residual = rx.sub("", residual)
    for rx in _SCAFFOLDING_LINE_RES:
        residual = rx.sub("", residual)
    # Blockquote residues — a `> …` line that's now just `>` after
    # its content was stripped, likewise standalone `___` etc.
    residual = re.sub(r"^\s*>\s*$", "", residual, flags=re.MULTILINE)
    residual = re.sub(r"^\s*_{3,}\s*$", "", residual, flags=re.MULTILINE)
    # Any bare markdown escape residue (mammoth emits `A\.5\.15`) —
    # strip line-wrap artifacts + whitespace.
    residual = residual.replace("\\", "").strip()
    return not residual


# ── Catalog membership predicate ──────────────────────────────────────
#
# Shared with rag/intake/extractor.py's `_catalog_recognises` (Task #606).
# Re-implemented here so the contract module doesn't circular-import.

_valid_item_ids_cache: Optional[set[str]] = None


def _valid_item_ids() -> set[str]:
    global _valid_item_ids_cache
    if _valid_item_ids_cache is not None:
        return _valid_item_ids_cache
    try:
        from enrichment.documents.document_requirements import (
            ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
        )
    except Exception:
        _valid_item_ids_cache = set()
        return _valid_item_ids_cache
    valid: set[str] = set()
    all_ers = list(ALL_EVIDENCE_REQUIREMENTS)
    for ds in ALL_DERIVED_SPECS:
        all_ers.extend(ds.direct_evidence or [])
    for er in all_ers:
        for ci in list(er.must_contain) + list(er.should_contain):
            if ci and getattr(ci, "id", None):
                valid.add(ci.id)
    _valid_item_ids_cache = valid
    return _valid_item_ids_cache


def catalog_recognises(item_id: str) -> bool:
    """True iff `item_id` is a curated ChecklistItem id."""
    return item_id in _valid_item_ids()


# ── Contract types ──────────────────────────────────────────────────


class SkipReason(str, enum.Enum):
    """Observable rejection reason. Ship 72'.d wires these into
    intake_trace_log metrics."""
    OK                = "ok"
    EMPTY_TEXT        = "empty_text"
    PURE_SCAFFOLDING  = "pure_scaffolding"
    MANGLED_ITEM_ID   = "mangled_item_id"
    UNRESOLVABLE_REF  = "unresolvable_control_ref"


@dataclass
class ExtractedCandidate:
    """One candidate finding proposed by an extractor. The `FindingContract`
    decides whether it becomes a `DocumentFinding` or gets skipped."""
    item_id:         str
    excerpt_text:    str
    document_name:   str
    upload_id:       str = ""
    tenant_id:       str = ""
    # Optional intel about which extractor path proposed the candidate —
    # populated by callers for logs + metrics; never affects the bind
    # decision.
    source_context:  dict = field(default_factory=dict)
    # Per-extractor overrides — defaulted to sane values by bind().
    finding:         str = "Comply"
    confidence:      str = "high"
    section:         Optional[str] = None
    page_number:     Optional[int] = None
    inference_source: Optional[str] = None
    extraction_path: str = "templated"
    # Ship 72'.b — LLM-path chunk provenance. Survives round-trip into
    # DocumentFinding for tenant-facing observability.
    chunk_id:        Optional[str] = None
    # Ship 72'.b — control_ref override for extractors that resolved
    # the ref through a non-item_id path (LLM output, structured rows,
    # fingerprints). When set, the contract skips the `item_control_ref`
    # derivation and uses this instead.
    control_ref:     Optional[str] = None
    standard_id:     Optional[str] = None


@dataclass
class BindResult:
    """Outcome of a FindingContract.bind() call. `finding` is populated
    on success, None on skip; `reason` is always populated."""
    reason:  SkipReason
    finding: Optional[DocumentFinding] = None


class FindingContract:
    """App-wide gate for extractor-emitted findings.

    Every extractor path is expected to call `.bind(candidate)` instead
    of directly constructing `DocumentFinding`. When the contract rejects
    a candidate, the reason is logged + a metrics counter increments —
    downstream (Ship 72'.d) intake_trace_log surfaces the counters so
    silent drops become observable.

    Stateless per-instance; the shared singleton `FINDING_CONTRACT`
    below is what most callers should use.
    """

    def bind(self, candidate: ExtractedCandidate) -> BindResult:
        # 1. Trivial empty check — often the extractor's regex captured
        # a marker with no body.
        text = (candidate.excerpt_text or "").strip()
        if not text:
            self._log_skip(SkipReason.EMPTY_TEXT, candidate)
            return BindResult(reason=SkipReason.EMPTY_TEXT)

        # 2. Valid item_id? — Task #606's catalog membership check.
        # LLM path may propose findings with no per-MUST binding; when
        # item_id is empty the caller passes "" and we skip the check —
        # such findings are dropped by the LLM path's own gate
        # (`bound_item_id is None`) BEFORE they reach the contract.
        if candidate.item_id and not catalog_recognises(candidate.item_id):
            self._log_skip(SkipReason.MANGLED_ITEM_ID, candidate)
            return BindResult(reason=SkipReason.MANGLED_ITEM_ID)

        # 3. Non-scaffolding text? — Ship 72'.a's is_scaffolding
        # predicate replaces every extractor's local scaffolding check.
        if is_scaffolding(text):
            self._log_skip(SkipReason.PURE_SCAFFOLDING, candidate)
            return BindResult(reason=SkipReason.PURE_SCAFFOLDING)

        # 4. Resolvable control_ref? — item:A.5.15:X → A.5.15. When
        # the caller pre-resolved the ref (LLM path, structured rows),
        # use that instead of deriving from item_id.
        control_ref = candidate.control_ref
        if not control_ref and candidate.item_id:
            from rag.id_types import item_control_ref
            control_ref = item_control_ref(candidate.item_id)
        if not control_ref:
            self._log_skip(SkipReason.UNRESOLVABLE_REF, candidate)
            return BindResult(reason=SkipReason.UNRESOLVABLE_REF)

        # 5. Resolvable standard_id?
        standard_id = candidate.standard_id
        if not standard_id:
            from rag.intake.extractor import _control_ref_to_standard
            standard_id = _control_ref_to_standard(control_ref)

        finding = DocumentFinding(
            upload_id         = candidate.upload_id,
            tenant_id         = candidate.tenant_id,
            document_name     = candidate.document_name,
            control_ref       = control_ref,
            standard_id       = standard_id,
            finding           = candidate.finding,
            evidence_text     = text[:500],
            confidence        = candidate.confidence,
            checklist_item_id = candidate.item_id or None,
            section           = candidate.section,
            page_number       = candidate.page_number,
            extraction_path   = candidate.extraction_path,
            inference_source  = candidate.inference_source,
            chunk_id          = candidate.chunk_id,
        )
        return BindResult(reason=SkipReason.OK, finding=finding)

    def _log_skip(self, reason: SkipReason, candidate: ExtractedCandidate) -> None:
        """Log at WARNING for anomalies (mangled ids, unresolvable refs)
        and at DEBUG for expected drops (empty text, pure scaffolding)
        so a normal upload doesn't spam WARN."""
        if reason in (SkipReason.MANGLED_ITEM_ID, SkipReason.UNRESOLVABLE_REF):
            logger.warning(
                "FindingContract skip: reason=%s item_id=%r context=%r",
                reason.value, candidate.item_id, candidate.source_context,
            )
        else:
            logger.debug(
                "FindingContract skip: reason=%s item_id=%r",
                reason.value, candidate.item_id,
            )


# Module-level singleton for most callers.
FINDING_CONTRACT: FindingContract = FindingContract()
