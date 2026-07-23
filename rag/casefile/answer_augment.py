"""
Structured answer augmentation (Ship 18'.b).

Deterministic backend logic that:
  1. Parses the LLM's JSON output into StructuredAnswer.
  2. Scans intro.text + actions[].body for cited refs.
  3. Builds RelatedCard[] from CaseFile (role, verdict, relation,
     evidence_summary, still_needed — all deterministic).
  4. Runs preservation-check verification against required_refs and
     INSERTS missing cards. APPEND-ONLY: LLM prose never rewritten.

Never raises on malformed LLM output — returns None so callers can
fall back to the prose path.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

from rag.casefile.answer_schema import (
    ActionCard,
    IntroCard,
    LeafState,
    RelatedCard,
    StructuredAnswer,
)


_LOG = logging.getLogger("rag.casefile.answer_augment")

# Ref pattern matches: A.5.15 / A.7.2.6 / Art.32 / Art.32.1.b / 9.2 / 10.1
_REF_RE = re.compile(
    r"\b(?:A\.\d+(?:\.\d+){1,3}|Art\.\s?\d+(?:\.\d+){0,3}[a-z]?|\d+\.\d+(?:\.\d+)?)\b"
)


# ── LLM output parsing ──────────────────────────────────────────────

def parse_llm_json(raw: str) -> Optional[dict]:
    """Best-effort JSON parse of LLM output. Returns None on failure.

    Tolerates:
      - LLM wrapping response in ```json ... ``` fences (retry
        with fences stripped)
      - Trailing prose after the JSON (finds first `{`, matches braces)
    """
    if not raw:
        return None

    text = raw.strip()

    # Strip common markdown code-fence wrappings
    if text.startswith("```"):
        # Drop the first line (```json or ```) and the trailing ```
        parts = text.split("\n", 1)
        if len(parts) == 2:
            text = parts[1]
        if text.endswith("```"):
            text = text[:-3].rstrip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try substring from first { to last }
    start = text.find("{")
    end   = text.rfind("}")
    if start >= 0 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return None


def parse_structured_answer(raw: str) -> Optional[StructuredAnswer]:
    """Parse LLM JSON output into a StructuredAnswer (with empty
    `related[]` — the caller populates it).

    Returns None if the payload is malformed or missing required fields.
    """
    payload = parse_llm_json(raw)
    if not isinstance(payload, dict):
        return None

    intro_data = payload.get("intro")
    if not isinstance(intro_data, dict):
        return None

    intro_text = (intro_data.get("text") or "").strip()
    if not intro_text:
        return None

    intro = IntroCard(
        text         = intro_text,
        primary_ref  = intro_data.get("primary_ref"),
        primary_role = intro_data.get("primary_role"),
    )

    actions_data = payload.get("actions") or []
    if not isinstance(actions_data, list):
        actions_data = []

    actions: list[ActionCard] = []
    for entry in actions_data:
        if not isinstance(entry, dict):
            continue
        title = (entry.get("title") or "").strip()
        body  = (entry.get("body")  or "").strip()
        if not title and not body:
            continue
        actions.append(ActionCard(
            title = title or "Action",
            body  = body,
            refs  = _refs_in(f"{title}\n{body}"),
        ))

    return StructuredAnswer(intro=intro, actions=actions, related=[])


# ── Ref extraction ──────────────────────────────────────────────────

def _refs_in(text: str) -> list[str]:
    """Return distinct refs in text order, normalising whitespace in
    Art. citations ("Art. 32" → "Art.32")."""
    if not text:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for m in _REF_RE.finditer(text):
        ref = m.group(0).replace("Art. ", "Art.").replace(" ", "")
        if ref not in seen:
            seen.add(ref)
            out.append(ref)
    return out


def collect_all_refs(structured: StructuredAnswer) -> list[str]:
    """Distinct refs found across intro.text + every action title+body."""
    parts = [structured.intro.text]
    for a in structured.actions:
        parts.append(a.title)
        parts.append(a.body)
    return _refs_in("\n".join(parts))


# ── Related-card builder ───────────────────────────────────────────

# Verdicts we surface. Anything else → "Unknown".
_KNOWN_VERDICTS = {"NC", "OFI", "Comply", "N/A", "Not Applicable"}


def _norm_verdict(finding: str) -> str:
    if not finding:
        return "Unknown"
    f = finding.strip()
    if f in _KNOWN_VERDICTS:
        return "N/A" if f == "Not Applicable" else f
    fl = f.lower()
    if fl == "nc":     return "NC"
    if fl == "ofi":    return "OFI"
    if fl == "comply": return "Comply"
    if fl in ("na", "n/a", "not_applicable"):
        return "N/A"
    return "Unknown"


def _relation_display(relation: str) -> str:
    """Human-readable label for the relation slug."""
    return {
        "primary":                "Primary control",
        "demonstrated_by":        "Demonstrates this obligation",
        "cross_framework_bridge": "Cross-framework link",
        "isms_clause":            "Management-system clause",
        "context":                "Related control",
    }.get(relation, "Related control")


def _standard_display(sid: str) -> str:
    """Route through the output gateway when available; fall back to a
    minimal in-place format."""
    if not sid:
        return ""
    try:
        from rag.output.gateway import humanize
        return humanize(sid, surface="structured_card")
    except Exception:
        # Minimal fallback — mirror format_standard_id's best-effort output.
        return sid.replace(":", " ").replace("_", " ")


def _dashboard_url(ref: str, standard_id: str) -> Optional[str]:
    """Match the frontend hash-router pattern (see arioncomply.html —
    Ship 4a `renderDemonstratedByPanel` uses this shape)."""
    if not ref:
        return None
    from urllib.parse import quote
    return f"/#dashboard?control={quote(ref)}"


def _node_metadata(cf, ref: str) -> tuple[str, str]:
    """Return (title, standard_id) from any resolver node with this ref,
    or fall back to posture record's control_ref + standard_id."""
    title = ""
    sid   = ""
    for n in cf.all_nodes():
        if getattr(n, "ref", None) == ref:
            title = getattr(n, "title", "") or ""
            sid   = getattr(n, "standard_id", "") or ""
            break
    if not sid:
        posture = cf.posture_for(ref) or {}
        sid = posture.get("standard_id") or ""
    return title, sid


def _classify_relation(
    cf,
    ref: str,
    primary_ref: Optional[str],
    demonstrated_by_primary: set[str],
) -> str:
    """Determine the relation slug for a ref, given the query's
    primary_ref + the set of demonstrators of the primary."""
    if primary_ref and ref == primary_ref:
        return "primary"
    if ref in demonstrated_by_primary:
        return "demonstrated_by"

    # ISMS management-system clauses look like 4.x / 5.x / ... / 10.x
    # (no A. prefix, no Art. prefix). Everything else with these numbers
    # is body-clause context to an Annex A primary.
    if re.match(r"^\d+\.\d+(?:\.\d+)?$", ref):
        # If the primary is an Annex A control (A.*) then the ISMS
        # clause is management-system context; otherwise it's context.
        if primary_ref and primary_ref.startswith("A."):
            return "isms_clause"
        return "isms_clause"

    # Same-standard vs cross-standard classification
    primary_sid = ""
    if primary_ref:
        _, primary_sid = _node_metadata(cf, primary_ref)
    ref_title, ref_sid = _node_metadata(cf, ref)

    if primary_sid and ref_sid and primary_sid != ref_sid:
        return "cross_framework_bridge"
    return "context"


def _collect_demonstrators(cf, primary_ref: Optional[str]) -> set[str]:
    """When the primary ref is an obligation, collect the set of
    program/extension refs that DEMONSTRATE it. Empty set otherwise.

    Uses `cf.demonstrated_by(ref)` which reads from the posture record's
    demonstrated_by overlay (populated by posture_loader per Phase 2b)."""
    if not primary_ref:
        return set()
    out: set[str] = set()
    for entry in cf.demonstrated_by(primary_ref):
        src_id = entry.get("src_id") or ""
        if not src_id:
            continue
        # src_id shape: STANDARD:VERSION:REF — extract the ref tail
        parts = src_id.rsplit(":", 1)
        if len(parts) == 2 and parts[1]:
            out.add(parts[1])
    return out


def _evidence_summary(
    pg_conn,
    tenant_id: str,
    ref: str,
    standard_id: str,
    verdict: str,
) -> tuple[str, list[str], list[LeafState]]:
    """Return (summary_text, still_needed_names, leaves) for a related card.

    Ship 19'.b — extended to return per-leaf state so the primary
    card can render a ✓/○ checklist. leaves[] populated for ALL
    cards; frontend decides render granularity (primary only, in
    Ship 19'.c).

    Only queries advisory for NC/OFI verdicts on non-empty standards.
    Fails silently on any error → returns ('', [], [])."""
    if verdict not in ("NC", "OFI"):
        return "", [], []
    if not (pg_conn and tenant_id and standard_id and ref):
        return "", [], []

    try:
        from rag.posture.advisory import build_per_must_advisory_data
        data = build_per_must_advisory_data(
            pg_conn      = pg_conn,
            tenant_id    = tenant_id,
            control_ref  = ref,
            standard_id  = standard_id,
        )
    except Exception as e:
        _LOG.debug("advisory lookup failed for %s: %s", ref, e)
        return "", [], []

    if not data:
        return "", [], []

    n_leaves    = data.get("n_leaves") or 0
    n_satisfied = data.get("n_satisfied") or 0
    n_partial   = data.get("n_partial") or 0
    if not n_leaves:
        return "", [], []

    if n_partial:
        summary = (
            f"{n_satisfied} of {n_leaves} required items present "
            f"({n_partial} with partial evidence)"
        )
    else:
        summary = f"{n_satisfied} of {n_leaves} required items present"

    # still_needed — leaves not satisfied whose labels we know
    still: list[str] = []
    # leaves[] — full per-leaf state for primary-card checklist
    leaves: list[LeafState] = []
    for leaf in data.get("leaves") or []:
        label = leaf.get("leaf_label") or ""
        if not label:
            continue
        satisfied = bool(leaf.get("satisfied"))
        leaves.append(LeafState(
            leaf_id             = leaf.get("leaf_id") or "",
            title               = label,
            evidence_type       = leaf.get("evidence_type") or "",
            evidence_type_label = leaf.get("evidence_type_label") or "",
            satisfied           = satisfied,
            n_have              = int(leaf.get("n_have") or 0),
            n_total             = int(leaf.get("n_total") or 0),
        ))
        if not satisfied:
            still.append(label)

    return summary, still[:6], leaves


def build_related_cards(
    cf,
    structured: StructuredAnswer,
    *,
    pg_conn = None,
    tenant_id: str = "",
    extra_refs: Optional[list[str]] = None,
) -> list[RelatedCard]:
    """Build the RelatedCard[] deterministically from the CaseFile.

    Union of:
      - refs the LLM cited in intro.text + actions[]
      - `extra_refs` (typically CaseFile.required_refs from
        preservation-check — ensures dropped refs still get cards)

    Cards are ordered:  primary → demonstrated_by → cross_framework →
    isms_clause → context.
    """
    cited = collect_all_refs(structured)
    extras = list(extra_refs or [])
    all_refs: list[str] = []
    seen: set[str] = set()
    for r in cited + extras:
        if r and r not in seen:
            seen.add(r)
            all_refs.append(r)

    primary_ref = structured.intro.primary_ref or (cited[0] if cited else None)
    demonstrators = _collect_demonstrators(cf, primary_ref)

    cards: list[RelatedCard] = []
    for ref in all_refs:
        title, sid = _node_metadata(cf, ref)

        # Skip refs we can't identify at all — no title, no standard.
        # Prevents surfacing arbitrary numeric strings.
        if not title and not sid:
            continue

        posture = cf.posture_for(ref) or {}
        verdict = _norm_verdict(posture.get("finding") or "")
        draft   = cf.needs_draft_tag(ref)
        role    = cf.role_of(ref) or "unknown"

        relation = _classify_relation(cf, ref, primary_ref, demonstrators)
        summary, still, leaves = _evidence_summary(pg_conn, tenant_id, ref, sid, verdict)

        cards.append(RelatedCard(
            ref              = ref,
            standard_id      = sid,
            standard_display = _standard_display(sid) or sid,
            title            = title or "",
            role             = role,
            verdict          = verdict,
            draft            = draft,
            relation         = relation,
            relation_display = _relation_display(relation),
            evidence_summary = summary,
            still_needed     = still,
            leaves           = leaves,
            dashboard_url    = _dashboard_url(ref, sid),
        ))

    # Sort: primary first, then demonstrated_by, cross-framework, isms
    # clause, context. Within each bucket, keep insertion order.
    _ORDER = {
        "primary":                0,
        "demonstrated_by":        1,
        "cross_framework_bridge": 2,
        "isms_clause":            3,
        "context":                4,
    }
    cards.sort(key=lambda c: (_ORDER.get(c.relation, 9), 0))

    # Now that we've done any ordering, fill each action card's `refs`
    # so the UI can render chips consistent with related-card presence.
    known_refs = {c.ref for c in cards}
    for action in structured.actions:
        action.refs = [r for r in action.refs if r in known_refs]

    return cards


# ── Preservation-check verification ─────────────────────────────────

def augment_and_repair(
    structured: StructuredAnswer,
    cf,
    spec,
    *,
    pg_conn = None,
    tenant_id: str = "",
) -> tuple[StructuredAnswer, list[dict]]:
    """Attach related cards + repair missing required_refs by INSERTING
    them. Returns (augmented_answer, repair_events).

    APPEND-ONLY: intro + actions are never modified. Missing refs get
    a RelatedCard inserted with the appropriate role/verdict.

    repair_events are compatible with chat_casefile_log's schema —
    each event is {kind, ref, detail}.
    """
    events: list[dict] = []

    # Build related cards including required_refs (guarantees they
    # get a card even if LLM omitted them from prose).
    extra_refs = sorted(spec.required_refs) if spec and spec.required_refs else []
    related = build_related_cards(
        cf,
        structured,
        pg_conn    = pg_conn,
        tenant_id  = tenant_id,
        extra_refs = extra_refs,
    )
    structured.related = related

    # Preservation-check repair events — record what would have been
    # missing from prose alone (auditor trail; the card presence
    # already handles it).
    cited = set(collect_all_refs(structured))
    if spec and spec.required_refs:
        missing = spec.required_refs - cited
        for ref in sorted(missing):
            events.append({
                "kind":   "missing_ref_structured",
                "ref":    ref,
                "detail": f"required ref '{ref}' absent from intro/actions "
                          f"— surfaced via RelatedCard insertion",
            })

    # Draft-tag events — every draft ref must have `draft=True` on
    # its card (deterministic per cf.needs_draft_tag; the card always
    # sets this correctly, so we log here only for parity with the
    # prose repair pass).
    if spec and spec.draft_refs:
        card_refs = {c.ref: c for c in structured.related}
        for ref in sorted(spec.draft_refs):
            card = card_refs.get(ref)
            if card and not card.draft:
                # This shouldn't happen (cf.needs_draft_tag is
                # deterministic) but log it if it does.
                events.append({
                    "kind":   "missing_draft_structured",
                    "ref":    ref,
                    "detail": f"draft ref '{ref}' present but card.draft=False",
                })

    return structured, events
