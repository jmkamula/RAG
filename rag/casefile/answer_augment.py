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

    # Minimal structured skeleton — LLM path passes StructuredAnswer
    # with intro + actions[]; short-circuits pass an intro-only skeleton
    # and let build_related_cards() populate related[] from extra_refs.
    skeleton = StructuredAnswer(
        intro   = IntroCard(text=intro_text or "", primary_ref=primary_ref),
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
