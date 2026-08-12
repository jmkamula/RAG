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
    RiskCard,
    StructuredAnswer,
)


# ── Ship 20'.b — CaseFileShim for short-circuit paths ───────────────
#
# build_related_cards() below requires a CaseFile for role/verdict/
# relation lookup. The LLM path builds one via SimpleNamespace at
# rank_and_answer:1132. Short-circuits don't carry the resolver
# outputs — they have `tenant` + `posture`. This shim duck-types the
# 5 methods build_related_cards uses so short-circuits can reuse it
# without touching the LLM-path code.

def _norm_finding(f):
    """Normalize finding to the canonical form CaseFile.needs_draft_tag
    expects."""
    if not f: return ""
    fl = str(f).strip()
    if fl in ("NC", "OFI", "Comply", "N/A"):
        return fl
    up = fl.upper()
    if up in ("NC", "OFI", "COMPLY"):
        return {"NC":"NC","OFI":"OFI","COMPLY":"Comply"}[up]
    return fl


class CaseFileShim:
    """Lightweight duck-typed stand-in for CaseFile.

    Used by short-circuit paths (Ship 20) that need to call
    build_related_cards without having built a full CaseFile.

    Constructor takes:
      * tenant         — tenant profile (for scope role_map lookup)
      * posture_by_ref — dict keyed by ref (NOT node_id — the
                         short-circuit paths typically only have refs)
      * node_lookup    — optional dict {ref: {"title": str,
                         "standard_id": str}} — populated by a
                         Neo4j fetch when the short-circuit has refs
                         it wants surfaced as cards
    """
    def __init__(self, tenant, posture_by_ref=None, node_lookup=None):
        self.tenant = tenant
        self._posture_by_ref = dict(posture_by_ref or {})
        self._node_lookup    = dict(node_lookup or {})

    # ── CaseFile-duck-typed methods used by build_related_cards ──

    def all_nodes(self):
        """Return duck-typed nodes exposing `ref`, `title`,
        `standard_id`, `xfw_edges` for every ref in node_lookup.

        _node_metadata iterates this to find title + standard_id.
        Short-circuits typically don't carry xfw_edges (bridges are
        resolved via the LLM path). Return [] when no lookup was
        prefetched.
        """
        from types import SimpleNamespace
        out = []
        for ref, meta in self._node_lookup.items():
            out.append(SimpleNamespace(
                ref         = ref,
                title       = meta.get("title", "") or "",
                standard_id = meta.get("standard_id", "") or "",
                xfw_edges   = [],
            ))
        return out

    def posture_for(self, ref):
        return self._posture_by_ref.get(ref)

    def needs_draft_tag(self, ref):
        rec = self.posture_for(ref) or {}
        finding = _norm_finding(rec.get("finding"))
        if finding not in ("NC", "OFI", "Comply"):
            return False
        return rec.get("confirmation_status") not in (
            "system_confirmed", "auditor_confirmed",
        )

    def role_of(self, ref):
        """Lookup role via tenant.scope role-grouped accessors +
        Postgres fallback (matches CaseFile.role_of behaviour)."""
        rec = self.posture_for(ref) or {}
        sid = rec.get("standard_id") or self._node_lookup.get(ref, {}).get("standard_id")
        if not sid:
            return None
        # Reuse CaseFile's role-map builder to keep behaviour consistent
        # (framework-role-model-arc). Build a minimal cf-shaped object
        # for `_load_standards_role_map` to see the scope.
        from types import SimpleNamespace
        _cf_like = SimpleNamespace(tenant=self.tenant, resolved=None)
        # Duck-type CaseFile._role_map by shortcutting into its scope
        # accessor logic.
        scope = getattr(self.tenant, "scope", None)
        if scope is not None:
            for group_name in ("programs", "extensions", "obligations"):
                role = group_name.rstrip("s")
                group = getattr(scope, group_name, None) or []
                for s in group:
                    if getattr(s, "id", None) == sid:
                        return role
        # Postgres fallback via process-cached loader
        try:
            from rag.casefile.types import _load_standards_role_map
            return _load_standards_role_map().get(sid)
        except Exception:
            return None

    def demonstrated_by(self, ref):
        rec = self.posture_for(ref) or {}
        return list(rec.get("demonstrated_by") or [])

    @property
    def tenant_name(self):
        return getattr(self.tenant, "name", "") or ""


# ── Ship 21'.b — structured_to_prose ────────────────────────────────
#
# Reconstruct answer_text prose from a StructuredAnswer. Used by
# both LLM path (rank_and_answer._casefile_flow) and short-circuits
# that want a canonical prose composition. Emits markdown so SDK/CLI
# consumers get a readable answer even without card rendering.
#
# Format (Ship 21'.a design):
#   {intro.text}
#
#   ## {action.title}
#   {action.body}
#
#   ## Related controls
#   - **A.5.15** (Access control, ISO 27001:2022) — OFI-DRAFT —
#     1 of 4 items present
#   - **10.1** (Continual improvement, ISO 27001:2022) — NC-DRAFT
#
# Related section is included ONLY when there's at least one card;
# omitted for intro-only payloads to keep clarify / N/A / no-refs
# responses clean.

def structured_to_prose(structured) -> str:
    """Render a StructuredAnswer as clean markdown prose.

    Replaces the old `title: body` inline reconstruction (Ship
    18'.b) — that format lost related-card detail entirely, and
    the `↳ Compliance facts:` footer (retired Ship 21'.b) was
    covering the gap awkwardly. This helper puts everything the
    cards show into the prose."""
    if structured is None:
        return ""

    lines: list[str] = []

    intro_text = (getattr(structured.intro, "text", None) or "").strip()
    if intro_text:
        lines.append(intro_text)

    for a in (structured.actions or []):
        title = (a.title or "").strip()
        body  = (a.body  or "").strip()
        if not (title or body):
            continue
        if lines:
            lines.append("")
        if title:
            lines.append(f"## {title}")
        if body:
            lines.append(body)

    # Ship 23'.c — group related cards into role-labeled sections
    # (Primary → Programs → Extensions → Obligations → Other).
    # Ordering + section headers make the auditor's mental model
    # explicit: "here's the primary control; here are the ISO 27001
    # programs implementing it; here are the ISO 27701 privacy
    # extensions on top; here are the GDPR obligations it demonstrates."
    related = list(structured.related or [])
    if related:
        groups: dict[str, list] = {
            "primary": [], "program": [], "extension": [],
            "obligation": [], "isms_clause": [], "other": [],
        }
        for r in related:
            rel = getattr(r, "relation", "") or ""
            if rel == "primary":
                groups["primary"].append(r)
            elif rel == "program":
                groups["program"].append(r)
            elif rel == "extension":
                groups["extension"].append(r)
            elif rel in ("obligation", "demonstrated_by"):
                # `demonstrated_by` (legacy) shows programs/extensions
                # demonstrating an obligation; from the primary-is-
                # obligation perspective these cards ARE programs +
                # extensions. Group by the card's role rather than
                # the legacy label.
                card_role = getattr(r, "role", "") or ""
                if card_role == "program":
                    groups["program"].append(r)
                elif card_role == "extension":
                    groups["extension"].append(r)
                elif card_role == "obligation":
                    groups["obligation"].append(r)
                else:
                    groups["other"].append(r)
            elif rel == "isms_clause":
                groups["isms_clause"].append(r)
            else:
                groups["other"].append(r)

        def _fmt_card(r) -> str:
            ref = (getattr(r, "ref", "") or "").strip()
            if not ref:
                return ""
            title    = (getattr(r, "title", "") or "").strip()
            std_disp = (getattr(r, "standard_display", "") or "").strip()
            verdict  = (getattr(r, "verdict", "") or "").strip() or "Unknown"
            draft    = bool(getattr(r, "draft", False))
            evidence = (getattr(r, "evidence_summary", "") or "").strip()

            verdict_tag = f"{verdict}-DRAFT" if draft and verdict in (
                "NC", "OFI", "Comply"
            ) else verdict
            context_parts = [p for p in (title, std_disp) if p]
            context = f" ({', '.join(context_parts)})" if context_parts else ""
            entry = f"- **{ref}**{context} — {verdict_tag}"
            if evidence:
                entry += f" — {evidence}"
            return entry

        # Section headers per role group. Sections omitted when empty.
        # relation_key is the raw slug used to look up overflow_counts;
        # section_key is the frontend/prose grouping bucket.
        section_headers = [
            # (section_key, header, relation_key(s) for overflow lookup)
            ("primary",     None,                              ("primary",)),
            ("program",     "## Programs",                     ("program",)),
            ("extension",   "## Extensions",                   ("extension",)),
            ("obligation",  "## Obligations",                  ("obligation",)),
            ("isms_clause", "## Management-system clauses",    ("isms_clause",)),
            ("other",       "## Related controls",             ("context", "cross_framework_bridge")),
        ]
        overflow_counts = getattr(structured, "overflow_counts", None) or {}
        primary_ref_for_drill = (getattr(structured.intro, "primary_ref", "") or "").strip()

        for group_key, header, relation_keys in section_headers:
            group_cards = groups.get(group_key) or []
            if not group_cards:
                continue
            if header is not None:
                if lines:
                    lines.append("")
                lines.append(header)
            for r in group_cards:
                entry = _fmt_card(r)
                if entry:
                    if header is None and lines and not lines[-1].startswith("- "):
                        lines.append("")
                    lines.append(entry)
            # Ship 25'.b — overflow tail per section. Sum across relation
            # keys because `other` combines context + cross_framework_bridge.
            shown_sum = 0
            total_sum = 0
            for rk in relation_keys:
                oc = overflow_counts.get(rk)
                if not oc:
                    continue
                shown_sum += int(oc.get("shown", 0))
                total_sum += int(oc.get("total", 0))
            if total_sum > shown_sum > 0:
                if primary_ref_for_drill:
                    tail = (
                        f"_Showing {shown_sum} of {total_sum} — "
                        f"see all in the dashboard for {primary_ref_for_drill}._"
                    )
                else:
                    tail = f"_Showing {shown_sum} of {total_sum} — see all in the dashboard._"
                lines.append(tail)

    # Ship 22'.c — risks section replaces the retired
    # `↳ Risk register: R-...` footer.
    risks = list(getattr(structured, "risks", None) or [])
    if risks:
        if lines:
            lines.append("")
        lines.append("## Risks")
        for rk in risks:
            ext = (getattr(rk, "external_ref", "") or "").strip()
            if not ext:
                continue
            threat = (getattr(rk, "threat", "") or "").strip()
            score  = getattr(rk, "risk_score", None)
            treat  = (getattr(rk, "treatment_status", "") or "").strip()
            linked = list(getattr(rk, "linked_controls", None) or [])

            entry = f"- **{ext}**"
            if threat:
                entry += f" — {threat}"
            if score is not None:
                entry += f" — score {score}/25"
            if treat:
                entry += f" — treatment: {treat}"
            if linked:
                entry += f" — linked {', '.join(linked[:6])}"
                if len(linked) > 6:
                    entry += f" (+{len(linked)-6} more)"
            lines.append(entry)

    return "\n".join(lines).rstrip()


# ── Ship 20'.b — helper to build intro-only structured payload ──────

def build_intro_only_structured(
    answer_text: str,
    *,
    primary_ref: str = None,
) -> StructuredAnswer:
    """Family A helper — intro-only structured payload.

    Used by short-circuit paths that carry no cited_refs (clarify
    questions, scope-N/A summaries, cascade prose reports, upload-
    status answers). Frontend renders as a single intro bubble;
    consistent with LLM-path envelope so clients don't branch on
    presence/absence of structured payload.
    """
    return StructuredAnswer(
        intro   = IntroCard(text=answer_text or "", primary_ref=primary_ref),
        actions = [],
        related = [],
    )


# ── Ship 20'.c — helpers for Family B/C (intro + related cards) ─────

def _reindex_posture_by_ref(posture_by_node_id: dict) -> dict:
    """Convert `{node_id: {finding, control_ref, ...}}` (as passed to
    the graph node) into `{control_ref: rec}` for CaseFileShim.

    Last ref wins on collision (matches CaseFile.posture_by_ref)."""
    from rag.id_types import ref_of
    out: dict = {}
    for nid, rec in (posture_by_node_id or {}).items():
        ref = (rec or {}).get("control_ref") or ref_of(nid)
        if ref:
            out[ref] = rec
    return out


def fetch_control_metadata(refs) -> dict:
    """Return `{ref: {"title": str, "standard_id": str}}` for the given
    refs by querying Neo4j `RequirementNode`. Fails silently → returns
    partial or empty dict.

    Used by short-circuit paths to populate title + standard_id on
    RelatedCard when the shim has no resolver-provided nodes.
    """
    if not refs:
        return {}
    try:
        from rag.posture.advisory import _get_neo_driver
        driver = _get_neo_driver()
        if driver is None:
            return {}
        wanted = [r for r in refs if r]
        if not wanted:
            return {}
        with driver.session() as session:
            rows = session.run(
                """
                MATCH (rn:RequirementNode)
                WHERE rn.ref IN $refs
                RETURN rn.ref          AS ref,
                       rn.title        AS title,
                       rn.standard_id  AS standard_id
                """,
                refs=wanted,
            ).data()
        out: dict = {}
        for row in rows:
            ref = row.get("ref")
            if not ref or ref in out:
                continue
            out[ref] = {
                "title":       row.get("title") or "",
                "standard_id": row.get("standard_id") or "",
            }
        return out
    except Exception as e:
        _LOG.debug("fetch_control_metadata failed: %s", e)
        return {}


def build_short_circuit_structured(
    intro_text: str,
    *,
    primary_ref: str = None,
    extra_refs: list = None,
    tenant = None,
    posture_by_node_id: dict = None,
    pg_conn = None,
    tenant_id: str = "",
    risks_data: list = None,
    documents_data: list = None,   # Ship 52'.b
) -> StructuredAnswer:
    """Family B/C helper — intro + related cards for short-circuits.

    Union of `primary_ref` + `extra_refs` becomes the set of refs
    that get RelatedCard entries. For each ref:
      - Look up standard_id + title from Neo4j (batched, one call)
      - Read posture from the reindexed posture dict
      - Build role/verdict/relation via CaseFileShim + build_related_cards
      - Fetch per-leaf evidence_summary / still_needed / leaves
        via advisory (same path as LLM-path augment)

    intro_text is passed through unchanged as intro.text (short-
    circuits already have their own composed prose).
    """
    # Ship 45'.b — OTel span. This function is a suspect for the
    # 7s post-resolver latency in retrieve (Ship 44'.d hunt).
    from rag.telemetry import get_tracer as _gt
    _tracer_sc = _gt(__name__)
    _sc_cm = _tracer_sc.start_as_current_span(
        "arion.answer_augment.build_short_circuit_structured"
    )
    _sc_span = _sc_cm.__enter__()
    try:
        _sc_span.set_attribute("arion.answer.n_extra_refs",
                                len(extra_refs or []))
        _sc_span.set_attribute("arion.answer.has_primary_ref",
                                bool(primary_ref))
    except Exception:
        pass

    all_refs: list = []
    seen: set = set()
    for r in ([primary_ref] if primary_ref else []) + list(extra_refs or []):
        if r and r not in seen:
            seen.add(r)
            all_refs.append(r)

    node_lookup = fetch_control_metadata(all_refs) if all_refs else {}

    posture_by_ref = _reindex_posture_by_ref(posture_by_node_id or {})
    shim = CaseFileShim(
        tenant         = tenant,
        posture_by_ref = posture_by_ref,
        node_lookup    = node_lookup,
    )

    # Skeleton with EMPTY intro.text so build_related_cards's
    # collect_all_refs scan doesn't pick up refs mentioned in the
    # composed short-circuit prose. Short-circuits are authoritative
    # about which refs to surface — the caller has already decided
    # (via primary_ref + extra_refs) which controls become cards.
    # Otherwise a Stage-1 list_queue prose that mentions 42 controls
    # by ref would produce 42 cards, blowing past the caller's cap.
    # The real intro.text is restored below after augmentation.
    skeleton = StructuredAnswer(
        intro   = IntroCard(text="", primary_ref=primary_ref),
        actions = [],
        related = [],
    )

    # Open a short-lived pg connection for advisory data (evidence_summary
    # / still_needed / leaves) when the caller didn't pass one. Mirrors
    # the LLM-path augment flow. Best-effort — augment runs with
    # pg_conn=None on connect failure.
    _own_conn = None
    if pg_conn is None and tenant_id and all_refs:
        try:
            import os as _os, psycopg2 as _pg2
            _own_conn = _pg2.connect(
                host     = _os.getenv("PGHOST",     "127.0.0.1"),
                dbname   = _os.getenv("PGDATABASE", "arioncomply_compliance"),
                user     = _os.getenv("PGUSER",     "arioncomply_app"),
                password = _os.getenv("PGPASSWORD", ""),
            )
            with _own_conn.cursor() as _cur:
                _cur.execute(
                    "SELECT set_config('app.tenant_id', %s, TRUE)",
                    (tenant_id,),
                )
            pg_conn = _own_conn
        except Exception as _ce:
            _LOG.debug(
                "short-circuit augment pg connect failed (evidence detail skipped): %s",
                _ce,
            )

    try:
        related = build_related_cards(
            shim,
            skeleton,
            pg_conn    = pg_conn,
            tenant_id  = tenant_id,
            extra_refs = all_refs,
        )
        skeleton.related = related
    finally:
        if _own_conn is not None:
            try: _own_conn.close()
            except Exception: pass
    # Restore the real intro text now that ref-scanning is done.
    skeleton.intro.text = intro_text or ""

    # Ship 22'.c — attach risk cards when the caller supplied them
    # (typically the risk short-circuit at arion_graph.py:2454).
    if risks_data:
        skeleton.risks = build_risk_cards(risks_data)

    # Ship 52'.b — attach document cards when the caller supplied
    # them (doc_inventory short-circuit at arion_graph.py:2637).
    # Same shape as `risks_data` — a list of pre-shaped dicts;
    # build_document_cards converts each into a DocumentCard.
    if documents_data:
        skeleton.documents = build_document_cards(documents_data)

    try:
        _sc_span.set_attribute("arion.answer.n_related_cards",
                                len(skeleton.related or []))
    except Exception:
        pass
    try: _sc_cm.__exit__(None, None, None)
    except Exception: pass

    return skeleton


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
    """Human-readable label for the relation slug. Delegates to
    `_relation_display_for` — Ship 23'.c added role-aware slugs
    (program / extension / obligation) so the frontend + prose can
    group by role section."""
    return _relation_display_for(relation)


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
    primary_ref + the set of demonstrators of the primary.

    Ship 23'.c: added role-aware slugs (`program` / `extension` /
    `obligation`) so the frontend + prose can group by role section.
    """
    if primary_ref and ref == primary_ref:
        return "primary"

    # Ship 23'.c — classify by role first (both for demonstrators and
    # generic cross-standard neighbors). The legacy `demonstrated_by`
    # label collapsed programs + extensions into one bucket; the
    # role-grouped surface wants them split.
    ref_title, ref_sid = _node_metadata(cf, ref)
    primary_sid = ""
    if primary_ref:
        _, primary_sid = _node_metadata(cf, primary_ref)
    is_cross_standard = bool(primary_sid and ref_sid and primary_sid != ref_sid)
    is_demonstrator   = ref in demonstrated_by_primary

    # ISMS management-system clauses look like 4.x / 5.x / ... / 10.x
    # (no A. prefix, no Art. prefix). Applies within the same standard
    # (both refs are ISO 27001); cross-standard ISMS clauses still
    # exist as programs in the role model.
    if not is_cross_standard and re.match(r"^\d+\.\d+(?:\.\d+)?$", ref):
        return "isms_clause"

    if is_cross_standard or is_demonstrator:
        # Look up the role of the ref's standard — the frontend
        # groups by these buckets: Programs / Extensions / Obligations.
        role = cf.role_of(ref) or ""
        if role == "program":
            return "program"
        if role == "extension":
            return "extension"
        if role == "obligation":
            return "obligation"
        return "cross_framework_bridge"

    # Same-standard sub-articles or in-family relatives
    return "context"


def _relation_display_for(relation: str) -> str:
    """Human-readable label displayed on the card. Extended in
    Ship 23'.c with role-aware labels."""
    return {
        "primary":                "Primary control",
        "demonstrated_by":        "Demonstrates this obligation",
        "cross_framework_bridge": "Cross-framework link",
        "isms_clause":            "Management-system clause",
        "context":                "Related control",
        # Ship 23'.c — role-aware section labels
        "program":                "Program (implementing standard)",
        "extension":              "Extension (privacy overlay)",
        "obligation":             "Obligation (legal/regulatory)",
    }.get(relation, "Related control")


def fetch_cross_role_neighbors(refs) -> list[dict]:
    """Ship 23'.c — return every cross-standard neighbor of the given refs.

    Deterministic Neo4j fetch — no LLM emission. Returns rows shaped:
      { source_ref, neighbor_ref, neighbor_standard_id, neighbor_title,
        edge_type, direction }

    direction is "outbound" (this ref → neighbor) or "inbound"
    (neighbor → this ref). Both directions matter because SUPPORTS
    is authored one-way (ext → program) but the program query wants
    to see extensions extending IT (inbound direction).

    Silent-fail → returns [] on any error.
    """
    if not refs:
        return []
    try:
        from rag.posture.advisory import _get_neo_driver
        driver = _get_neo_driver()
        if driver is None:
            return []
        wanted = [r for r in refs if r]
        if not wanted:
            return []
        with driver.session() as session:
            rows = session.run(
                """
                MATCH (a:RequirementNode)-[r:DEMONSTRATES|IMPLEMENTS|SUPPORTS|GOVERNANCE]-(b:RequirementNode)
                WHERE a.ref IN $refs
                  AND a.standard_id <> b.standard_id
                RETURN a.ref               AS source_ref,
                       b.ref               AS neighbor_ref,
                       b.standard_id       AS neighbor_standard_id,
                       b.title             AS neighbor_title,
                       type(r)             AS edge_type,
                       startNode(r).ref    AS start_ref
                """,
                refs=wanted,
            ).data()
        out: list[dict] = []
        for row in rows:
            src = row.get("source_ref")
            direction = ("outbound" if row.get("start_ref") == src
                         else "inbound")
            out.append({
                "source_ref":           src,
                "neighbor_ref":         row.get("neighbor_ref"),
                "neighbor_standard_id": row.get("neighbor_standard_id"),
                "neighbor_title":       row.get("neighbor_title") or "",
                "edge_type":            row.get("edge_type"),
                "direction":            direction,
            })
        return out
    except Exception as e:
        _LOG.debug("fetch_cross_role_neighbors failed: %s", e)
        return []


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
    *,
    prebuilt_advisory: Optional[dict] = None,
) -> tuple[str, list[str], list[LeafState]]:
    """Return (summary_text, still_needed_names, leaves) for a related card.

    Ship 19'.b — extended to return per-leaf state so the primary
    card can render a ✓/○ checklist. leaves[] populated for ALL
    cards; frontend decides render granularity (primary only, in
    Ship 19'.c).

    Ship 45'.c — accepts `prebuilt_advisory` from a batched
    `build_advisory_data_for_refs` call to avoid the per-ref N+1.
    Falls back to per-ref lookup for backward compatibility.

    Only queries advisory for NC/OFI verdicts on non-empty standards.
    Fails silently on any error → returns ('', [], [])."""
    if verdict not in ("NC", "OFI"):
        return "", [], []
    if not (pg_conn and tenant_id and standard_id and ref):
        return "", [], []

    data = prebuilt_advisory
    if data is None:
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
        # Ship 60'.i — roll up bridge attribution from must_items[]
        # for the SPA nudge. Same idiom as renderBridgeChip in the
        # SPA; kept local so LeafState remains self-contained.
        n_bridged = int(leaf.get("n_bridged") or 0)
        bridge_stds: list[str] = []
        if n_bridged:
            _seen: set[str] = set()
            for m in leaf.get("must_items") or []:
                if m.get("satisfied"):
                    continue
                for b in m.get("bridge_sources") or []:
                    sid = b.get("source_standard_id") or ""
                    if not sid or sid in _seen:
                        continue
                    _seen.add(sid)
                    # humanize inline (avoid the async output-gateway
                    # import in this hot path).
                    if sid.startswith("ISO27001"):
                        bridge_stds.append("ISO 27001" + sid[8:])
                    elif sid.startswith("ISO27701"):
                        bridge_stds.append("ISO 27701" + sid[8:])
                    elif sid.startswith("GDPR"):
                        bridge_stds.append("GDPR")
                    else:
                        bridge_stds.append(sid)
            bridge_stds.sort()
        leaves.append(LeafState(
            leaf_id             = leaf.get("leaf_id") or "",
            title               = label,
            evidence_type       = leaf.get("evidence_type") or "",
            evidence_type_label = leaf.get("evidence_type_label") or "",
            satisfied           = satisfied,
            n_have              = int(leaf.get("n_have") or 0),
            n_total             = int(leaf.get("n_total") or 0),
            n_bridged           = n_bridged,
            bridge_stds         = bridge_stds,
        ))
        if not satisfied:
            still.append(label)

    return summary, still[:6], leaves


# ── Ship 25'.b — per-role fanout cap ────────────────────────────────
#
# Ship 24's coverage completion made Art.32 surface 55 cross-role
# cards (48 Programs alone). The role-grouped surface (Ship 23'.c)
# needs a cap to stay useful on high-fanout obligations + broad
# programs.

_CROSS_ROLE_SECTION_CAP = 8

# Verdict severity — auditor triage first, settled states last.
_VERDICT_SEVERITY = {
    "NC":      0,
    "OFI":     1,
    "Comply":  2,
    "N/A":     3,
    "Unknown": 4,
}

# Role sections subject to the cap. Primary is NEVER capped.
_CAPPABLE_RELATIONS = {
    "program", "extension", "obligation",
    "demonstrated_by",       # legacy label — same section as program/extension
    "cross_framework_bridge",
    "isms_clause",
    "context",
}


def _rank_key(card, fanout_map: dict) -> tuple:
    """Deterministic ranking key for cross-role cards.

    Order (highest priority first):
      1. Verdict severity — NC > OFI > Comply > N/A > Unknown
      2. DRAFT flag — draft ranked higher than confirmed
      3. Fanout centrality — cards with more cross-role edges
      4. Ref — alphabetical tie-breaker
    """
    verdict  = getattr(card, "verdict", "") or "Unknown"
    draft    = bool(getattr(card, "draft", False))
    ref      = getattr(card, "ref", "") or ""
    fanout   = fanout_map.get(ref, 0)
    return (
        _VERDICT_SEVERITY.get(verdict, 5),
        0 if draft else 1,          # draft first → 0 before 1
        -fanout,                    # higher fanout → lower key
        ref,
    )


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
    # Ship 45'.b — trace this function; it does per-ref Neo4j +
    # Postgres lookups that may be N+1.
    from rag.telemetry import get_tracer as _gt_rc
    _tr_rc = _gt_rc(__name__)
    _rc_cm = _tr_rc.start_as_current_span("arion.answer_augment.build_related_cards")
    _rc_span = _rc_cm.__enter__()
    try:
        _rc_span.set_attribute("arion.answer.n_extra_refs",
                                len(extra_refs or []))
    except Exception:
        pass

    cited = collect_all_refs(structured)
    extras = list(extra_refs or [])
    all_refs: list[str] = []
    seen: set[str] = set()
    for r in cited + extras:
        if r and r not in seen:
            seen.add(r)
            all_refs.append(r)

    # Ship 23'.c — normalize primary_ref before use. The LLM
    # sometimes emits variants like "GDPR Art. 32" instead of the
    # canonical "Art.32"; without normalization, primary_ref
    # doesn't match any known ref and the card classifier can't
    # look up its standard_id, causing every cross-role card to
    # fall through to "context".
    raw_primary = structured.intro.primary_ref
    normalized  = _refs_in(raw_primary) if raw_primary else []
    primary_ref = (normalized[0] if normalized else None) or (cited[0] if cited else None)
    # Store the normalised form back on the intro so downstream
    # consumers (frontend chip, SDK) see the canonical form.
    if primary_ref and structured.intro.primary_ref != primary_ref:
        structured.intro.primary_ref = primary_ref

    demonstrators = _collect_demonstrators(cf, primary_ref)

    # Ship 22'.d — auto-inject obligation demonstrators as cards.
    # When ANY cited obligation ref (GDPR Art.5 / Art.32 / NIS2 /
    # DORA article, including sub-articles like Art.32.1.d whose
    # parents carry the DEMONSTRATED_BY overlay) has DEMONSTRATED_BY
    # relationships, pull the implementing controls in as cards even
    # if the LLM didn't cite them in prose. Mirrors the retired
    # ↳ Bridges to footer's guarantee that ISO bridge refs surface
    # on cross-framework queries.
    #
    # We iterate all cited refs (not just primary_ref) because the
    # LLM may prose-cite a sub-article first, making primary_ref =
    # Art.32.1.d — but the demonstrated_by overlay lives on Art.32.
    # `_collect_demonstrators` handles the None/unknown case gracefully.
    all_demonstrators = set(demonstrators)
    for ref in list(cited):
        for dref in _collect_demonstrators(cf, ref):
            all_demonstrators.add(dref)
    for dref in sorted(all_demonstrators):
        if dref and dref not in seen:
            seen.add(dref)
            all_refs.append(dref)

    # Ship 23'.c — auto-inject cross-role neighbors for every cited
    # ref (program → extensions; extension → parent programs;
    # obligation → programs + extensions demonstrating it). The
    # deterministic Neo4j traversal via fetch_cross_role_neighbors
    # covers the directions the DEMONSTRATED_BY overlay doesn't
    # (e.g. SUPPORTS: 27701 → 27001 inbound direction when the
    # primary is a program). Without this, a program query only
    # shows its own primary card + demonstrated_by obligations —
    # no extensions.
    cross_role_ns = fetch_cross_role_neighbors(list(cited))
    ns_titles: dict[str, str] = {}
    ns_sids:   dict[str, str] = {}
    for row in cross_role_ns:
        nref = row.get("neighbor_ref")
        if not nref or nref in seen:
            continue
        seen.add(nref)
        all_refs.append(nref)
        # Cache title + standard_id so the card render below can use
        # them without another lookup (short-circuit CaseFileShim
        # doesn't have these controls in its node_lookup).
        if nref not in ns_titles and (row.get("neighbor_title") or "").strip():
            ns_titles[nref] = row["neighbor_title"]
        if nref not in ns_sids and (row.get("neighbor_standard_id") or "").strip():
            ns_sids[nref]   = row["neighbor_standard_id"]

    # Ship 45'.c — batch-precompute advisory data for all NC/OFI refs
    # before the card loop. Was N+1: each _evidence_summary call built
    # a fresh EvalContext + Neo4j session + spec resolver. Now built
    # once + reused for every ref.
    _refs_by_std_for_batch: list[tuple[str, str]] = []
    _seen_batch: set[tuple[str, str]] = set()
    for _ref in all_refs:
        _t, _s = _node_metadata(cf, _ref)
        if not _s and _ref in ns_sids: _s = ns_sids[_ref]
        if not _s: continue
        _p = cf.posture_for(_ref) or {}
        _v = _norm_verdict(_p.get("finding") or "")
        if _v not in ("NC", "OFI"): continue
        _key = (_ref, _s)
        if _key in _seen_batch: continue
        _seen_batch.add(_key)
        _refs_by_std_for_batch.append(_key)
    _advisory_batch: dict[str, dict] = {}
    if _refs_by_std_for_batch and pg_conn is not None and tenant_id:
        try:
            from rag.posture.advisory import build_advisory_data_for_refs
            _advisory_batch = build_advisory_data_for_refs(
                pg_conn     = pg_conn,
                tenant_id   = tenant_id,
                refs_by_std = _refs_by_std_for_batch,
            ) or {}
        except Exception as _e:
            _LOG.debug("build_advisory_data_for_refs failed: %s", _e)

    cards: list[RelatedCard] = []
    for ref in all_refs:
        title, sid = _node_metadata(cf, ref)

        # Ship 23'.c — fall back to the cross-role-neighbor fetch's
        # inline title + standard_id when _node_metadata returned
        # empty (short-circuit CaseFileShim path with no resolver
        # nodes, or LLM path where the ref wasn't in graph_nodes).
        if not title and ref in ns_titles:
            title = ns_titles[ref]
        if not sid and ref in ns_sids:
            sid = ns_sids[ref]

        # Skip refs we can't identify at all — no title, no standard.
        # Prevents surfacing arbitrary numeric strings.
        if not title and not sid:
            continue

        posture = cf.posture_for(ref) or {}
        verdict = _norm_verdict(posture.get("finding") or "")
        draft   = cf.needs_draft_tag(ref)
        role    = cf.role_of(ref) or "unknown"

        relation = _classify_relation(cf, ref, primary_ref, demonstrators)
        summary, still, leaves = _evidence_summary(
            pg_conn, tenant_id, ref, sid, verdict,
            prebuilt_advisory = _advisory_batch.get(ref),
        )

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

    # Sort: primary first, then by role-group order (Ship 23'.c).
    # Program → Extension → Obligation is the auditor's mental model:
    #   "here's the primary control, here are the programs that
    #   implement / are implemented by it, here are the privacy
    #   extensions on top, here are the legal obligations."
    # cross_framework_bridge stays as a fallback for cards whose
    # role_of() couldn't resolve (should be rare post Ship 23'.b).
    _ORDER = {
        "primary":                0,
        "program":                1,
        "extension":              2,
        "obligation":             3,
        "demonstrated_by":        4,   # legacy — same bucket as programs/extensions
        "cross_framework_bridge": 5,
        "isms_clause":            6,
        "context":                7,
    }

    # Ship 25'.b — per-role cap with deterministic ranking.
    # Group cards by relation, rank each group by
    # (verdict severity, DRAFT, fanout, ref), cap at
    # _CROSS_ROLE_SECTION_CAP, and track {shown, total} per role
    # on the structured payload so the frontend + prose render an
    # overflow tail.
    #
    # Build a fanout map: how many cross-role neighbors did the
    # audit surface for each ref? Cards with higher fanout are more
    # "central" in the graph and rise to the top within their group
    # after verdict + draft sorting.
    fanout_map: dict = {}
    for row in cross_role_ns:
        nref = row.get("neighbor_ref")
        if nref:
            fanout_map[nref] = fanout_map.get(nref, 0) + 1

    # Group cards by relation, keeping insertion order within each
    # group for stability during ranking ties.
    _by_relation: dict = {}
    for c in cards:
        _by_relation.setdefault(c.relation, []).append(c)

    capped_cards: list[RelatedCard] = []
    overflow: dict = {}
    for rel in sorted(_by_relation.keys(), key=lambda r: _ORDER.get(r, 9)):
        group = _by_relation[rel]
        if rel == "primary" or rel not in _CAPPABLE_RELATIONS:
            # Primary always kept whole (never > 1); non-cappable
            # relations (should be empty post-Ship-23'.c) also pass
            # through.
            capped_cards.extend(group)
            continue
        # Rank + cap
        ranked = sorted(group, key=lambda c: _rank_key(c, fanout_map))
        total = len(ranked)
        shown = ranked[:_CROSS_ROLE_SECTION_CAP]
        capped_cards.extend(shown)
        if total > _CROSS_ROLE_SECTION_CAP:
            overflow[rel] = {"shown": len(shown), "total": total}

    # Attach overflow signal to the structured payload for downstream
    # rendering. Frontend + prose consume this to emit the tail.
    if overflow:
        structured.overflow_counts = overflow

    # Now that we've done any ordering, fill each action card's `refs`
    # so the UI can render chips consistent with related-card presence.
    known_refs = {c.ref for c in capped_cards}
    for action in structured.actions:
        action.refs = [r for r in action.refs if r in known_refs]

    try:
        _rc_span.set_attribute("arion.answer.n_capped_cards", len(capped_cards))
    except Exception:
        pass
    try: _rc_cm.__exit__(None, None, None)
    except Exception: pass

    return capped_cards


# ── Ship 22'.c — risk-card builder ──────────────────────────────────

def build_risk_cards(risks_data) -> list[RiskCard]:
    """Deterministic conversion of `CaseFile.risks[]` (or the same
    dict list from `fetch_risks_for_casefile`) into RiskCard[].

    Every field derives from the tenant's risk-register row; no LLM
    emission surface. Silent-fail per row on unexpected shape."""
    from urllib.parse import quote
    out: list[RiskCard] = []
    for entry in (risks_data or []):
        if not isinstance(entry, dict):
            continue
        ext = (entry.get("external_ref") or "").strip()
        if not ext:
            continue
        # linked_controls is a list of dicts from linked_controls_view;
        # each dict has "ref" + "role" + "subject". Flatten to refs
        # ordered by role (program → extension → obligation) for a
        # scannable card body.
        role_order = {"program": 0, "extension": 1, "obligation": 2}
        linked_raw = list(entry.get("linked_controls") or [])
        linked_sorted = sorted(
            [lc for lc in linked_raw if isinstance(lc, dict)],
            key=lambda lc: (
                role_order.get((lc.get("role") or "").lower(), 99),
                lc.get("ref") or "",
            ),
        )
        linked_refs = [lc.get("ref") for lc in linked_sorted if lc.get("ref")]

        # Dashboard drill-in — routes to /#risks?risk_id=<uuid>
        risk_id = (entry.get("id") or "").strip()
        dash_url = f"/#risks?risk_id={quote(risk_id)}" if risk_id else None

        out.append(RiskCard(
            external_ref        = ext,
            threat              = entry.get("threat") or None,
            vulnerability       = entry.get("vulnerability") or None,
            risk_score          = entry.get("risk_score"),
            residual_risk_level = entry.get("residual_risk_level"),
            treatment_option    = entry.get("treatment_option") or None,
            treatment_status    = entry.get("treatment_status") or None,
            risk_owner_text     = entry.get("risk_owner_text") or None,
            review_date         = entry.get("review_date") or None,
            linked_controls     = linked_refs,
            dashboard_url       = dash_url,
        ))
    return out


def build_document_cards(documents_data) -> list["DocumentCard"]:
    """Ship 52'.b — deterministic conversion of pre-shaped document
    dicts into DocumentCard[].

    Each `documents_data` entry is a dict produced by the doc_inventory
    short-circuit's `_build_documents_data()` helper (in
    rag/arion_graph.py). Fields expected:

      title, external_ref, evidence_type, evidence_type_display,
      uploaded_at, standards (list of {standard_id, standard_display,
      n_refs}), standards_span, total_refs, dashboard_url

    Silent-fail per row on unexpected shape — the doc list should
    survive a single bad row without breaking the whole card render.
    """
    from rag.casefile.answer_schema import DocumentCard, StandardsSummary
    out: list["DocumentCard"] = []
    for entry in (documents_data or []):
        if not isinstance(entry, dict):
            continue
        title = (entry.get("title") or "").strip()
        if not title:
            continue
        try:
            standards = [
                StandardsSummary(
                    standard_id      = s.get("standard_id") or "",
                    standard_display = s.get("standard_display") or "",
                    n_refs           = int(s.get("n_refs") or 0),
                )
                for s in (entry.get("standards") or [])
                if isinstance(s, dict)
            ]
            out.append(DocumentCard(
                title                 = title,
                external_ref          = entry.get("external_ref") or None,
                evidence_type         = entry.get("evidence_type") or "",
                evidence_type_display = entry.get("evidence_type_display") or "",
                uploaded_at           = entry.get("uploaded_at") or None,
                standards             = standards,
                standards_span        = int(entry.get("standards_span") or len(standards)),
                total_refs            = int(entry.get("total_refs") or
                                            sum(s.n_refs for s in standards)),
                dashboard_url         = entry.get("dashboard_url") or None,
            ))
        except Exception:
            # Silent-fail per row — the doc list should survive a
            # single bad row without breaking the whole card render.
            continue
    return out


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

    # Ship 22'.c — attach risk cards from CaseFile.risks (populated by
    # Ship 14'.e for posture_risk queries). Deterministic; every field
    # derives from the risk-register row.
    cf_risks = getattr(cf, "risks", None) or []
    if cf_risks:
        structured.risks = build_risk_cards(cf_risks)

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

    # Ship 22'.c — risk-refs auditor parity. Repair events fire when
    # the LLM's prose dropped a risk external_ref, exactly as the
    # retired risk footer would have surfaced. Structured payload
    # renders every risk as a RiskCard (already attached above); the
    # events log the drop for observability via
    # scripts/audit_retired_footer.sql.
    if spec and getattr(spec, "required_risk_refs", None):
        text_scan = (structured.intro.text or "").lower()
        for a in (structured.actions or []):
            text_scan += " " + (a.title or "").lower()
            text_scan += " " + (a.body  or "").lower()
        for r in (spec.required_risk_refs or []):
            if r and r.lower() not in text_scan:
                events.append({
                    "kind":   "missing_risk_ref",
                    "ref":    r,
                    "detail": f"risk external_ref '{r}' absent from "
                              f"intro/actions — surfaced via RiskCard",
                })

    return structured, events
