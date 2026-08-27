"""
Tenant scope filter — Layer 1 / 2 / 3 defense against out-of-scope
control leakage in LLM answers.

Problem statement: each tenant has controls marked N/A based on their
business model (Arion cloud-only → A.7.x physical N/A; processor-only
company → A.7.2.x Controller-side N/A; etc.). Today's LLM answers can
still mention these controls or their associated concepts because:

  1. Not all context paths filter N/A (retrieval hits, xfw nodes,
     posture summaries may include them)
  2. The system prompt doesn't explicitly enumerate the tenant's
     N/A scope
  3. The LLM can hallucinate references from training even when the
     context is clean

This module provides three complementary layers:

  Layer 1 — get_tenant_na_scope(tenant_id, pg_conn)
    Returns the tenant's active N/A scope from posture_controls:
    {(control_ref, standard_id), ...}. Callers use this to filter
    nodes/hits/posture data before assembling the LLM context.

  Layer 2 — build_scope_instruction(tenant_id, pg_conn, tenant_facts)
    Returns a prompt fragment listing:
      - Tenant scope facts (has_physical_premises, does_software_dev, ...)
      - The N/A control set with "DO NOT enumerate these in answers"
    Injected into the system prompt so the LLM sees the boundaries
    before composing.

  Layer 3 — filter_response_for_scope(response_text, na_refs, query_text)
    Post-composition scrub. Scans the LLM output for mentions of
    N/A refs. If a mention appears in the answer AND the query did
    NOT ask about that ref explicitly, strip the containing sentence.
    Defensive net catching LLM hallucinations that slipped past
    layers 1+2.

    NOTE: this is REF-level filtering only. Concept-word filtering
    (stripping the word "physical" itself when tenant has no
    premises) is a separate, tighter arc — deferred. Layer 3 here
    focuses on the auditable "did the LLM mention control X that
    is N/A for you" case.

All three layers are query-aware: if the tenant explicitly asks
about an N/A control ("why is A.7.4 N/A?"), the filters allow
that ref through with proper scope framing — otherwise scope
explanations become impossible.
"""
from __future__ import annotations
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


# Regex to detect control ref mentions in LLM output. Covers the
# common shapes across ISO 27001, ISO 27701, GDPR:
#   A.5.9 / A.5.18 / A.7.14        27001 Annex A
#   A.7.2.6 / B.8.2.6              27701
#   Art. 32 / Article 30.1         GDPR
#   4.3 / 6.1.2 / 9.2              ISMS clauses
_REF_MENTION_RE = re.compile(
    r"\b(?:"
    r"[AB]\.\d+(?:\.\d+){1,2}"       # A.5.9, A.7.2.6, B.8.2.6
    r"|Art(?:icle)?\.?\s*\d+(?:\.\d+)?"  # Art.32, Article 30.1
    r"|\d\.\d+(?:\.\d+)?"            # 6.1.2, 4.3
    r")\b",
    re.IGNORECASE,
)


def get_tenant_na_scope(tenant_id: str, pg_conn) -> set[str]:
    """Return the set of `control_ref`s the tenant has declared N/A
    (leaf-level, from posture_controls). Empty set on any DB error —
    caller degrades to no scope filtering (safe fallback).

    Note: returns REFS only (not full (ref, std) tuples). ISO 27001
    A.5.9 is the same ref as GDPR Art.5.9 collision-wise only if you
    misread — the LLM's context always carries the standard label
    inline, so ref-level filtering is sufficient in practice.
    """
    if not tenant_id or not pg_conn:
        return set()
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute(
                # Ship 98'.d (2026-08-27) — migrated to Ship 66'.a's
                # SSoT column applicability_status. Data has been kept in
                # sync since Ship 66'.a, so this is a no-op on current
                # tenants, but future-proofs against writers that touch
                # only applicability_status without mirroring to
                # finding. See [[feedback-na-dominance-via-applicability-column]].
                """
                SELECT DISTINCT control_ref
                  FROM posture_controls
                 WHERE tenant_id            = %s::uuid
                   AND applicability_status = 'na'
                   AND is_active            = TRUE
                """,
                (tenant_id,),
            )
            return {r[0] for r in cur.fetchall() if r[0]}
    except Exception as e:
        logger.warning("get_tenant_na_scope failed: %s", e)
        return set()


def get_tenant_scope_facts(tenant_id: str, pg_conn) -> dict:
    """Return a compact dict of tenant scope facts useful for the
    system prompt: has_physical_premises, does_software_development,
    processes_personal_data, employee_count, sector. Silent
    fallback returns {} on error."""
    if not tenant_id or not pg_conn:
        return {}
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute(
                """
                SELECT t.has_physical_premises,
                       t.does_software_development,
                       t.industry,
                       t.employee_count,
                       cf.processes_personal_data,
                       cf.role_controller,
                       cf.role_processor,
                       cf.uses_processors
                  FROM tenants t
                  LEFT JOIN client_facts cf ON cf.tenant_id = t.id
                 WHERE t.id = %s::uuid
                """,
                (tenant_id,),
            )
            row = cur.fetchone()
            if not row:
                return {}
            return {
                "has_physical_premises":     row[0],
                "does_software_development": row[1],
                "industry":                  row[2],
                "employee_count":            row[3],
                "processes_personal_data":   row[4],
                "role_controller":           row[5],
                "role_processor":            row[6],
                "uses_processors":           row[7],
            }
    except Exception as e:
        logger.warning("get_tenant_scope_facts failed: %s", e)
        return {}


def build_scope_instruction(
    na_refs:     set[str],
    scope_facts: dict,
) -> str:
    """Compose a prompt fragment injected into the system prompt.
    Enumerates tenant scope facts + the full N/A control list with
    explicit "DO NOT enumerate these" instruction.

    Returns empty string when both inputs are empty — no scope block
    added to prompt in that case (backward compatible).
    """
    if not na_refs and not scope_facts:
        return ""

    lines: list[str] = []
    lines.append("TENANT SCOPE — READ CAREFULLY:")

    # Facts block — the concrete business shape
    if scope_facts:
        facts_lines: list[str] = []
        if scope_facts.get("has_physical_premises") is False:
            facts_lines.append(
                "  - This tenant has NO physical premises (cloud-only). "
                "Do NOT recommend physical access controls, facility "
                "security, on-site monitoring, or premises-management "
                "actions — they are structurally inapplicable."
            )
        if scope_facts.get("does_software_development") is False:
            facts_lines.append(
                "  - This tenant does NO software development. Do NOT "
                "recommend SDLC controls, secure coding practices, "
                "development environment segregation, or dev-team "
                "actions — they are structurally inapplicable."
            )
        if scope_facts.get("processes_personal_data") is False:
            facts_lines.append(
                "  - This tenant does NOT process personal data. GDPR "
                "and ISO 27701 controls are largely inapplicable — do "
                "NOT recommend privacy operational controls."
            )
        if scope_facts.get("role_processor") and not scope_facts.get("role_controller"):
            facts_lines.append(
                "  - This tenant acts ONLY as a Processor. Do NOT "
                "recommend Controller-side obligations (data subject "
                "notice authoring, consent obtaining, DSAR handling as "
                "primary controller — those are the customer's role)."
            )
        if facts_lines:
            lines.append("Business shape:")
            lines.extend(facts_lines)

    # N/A control list — the auditable exclusion set
    if na_refs:
        sorted_refs = sorted(na_refs)
        # Compact — comma-separated inline for prompt-token efficiency
        refs_str = ", ".join(sorted_refs)
        lines.append(
            f"Controls marked N/A (out of scope for this tenant, do NOT "
            f"enumerate as gaps or recommend remediation for these): "
            f"{refs_str}"
        )
        lines.append(
            "EXCEPTION: if the user's query explicitly names one of "
            "these refs OR asks about scope/why-N/A, you MAY reference "
            "the control — but frame it as N/A/scoped-out, NOT as a gap."
        )

    return "\n".join(lines) + "\n"


def _sentence_split(text: str) -> list[str]:
    """Very conservative sentence split. Preserves bullet-list
    boundaries. Not aiming for NLP perfection — just something that
    lets Layer 3 strip whole sentences containing forbidden refs.
    """
    # Split on newlines that look like new bullets/paragraphs,
    # plus period-space boundaries.
    parts = re.split(r"(?:\n\s*-\s+|\n\s*\d+\.\s+|\n\n|\.\s+(?=[A-Z]))", text)
    return [p for p in parts if p.strip()]


def filter_response_for_scope(
    response_text: str,
    na_refs:       set[str],
    query_text:    str,
) -> tuple[str, list[str]]:
    """Layer 3 — scan the LLM's answer for mentions of N/A refs.
    Strip whole sentences containing a forbidden ref UNLESS the
    ref appears verbatim in the user's query (query-aware exception).

    Returns (filtered_text, stripped_refs) — stripped_refs is the
    list of N/A control_refs that were removed, for logging /
    telemetry.

    Behaviour:
      - Empty na_refs → return text unchanged.
      - Ref in query_text → keep sentence (user asked about it).
      - Ref in text but not in query → drop that sentence.
      - Text without any refs → unchanged.

    Conservative: only strips SENTENCES containing forbidden refs.
    Doesn't touch surrounding markdown formatting. If the whole
    answer collapses to <100 chars after stripping, returns the
    ORIGINAL (better to be verbose than to render an empty answer).
    """
    if not response_text or not na_refs:
        return response_text, []

    # Refs that the user explicitly asked about — those are allowed
    query_refs: set[str] = set()
    for m in _REF_MENTION_RE.finditer(query_text or ""):
        query_refs.add(m.group(0).replace(" ", "").replace("Article", "Art.").upper())

    def _normalise(ref: str) -> str:
        return ref.replace(" ", "").replace("Article", "Art.").upper()

    query_refs_norm = {_normalise(r) for r in query_refs}
    na_norm = {_normalise(r) for r in na_refs}

    sentences = _sentence_split(response_text)
    kept: list[str] = []
    stripped: list[str] = []
    for s in sentences:
        s_refs = {_normalise(m.group(0)) for m in _REF_MENTION_RE.finditer(s)}
        # A sentence is offending if it mentions an N/A ref that
        # the user did NOT ask about
        offending = (s_refs & na_norm) - query_refs_norm
        if offending:
            stripped.extend(sorted(offending))
            continue
        kept.append(s)

    result = "\n\n".join(kept).strip()
    # Safety: if scrubbing collapsed the answer, keep the original
    # verbose one — better to leak than to serve garbage.
    if len(result) < 100 and len(response_text) >= 100:
        return response_text, []
    return result, sorted(set(stripped))
