"""
check_and_repair — post-answer verification against a PreservationSpec.

Given the LLM's answer_text + the PreservationSpec extracted from the
CaseFile, detects missing elements and repairs them deterministically.

Repair strategy: APPEND-ONLY. We never rewrite the LLM's prose (risk
of breaking a good answer chasing a subtle bug). Missing elements are
appended as footer lines — same pattern as Ship 1.14's bridge_footer.

Two footers may be appended:

  ↳ Bridges to ISO 27001 for Art.X: A.5.15 [Comply], A.5.18 [NC-DRAFT]
    (from PreservationSpec.bridge_footer)

  ↳ Compliance facts: A.5.18 [NC-DRAFT] — register incomplete;
                       A.5.20 [NC-DRAFT] — gap description
    (for required_refs the LLM dropped from prose)

Repair events are returned alongside the text so the caller can log
them to chat_casefile_log (Ship 2'.g) for measurement.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from rag.casefile.types import CaseFile
from rag.casefile.preservation import PreservationSpec


logger = logging.getLogger(__name__)


# ── Repair event ──────────────────────────────────────────────────────

@dataclass
class RepairEvent:
    kind:   str            # "missing_ref" | "missing_verdict_near_ref"
                           # | "missing_draft_near_ref" | "missing_bridge_footer"
    ref:    Optional[str] = None
    detail: str = ""


@dataclass
class RepairResult:
    text:            str
    events:          list[RepairEvent] = field(default_factory=list)
    footers_added:   list[str]         = field(default_factory=list)

    @property
    def repaired(self) -> bool:
        return bool(self.events)


# ── Detection primitives ─────────────────────────────────────────────

# Same regex as llm_answer.py's _VERIFIER_REF_RE — matches ISO Annex A,
# ISO body clauses, and GDPR articles.
_REF_RE = re.compile(
    r"\b(?:A\.\d+(?:\.\d+){0,2}|Art\.\d+(?:\.\d+)?|\d+\.\d+(?:\.\d+){0,2})\b"
)


def _refs_in_text(text: str) -> set[str]:
    """Refs literally present in the answer text."""
    return set(_REF_RE.findall(text or ""))


def _verdict_appears_near(text: str, ref: str, verdict: str, window: int = 80) -> bool:
    """True if `verdict` (NC/OFI/Comply) appears within `window` chars
    of any occurrence of `ref` in `text`."""
    if not (text and ref and verdict):
        return False
    lo = 0
    for m in re.finditer(re.escape(ref), text):
        start = max(0, m.start() - window)
        end   = min(len(text), m.end() + window)
        neighborhood = text[start:end]
        if re.search(rf"\b{re.escape(verdict)}\b", neighborhood, re.IGNORECASE):
            return True
        lo = m.end()
    return False


def _draft_appears_near(text: str, ref: str, window: int = 80) -> bool:
    """True if 'DRAFT' appears within `window` chars of any occurrence
    of `ref` in `text`."""
    if not (text and ref):
        return False
    for m in re.finditer(re.escape(ref), text):
        start = max(0, m.start() - window)
        end   = min(len(text), m.end() + window)
        if "DRAFT" in text[start:end].upper():
            return True
    return False


# ── Footer builders ──────────────────────────────────────────────────

from rag.casefile.digest import _verdict_tag, _sanitize_gap_text


def _compliance_facts_footer(
    missing_refs:   list[str],
    spec:           PreservationSpec,
    cf:             CaseFile,
) -> str:
    """Build a "↳ Compliance facts: ..." line for the refs the LLM
    dropped. Each entry carries the ref, verdict, [DRAFT] if
    unconfirmed, and a short body from the posture record.
    """
    if not missing_refs:
        return ""
    posture = cf.posture_by_ref()
    parts: list[str] = []
    for ref in sorted(missing_refs):
        rec = posture.get(ref) or {}
        verdict = spec.verdict_by_ref.get(ref)
        draft = ref in spec.draft_refs
        if verdict:
            tag = _verdict_tag(verdict, draft)
            body = ""
            if verdict in ("NC", "OFI"):
                body = _sanitize_gap_text((rec.get("gap_description") or "").strip())
            elif verdict == "Comply":
                body = _sanitize_gap_text((rec.get("evidence_text") or "").strip())
            body = " ".join(body.split())
            if len(body) > 100:
                body = body[:99] + "…"
            entry = f"{ref} {tag}"
            if body:
                entry += f" — {body}"
            parts.append(entry)
        else:
            # No verdict — the ref was cited but has no substantive
            # posture (e.g. an article that inherits from bridges).
            # Still record the ref so downstream can log it.
            parts.append(ref)
    if not parts:
        return ""
    return "↳ Compliance facts: " + "; ".join(parts)


# ── Main entry ───────────────────────────────────────────────────────

def check_and_repair(
    answer_text: str,
    spec:        PreservationSpec,
    cf:          CaseFile,
) -> RepairResult:
    """Verify answer against the preservation spec and append
    deterministic footers for anything the LLM dropped.

    Returns a RepairResult with the (possibly extended) text + a list
    of RepairEvents describing what was fixed.
    """
    # Ship 44'.d — OTel span. Case-file's preservation-check repair
    # pass is the deterministic guarantee that LLM prose doesn't drop
    # required refs. Trace event count → how often the LLM slips.
    from rag.telemetry import get_tracer
    _tracer = get_tracer(__name__)
    _span_cm = _tracer.start_as_current_span("arion.casefile.check_and_repair")
    _span = _span_cm.__enter__()

    text = (answer_text or "").rstrip()
    events:  list[RepairEvent] = []
    footers: list[str]         = []

    try:
        _span.set_attribute("arion.casefile.repair.input_chars", len(text))
        _span.set_attribute("arion.casefile.repair.n_required_refs",
                            len(spec.required_refs))
        _span.set_attribute("arion.casefile.repair.n_draft_refs",
                            len(spec.draft_refs))
    except Exception:
        pass

    if spec.is_empty():
        try:
            _span.set_attribute("arion.casefile.repair.spec_empty", True)
        except Exception:
            pass
        try: _span_cm.__exit__(None, None, None)
        except Exception: pass
        return RepairResult(text=text)

    refs_present = _refs_in_text(text)

    # ── 1. Missing required refs ─────────────────────────────────────
    missing_refs = sorted(spec.required_refs - refs_present)
    if missing_refs:
        for ref in missing_refs:
            events.append(RepairEvent(
                kind="missing_ref",
                ref=ref,
                detail=f"required ref '{ref}' absent from answer prose",
            ))

    # ── 2. Missing [DRAFT] near mentioned draft_refs ─────────────────
    #    Only checks refs the LLM actually included (otherwise it
    #    falls into #1 above).
    for ref in sorted(spec.draft_refs & refs_present):
        if not _draft_appears_near(text, ref):
            events.append(RepairEvent(
                kind="missing_draft_near_ref",
                ref=ref,
                detail=f"ref '{ref}' present but no DRAFT tag nearby "
                       f"(posture unconfirmed)",
            ))

    # ── 3. Missing verdict acronym near mentioned refs ──────────────
    for ref, verdict in sorted(spec.verdict_by_ref.items()):
        if ref not in refs_present:
            continue  # already counted in #1
        if not _verdict_appears_near(text, ref, verdict):
            events.append(RepairEvent(
                kind="missing_verdict_near_ref",
                ref=ref,
                detail=f"ref '{ref}' present but verdict "
                       f"'{verdict}' not adjacent",
            ))

    # ── 4. Missing bridge footer (RETIRED Ship 22'.b) ───────────────
    # Ship 20 made every chat path emit answer_structured;
    # cross_framework_bridge + demonstrated_by cards in related[]
    # render every ISO 27001 control linked to a cited GDPR article
    # (see rag/casefile/answer_augment.py::_collect_demonstrators +
    # _classify_relation). The bridge footer is structurally
    # redundant with those cards, so we retire the visible append.
    #
    # Repair events still fire for observability — auditors reading
    # chat_casefile_log.repair_events can identify bridge misses via
    # kind="missing_bridge_footer" and drill in through
    # scripts/audit_retired_footer.sql.
    if spec.bridge_footer:
        footer_refs = set(_REF_RE.findall(spec.bridge_footer))
        missing_bridge_refs = footer_refs - refs_present
        if missing_bridge_refs and spec.bridge_footer not in text:
            events.append(RepairEvent(
                kind="missing_bridge_footer",
                ref=None,
                detail=f"bridge footer absent + refs {sorted(missing_bridge_refs)} "
                       f"missing from answer",
            ))
            # NO footer append. `_build_bridge_footer` helper kept in
            # preservation.py for any future caller that wants to
            # reconstruct the string.

    # ── Compliance-facts footer RETIRED in Ship 21'.b ────────────────
    # Ship 20 made every chat path emit answer_structured; related[]
    # cards render every dropped ref with full metadata (verdict, role,
    # evidence summary, per-leaf checklist). The `↳ Compliance facts:`
    # append is structurally redundant with those cards + the truncated
    # tail ("still needed: operating procedure, sc…") was a UX
    # regression Ship 18/19 already fixed on the card render.
    #
    # Repair events (missing_ref / missing_draft_near_ref /
    # missing_verdict_near_ref) still populate above and land in
    # chat_casefile_log.repair_events for auditor drill-in via
    # scripts/audit_retired_footer.sql — the visible prose append is
    # the only thing removed. `_compliance_facts_footer` helper kept
    # for any future callers that want to reconstruct the string.
    # See ship-21-prime-a-footer-retire-design-2026-07-23 memo.

    # ── 5. Risk footer RETIRED in Ship 22'.c ─────────────────────────
    # Ship 22'.c added RiskCard + `risks: list[RiskCard]` to
    # StructuredAnswer, populated deterministically from
    # CaseFile.risks in augment_and_repair. `structured_to_prose`
    # renders a `## Risks` section listing every risk with threat +
    # score + treatment status + linked controls. The
    # `↳ Risk register: R-...` prose append is structurally
    # redundant.
    #
    # Repair events (missing_risk_ref) still fire for observability —
    # auditors reading chat_casefile_log.repair_events can identify
    # LLM drops via scripts/audit_retired_footer.sql.
    if spec.required_risk_refs:
        text_lower = text.lower()
        missing_risk_refs = [
            r for r in spec.required_risk_refs
            if r and r.lower() not in text_lower
        ]
        for r in missing_risk_refs:
            events.append(RepairEvent(
                kind="missing_risk_ref",
                ref=r,
                detail=f"risk external_ref '{r}' absent from answer prose",
            ))
        # NO footer append. RiskCard[] in the structured payload +
        # the `## Risks` prose section carry the equivalent content.

    # ── Assemble output ──────────────────────────────────────────────
    if footers:
        text = text + "\n\n" + "\n".join(footers)

    try:
        _span.set_attribute("arion.casefile.repair.events_count", len(events))
        _span.set_attribute("arion.casefile.repair.footers_added", len(footers))
        _span.set_attribute("arion.casefile.repair.output_chars", len(text))
        # Repair event kinds — counts by kind (privacy-safe: no content)
        kind_counts: dict[str, int] = {}
        for e in events:
            k = getattr(e, "kind", "unknown")
            kind_counts[k] = kind_counts.get(k, 0) + 1
        for k, n in kind_counts.items():
            _span.set_attribute(f"arion.casefile.repair.n_{k}", n)
    except Exception:
        pass
    try: _span_cm.__exit__(None, None, None)
    except Exception: pass

    return RepairResult(text=text, events=events, footers_added=list(footers))
