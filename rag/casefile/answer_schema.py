"""
Structured chat response schema (Ship 18'.a design).

Payload shape returned to the client alongside the prose `answer`:

    StructuredAnswer:
        intro:   IntroCard         # required — 1-2 sentence framing
        actions: list[ActionCard]  # 0..N remediation steps (LLM-authored)
        related: list[RelatedCard] # 0..N cited/derived refs (backend-derived)

The LLM emits ONLY `intro` + `actions` as JSON (via
response_format={"type": "json_object"}). `related[]` is 100%
deterministic — the backend builds it from CaseFile so structural
metadata (role, verdict, relation, evidence_summary) has no
hallucination surface.

See docs/memory/ship_18_prime_a_structured_answer_design_2026_07_23.md.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ── Card models ─────────────────────────────────────────────────────

class IntroCard(BaseModel):
    """Top card — 1-2 sentence framing of the query."""
    text:         str
    primary_ref:  Optional[str] = None       # e.g. "A.5.15"
    primary_role: Optional[str] = None       # program / extension / obligation / guidance


class ActionCard(BaseModel):
    """One remediation step. LLM-authored prose + backend-augmented ref chips."""
    title: str                               # imperative header, ≤80 chars
    body:  str                               # concrete guidance; names items when known
    refs:  list[str] = Field(default_factory=list)  # backend-scanned refs mentioned in title+body


class LeafState(BaseModel):
    """Ship 19'.b — per-leaf state for the primary-card checklist.

    Populated from `build_per_must_advisory_data.leaves`. Rendered
    only on the primary card (`relation == "primary"`); other cards
    keep their compact summary shape.
    """
    leaf_id:              str    # e.g. "req:A.5.15:access_control_policy"
    title:                str    # humanized leaf title (e.g. "Access control policy")
    evidence_type:        str    # raw slug (e.g. "policy") — kept for tooltip
    evidence_type_label:  str    # humanized (e.g. "policy document")
    satisfied:            bool   # True → ✓, False → ○
    n_have:               int    # per-MUST count of satisfied items
    n_total:              int    # per-MUST count of total items


class RelatedCard(BaseModel):
    """One cited / derived control ref. 100% backend-derived from CaseFile."""
    ref:              str
    standard_id:      str
    standard_display: str                    # "ISO 27001:2022" (via gateway)
    title:            str                    # control title from Neo4j
    role:             str                    # program / extension / obligation / guidance / unknown
    verdict:          str                    # NC / OFI / Comply / N/A / Unknown
    draft:            bool = False           # posture unconfirmed
    relation:         str                    # primary / demonstrated_by / cross_framework_bridge / isms_clause / context
    relation_display: str                    # gateway-humanized ("Cross-framework link", etc.)
    evidence_summary: str = ""               # deterministic — "1 of 4 required items present"
    still_needed:     list[str] = Field(default_factory=list)  # item names with no evidence
    leaves:           list[LeafState] = Field(default_factory=list)  # Ship 19'.b — per-leaf checklist
    dashboard_url:    Optional[str] = None   # deep-link to /dashboard drill-in


class RiskCard(BaseModel):
    """Ship 22'.c — one risk-register entry.

    Risks aren't controls: no standard_id / verdict / role / leaves.
    Populated from CaseFile.risks[] (Ship 14'.e — top-8 by risk_score
    for posture_risk queries). Fully deterministic — no LLM emission
    of risk metadata.
    """
    external_ref:      str                            # "R-042"
    threat:            Optional[str] = None           # tenant-authored description
    vulnerability:     Optional[str] = None
    risk_score:        Optional[int] = None           # likelihood * impact, 0-25
    residual_risk_level: Optional[int] = None
    treatment_option:  Optional[str] = None           # "avoid" / "reduce" / "transfer" / "accept"
    treatment_status:  Optional[str] = None           # "in_treatment" / "accepted" / "implemented"
    risk_owner_text:   Optional[str] = None           # display name
    review_date:       Optional[str] = None           # ISO date string
    linked_controls:   list[str] = Field(default_factory=list)  # control refs (ordered by role)
    dashboard_url:     Optional[str] = None           # /#risks?risk_id=<uuid>


class StructuredAnswer(BaseModel):
    """Full structured chat response."""
    intro:   IntroCard
    actions: list[ActionCard] = Field(default_factory=list)
    related: list[RelatedCard] = Field(default_factory=list)
    risks:   list[RiskCard]   = Field(default_factory=list)   # Ship 22'.c
    # Ship 25'.b — per-role overflow signal for capped sections.
    # Shape: `{role: {"shown": int, "total": int}}` for roles where
    # the total exceeded the per-section cap (default 8). Frontend +
    # prose render an `_Showing N of M — open dashboard →_` tail.
    # Empty dict when no section overflowed.
    overflow_counts: dict = Field(default_factory=dict)


# ── LLM JSON schema (for prompt inclusion) ──────────────────────────
#
# What the LLM sees + emits. We deliberately DROP `related[]` from the
# LLM-facing schema — LLM emits only `intro + actions`, backend builds
# `related` deterministically from CaseFile.

LLM_OUTPUT_SCHEMA = """{
  "intro": {
    "text": "string, 1-2 sentences framing the answer",
    "primary_ref": "string, optional — the control ref this query is about (e.g. 'A.5.15')"
  },
  "actions": [
    {
      "title": "string, imperative, <=80 chars",
      "body":  "string, concrete guidance; name specific items when known"
    }
  ]
}"""


LLM_OUTPUT_RULES = """OUTPUT FORMAT
Return a single JSON object with exactly two top-level keys: `intro`
and `actions`. Do NOT emit a `related` array — the backend adds it.

Schema:
""" + LLM_OUTPUT_SCHEMA + """

Card content rules:
1. `intro.text` — 1-2 sentences. MUST directly answer the query's
   central question, echoing the query's key terms (e.g. if the
   query asks "are we certified?" the intro contains
   "certification" / "certified"; if it asks about ISO 27004, the
   intro contains "27004"). Never open with "This response...".
   The ONLY thing you may drop from the digest content is the
   N-of-M item count ("1 of 4 items present" / "0 of 18 required")
   — the primary card renders that as a per-leaf checklist.
   Everything else stays: verdict acronyms (NC, OFI, Comply, DRAFT
   tags), query framing terms, guidance-standard names (see rule
   7), role/framework markers.

   IMPORTANT — use the DIGEST verdict tag verbatim. If the digest
   shows [NC], write "NC" (not "NC-DRAFT"). Only append "-DRAFT"
   when the digest tag itself includes it ([NC-DRAFT] / [OFI-DRAFT]
   / [Comply-DRAFT]). The digest reflects live confirmation status;
   echoing a stale "-DRAFT" suffix contradicts what the tenant sees
   on their dashboard. (Ship 30 fix, 2026-07-25.)

   Examples:
     Digest shows "A.5.15 [OFI-DRAFT] register incomplete",
     query "how do I remediate A.5.15?" →
       "ISO 27001 A.5.15 (Access control) requires authorized
        access to information and assets. Currently OFI-DRAFT."
     Digest shows "B.8.4.1 [NC] no systematic temp-file sweep",
     query "posture on B.8.4.1?" →
       "ISO 27701 B.8.4.1 (Temporary files) requires periodic
        verification that unused temp files are deleted. Currently
        NC — no systematic sweep in place."
     Query "are we certified?" →
       "Arion is currently working toward ISO 27001 certification;
        several controls remain NC and require remediation before
        an external audit can succeed."
     Query "what does ISO 27004 say about monitoring?" →
       "ISO 27004 provides guidance on the monitoring, measurement,
        analysis and evaluation required by ISO 27001 clause 9.1.
        Currently OFI-DRAFT."
2. `intro.primary_ref` — the single ref the query is about, when
   the query targets one specific control. Omit for broad queries.
3. `actions[]` — 0-5 cards. Each card is ONE concrete step.
   - `title`: short imperative ("Complete the register", "Publish
     the policy"). Never a restatement of body.
   - `body`: concrete guidance. When you know specific item names
     from the POSTURE / OBLIGATIONS section, NAME them. Never write
     "1 of 4 required items" without naming which items — the
     tenant needs actionable specifics.
4. For DEFINITION queries → `actions=[]` (empty). The intro carries
   the definition; there's no remediation to take.
5. For POSTURE_STATUS queries → `actions=[]` unless the tenant asks
   for guidance. The intro summarises status; related cards carry
   detail.
6. When you cite a ref in `intro.text` or `action.body`, keep the
   canonical form ("A.5.15", "Art.32", "9.2") — the backend scans
   these to build the related-cards list.
7. GUIDANCE citations MUST appear by full ISO standard name in
   `intro.text` — this rule fires REGARDLESS of how brief the
   intro must otherwise be (rule 1's N-of-M subtraction does NOT
   remove this). When the OBLIGATIONS / GUIDANCE section mentions
   a specific ISO family standard (ISO 27002, ISO 27003, ISO
   27004, ISO 27005, ISO 27701, ISO 27017, ISO 27018, ISO 27552,
   ISO 27799), name it verbatim in the intro — "ISO 27005"
   (not just "the risk-management standard"). Auditors trace the
   guidance path by standard number. When the query itself names
   an ISO standard (e.g. "what does ISO 27004 say about..."), the
   intro MUST echo that standard's name back.
8. LISTING queries — when the user asks "what must X contain",
   "what are the required items", "list the required elements",
   "what should X include": enumerate EVERY item from the
   OBLIGATIONS section (or ≥5 if the section carries more) as a
   NEWLINE-SEPARATED BULLETED LIST inside `intro.text` or a
   single `action.body`. Each item MUST be on its own line
   prefixed with "- " (hyphen space). Do NOT emit them inline as
   a comma-separated sentence — auditors read the bulleted list
   verbatim. The enumeration IS the answer for these queries.
   Example format for `intro.text`:
     "The ISMS scope statement must contain:\n- item one\n- item
      two\n- item three\n- item four\n- item five"

Never emit prose outside the JSON object. Never wrap in markdown
code fences. The response body IS the JSON."""
