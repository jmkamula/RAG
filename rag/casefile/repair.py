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
    text = (answer_text or "").rstrip()
    events:  list[RepairEvent] = []
    footers: list[str]         = []

    if spec.is_empty():
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

    # ── 4. Missing bridge footer ─────────────────────────────────────
    if spec.bridge_footer:
        # Ship 1.14 already skips its own bridge footer append when
        # every bridge ref is present. Mirror that: only complain if
        # the footer or its content isn't already in the text.
        footer_present = spec.bridge_footer in text
        if not footer_present:
            # Also check for a partial footer — text may already carry
            # some of the bridge refs via the LLM's own citation.
            # (This matches llm_answer.py:1626 behaviour.)
            footer_refs = set(_REF_RE.findall(spec.bridge_footer))
            missing_bridge_refs = footer_refs - refs_present
            if missing_bridge_refs:
                events.append(RepairEvent(
                    kind="missing_bridge_footer",
                    ref=None,
                    detail=f"bridge footer absent + refs {sorted(missing_bridge_refs)} "
                           f"missing from answer",
                ))
                footers.append(spec.bridge_footer)

    # ── Build compliance-facts footer for missing refs ───────────────
    #     (draft/verdict-tag misses are consolidated by ref into the
    #      same footer entry; we don't add a separate footer per event.)
    refs_for_footer: set[str] = set(missing_refs)
    # Also include refs that were present in prose but stripped their
    # verdict tag — the footer restores the [NC-DRAFT] provenance.
    for ev in events:
        if ev.kind in ("missing_draft_near_ref", "missing_verdict_near_ref") and ev.ref:
            refs_for_footer.add(ev.ref)
    if refs_for_footer:
        facts_line = _compliance_facts_footer(
            sorted(refs_for_footer), spec, cf,
        )
        if facts_line:
            footers.append(facts_line)

    # ── 5. Ship 14'.e — Missing risk external_refs ────────────────────
    # When the classifier routed to POSTURE_RISK and the digest
    # surfaced N risks, the LLM should cite their external_refs (R-XXX)
    # in prose. Missing refs land in a dedicated risk-facts footer via
    # APPEND-ONLY discipline — never rewrites LLM prose.
    if spec.required_risk_refs:
        # Text-match on the raw external_ref (e.g. "R-042"). Case-
        # insensitive to catch "r-042" style variants.
        text_lower = text.lower()
        missing_risk_refs = [
            r for r in spec.required_risk_refs
            if r and r.lower() not in text_lower
        ]
        if missing_risk_refs:
            for r in missing_risk_refs:
                events.append(RepairEvent(
                    kind="missing_risk_ref",
                    ref=r,
                    detail=f"risk external_ref '{r}' absent from answer prose",
                ))
            footers.append(
                "↳ Risk register: " + ", ".join(missing_risk_refs)
            )

    # ── Assemble output ──────────────────────────────────────────────
    if footers:
        text = text + "\n\n" + "\n".join(footers)

    return RepairResult(text=text, events=events, footers_added=list(footers))
