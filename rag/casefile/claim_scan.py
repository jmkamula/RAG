"""
Passive claim scanner (Ship 6'.d, 2026-07-19).

Scans a post-repair chat answer for normative-verb claims about
standards or refs ("Art.32 requires X", "under GDPR ...", "the
control mandates Y") and reports each as a ClaimEvent. Two
per-event signals help downstream reviewers spot the risky cases:

    ref_in_digest        — TRUE when the ref cited by the LLM is
                           present in the case-file's posture or
                           graph_nodes for this turn (safe).
                           FALSE means the LLM invoked a ref not
                           surfaced this turn — worth reviewing.

    standard_in_scope    — TRUE when the ref's standard family
                           (ISO 27001 / GDPR / ISO 27701) is in
                           the tenant's queryable_standards
                           (scope_standards on the CaseFile).

APPEND-ONLY passive design: the scanner NEVER rewrites answer
text, NEVER blocks the response, NEVER auto-append warnings. Its
output is logged to `chat_casefile_log.claim_events` for later
observability arcs (Ship 6'.e+).

See [[ship-6-prime-a-llm-role-audit-2026-07-18]] +
[[ship-6-prime-c-preservation-retrospective-2026-07-19]] for the
compliance-stakes framing that motivated this arc.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Optional


# ── Regex patterns ─────────────────────────────────────────────────
#
# Each pattern captures a (ref, verb) pair we want to flag. Refs
# can be:
#   Art.N       / Art.N.N     / Art.N.N.letter  — GDPR articles
#   A.N.N       / A.N.N.N                        — ISO Annex A
#   N.N         / N.N.N                          — ISMS clauses
#   ISO 27001 / ISO 27002 / ISO 27701 / GDPR    — standard names
#
# Verbs are the normative-claim verbs that could carry a false
# statement of fact. We deliberately exclude "may", "should",
# "could" — those are advisory, not claims-of-fact.

_REF_TOKEN = (
    r"(?:"
    r"Art\.\s*\d+(?:\.\d+)*(?:\.[a-z])?"
    r"|A\.\d+(?:\.\d+)*"
    r"|(?<!\d)\d+\.\d+(?:\.\d+)?"
    r"|ISO\s*27001(?::20\d{2})?"
    r"|ISO\s*27002(?::20\d{2})?"
    r"|ISO\s*27701(?::20\d{2})?"
    r"|GDPR"
    r")"
)

_NORMATIVE_VERB = (
    r"(?:requires?|mandates?|specifies?|states?|prescribes?|obliges?)"
)

# Pattern A — direct: "REF requires ...", "REF mandates ..."
_PATTERN_A = re.compile(
    rf"({_REF_TOKEN})\s+({_NORMATIVE_VERB})\s+([^.;\n]{{5,200}})",
    re.IGNORECASE,
)

# Pattern B — prepositional: "per REF ...", "under REF ...",
# "according to REF ...", "as required by REF ..."
_PATTERN_B = re.compile(
    rf"(?:per|according to|under|as required by|pursuant to)\s+"
    rf"({_REF_TOKEN})[,:\s]+([^.;\n]{{5,200}})",
    re.IGNORECASE,
)

# Pattern C — generic-noun: "the standard requires ...",
# "the article mandates ..." — no explicit ref, but a claim-of-fact.
# We report these with ref=None so the reviewer knows it's an
# untethered normative statement.
_PATTERN_C = re.compile(
    rf"the\s+(standard|regulation|article|control|obligation)\s+"
    rf"({_NORMATIVE_VERB})\s+([^.;\n]{{5,200}})",
    re.IGNORECASE,
)


# ── Data class ─────────────────────────────────────────────────────

@dataclass
class ClaimEvent:
    """One normative-verb claim detected in the LLM answer."""
    ref:               Optional[str]     # None for pattern C
    verb:              str
    snippet:           str               # what the claim asserts (200 chars max)
    ref_in_digest:     bool
    standard_in_scope: bool
    kind:              str               # 'direct' | 'prepositional' | 'generic'


# ── Ref-family helpers ─────────────────────────────────────────────

def _canonicalise_ref(raw: str) -> str:
    """Normalise the captured ref to the form used elsewhere in
    the codebase (rag.id_types conventions). 'Art. 32' → 'Art.32';
    'ISO 27001:2022' left as-is; whitespace stripped."""
    s = raw.strip()
    # Collapse "Art." + space + digits → "Art.N"
    s = re.sub(r"(Art\.)\s+(\d)", r"\1\2", s)
    # Collapse "ISO   27001" → "ISO 27001"
    s = re.sub(r"\s+", " ", s)
    return s


def _standard_family(ref: str) -> Optional[str]:
    """Infer which standard a ref belongs to. Returns one of:
    'ISO27001:2022', 'ISO27701:2019', 'GDPR:2016/679', or None
    when the ref is a standard name (e.g. 'GDPR' itself)."""
    r = ref.lower().replace(" ", "")
    if r.startswith("art."):
        return "GDPR:2016/679"
    if r.startswith("a."):
        return "ISO27001:2022"
    if re.match(r"^\d+\.\d+", r):
        return "ISO27001:2022"          # ISMS clauses live in ISO 27001
    if r.startswith("iso27001"):
        return "ISO27001:2022"
    if r.startswith("iso27701"):
        return "ISO27701:2019"
    if r.startswith("iso27002"):
        return "ISO27001:2022"          # 27002 is guidance for 27001
    if "gdpr" in r:
        return "GDPR:2016/679"
    return None


# ── Digest / scope introspection ───────────────────────────────────

def _digest_refs(case_file) -> set[str]:
    """The set of refs the LLM saw in this turn's case-file
    digest. Includes both posture refs (assessed for the tenant)
    and graph-node refs (surfaced in obligations / xfw sections)."""
    refs: set[str] = set()
    try:
        posture = case_file.posture_by_ref() or {}
        refs.update(posture.keys())
    except Exception:
        pass
    try:
        for n in case_file.all_nodes():
            r = getattr(n, "ref", None)
            if r:
                refs.add(r)
    except Exception:
        pass
    return refs


def _scope_standards(case_file) -> set[str]:
    try:
        return set(case_file.scope_standards or [])
    except Exception:
        return set()


# ── Main entry point ───────────────────────────────────────────────

def scan_claims(answer_text: str, case_file) -> list[ClaimEvent]:
    """Return every normative-verb claim found in `answer_text`,
    each enriched with ref_in_digest + standard_in_scope signals.

    Passive scan — the caller decides whether to log, alert, or
    ignore. This function has no side effects.
    """
    if not answer_text:
        return []

    digest_refs = _digest_refs(case_file)
    scope_stds  = _scope_standards(case_file)
    events:     list[ClaimEvent] = []

    def _make(ref_raw: Optional[str], verb: str, snippet: str, kind: str) -> ClaimEvent:
        ref = _canonicalise_ref(ref_raw) if ref_raw else None
        std = _standard_family(ref) if ref else None
        in_digest = bool(ref) and (ref in digest_refs)
        in_scope  = std in scope_stds if std else False
        return ClaimEvent(
            ref=ref,
            verb=verb.strip().lower(),
            snippet=snippet.strip()[:200],
            ref_in_digest=in_digest,
            standard_in_scope=in_scope,
            kind=kind,
        )

    for m in _PATTERN_A.finditer(answer_text):
        events.append(_make(m.group(1), m.group(2), m.group(3), "direct"))

    for m in _PATTERN_B.finditer(answer_text):
        # Pattern B's verb is implicit ("per REF, X"); use the
        # preposition as the verb marker for downstream filtering.
        prep_span = answer_text[m.start():m.start() + 40]
        prep_match = re.match(
            r"(per|according to|under|as required by|pursuant to)",
            prep_span, re.IGNORECASE,
        )
        prep = prep_match.group(1).lower() if prep_match else "per"
        events.append(_make(m.group(1), prep, m.group(2), "prepositional"))

    for m in _PATTERN_C.finditer(answer_text):
        events.append(_make(None, m.group(2), m.group(3), "generic"))

    return events


def claims_to_json(events: list[ClaimEvent]) -> list[dict]:
    """Serialize events for storage in jsonb. Preserves all fields."""
    return [asdict(e) for e in events]
