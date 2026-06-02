"""ArionComply — chat surface for acknowledging engine-detected gaps.

Recognises queries like:
  "acknowledge the A.5.1 review record gap because we conduct reviews offline"
  "ack A.5.1 communication record"
  "mark A.5.1 approval as acknowledged — signed offline, scanned to drive"
  "acknowledge the policy gap for A.5.23 — covered by AWS attestation"

Slot-fills (control_ref, role, rationale) and writes status='acknowledged'
on the matching tenant_evidence_gaps row. Returns a deterministic
confirmation answer; on no-match returns None so the regular pipeline
handles the query.

Per [[human_in_the_loop_positioning]]: acknowledging a gap suppresses it
from the headline but does NOT flip the verdict to Comply — posture
ownership stays with the client via a separate posture_controls override
(or, eventually, an explicit "mark control Comply" surface).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# ── Slot grammar ──────────────────────────────────────────────────────────────
# Trigger verbs: ack / acknowledge / dismiss / mark ... acknowledged
_TRIGGER_RE = re.compile(
    r"\b(?:ack(?:nowledge)?|dismiss|mark\s+(?:as\s+)?(?:acknowledged|known))\b",
    re.IGNORECASE,
)

# Control reference: A.5.1, A.8.19, 5.2, 9.2, Art.32, Art.32.1.a
_CONTROL_RE = re.compile(
    r"\b("
    r"A\.\d+(?:\.\d+)*"
    r"|Art\.\d+(?:\.\d+[a-z]?)*"
    r"|\d+\.\d+(?:\.\d+)?"   # ISMS clauses 4.1 … 10.2 — \d+ so '10.x' matches
    r")\b",
)

# Role vocabulary — the roles the engine currently emits. Match either with
# space or underscore, case-insensitive. Order matters: longer patterns first
# so "review record" wins over "record" alone.
_ROLE_ALIASES = [
    ("review_record",        r"review[\s_-]?records?"),
    ("communication_record", r"communication[\s_-]?records?"),
    ("attestation_record",   r"attestation[\s_-]?records?"),
    ("register_entry",       r"register[\s_-]?(?:entry|entries)"),
    ("drill_record",         r"drill[\s_-]?records?"),
    ("approval",             r"approval(?:s)?"),
    ("policy",               r"polic(?:y|ies)"),
    ("procedure",            r"procedures?"),
    ("dpa",                  r"dpa|data\s+processing\s+agreement"),
    ("scope_statement",      r"scope\s+statement"),
    ("privacy_notice",       r"privacy\s+notice"),
    ("dsar_response",        r"dsar(?:\s+response)?"),
    ("records_of_processing", r"records?\s+of\s+processing|ropa"),
    ("breach_notification",  r"breach\s+notification"),
    ("risk_assessment",      r"risk\s+assessment"),
    ("risk_treatment_plan",  r"risk\s+treatment\s+plan"),
    ("audit_programme",      r"audit\s+programme|audit\s+program"),
    ("management_review_minutes", r"management\s+review(?:\s+minutes)?"),
]
_ROLE_RE = re.compile(
    r"\b(" + "|".join(p for _, p in _ROLE_ALIASES) + r")\b",
    re.IGNORECASE,
)
_ROLE_ALIAS_LOOKUP: list[tuple[str, re.Pattern]] = [
    (role, re.compile(pat, re.IGNORECASE)) for role, pat in _ROLE_ALIASES
]

# Optional rationale clause: "because ...", "since ...", "— ...", "- ..."
_RATIONALE_RE = re.compile(
    r"(?:\bbecause\b|\bsince\b|\breason:?\b|—|-)\s*(?P<reason>.+?)\s*\.?\s*$",
    re.IGNORECASE,
)


@dataclass
class AcknowledgeIntent:
    control_ref: str        # e.g. "A.5.1"
    role:        str        # e.g. "review_record"
    rationale:   str        # may be empty
    raw_query:   str


def parse_acknowledge_intent(query: str) -> Optional[AcknowledgeIntent]:
    """Returns an AcknowledgeIntent if the query is recognisably an ack
    request, else None. Conservative: requires all three of (trigger verb,
    control ref, role) — anything weaker would risk firing on innocuous
    'we acknowledge access rights' style prose."""
    if not query:
        return None
    if not _TRIGGER_RE.search(query):
        return None

    ctrl_m = _CONTROL_RE.search(query)
    if not ctrl_m:
        return None
    role_m = _ROLE_RE.search(query)
    if not role_m:
        return None

    # Resolve which role alias matched (the outer group is the raw text).
    matched = role_m.group(1)
    canonical_role = ""
    for role, pat in _ROLE_ALIAS_LOOKUP:
        if pat.fullmatch(matched):
            canonical_role = role
            break
    if not canonical_role:
        return None

    rationale = ""
    r_m = _RATIONALE_RE.search(query)
    if r_m:
        rationale = (r_m.group("reason") or "").strip().rstrip(".")

    return AcknowledgeIntent(
        control_ref = ctrl_m.group(1),
        role        = canonical_role,
        rationale   = rationale,
        raw_query   = query,
    )


# ── Write path ────────────────────────────────────────────────────────────────

def acknowledge_gap(
    pg_conn,
    tenant_id:    str,
    intent:       AcknowledgeIntent,
    acknowledged_by: str = "chat_user",
) -> dict:
    """Apply the acknowledgement and return a result dict consumed by the
    chat surface. Possible result shapes:

      {'ok': True,  'control_ref': ..., 'role': ..., 'gap_summary': ...}
      {'ok': False, 'reason': 'no_open_gap' | 'multiple_matches' | 'db_error'}

    'no_open_gap' fires when there's no matching tenant_evidence_gaps row in
    status='open' — could mean the user is acknowledging something that's
    already resolved, or the control/role pair doesn't exist for this tenant.
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute(
                """
                SELECT id, control_id, leaf_id, gap_summary, status
                  FROM tenant_evidence_gaps
                 WHERE tenant_id  = %s
                   AND control_ref = %s
                   AND role        = %s
                """,
                (tenant_id, intent.control_ref, intent.role),
            )
            rows = cur.fetchall()
            if not rows:
                return {"ok": False, "reason": "no_match"}

            # If multiple rows match (shouldn't happen — leaf_id should be
            # unique per role for a control, but defensive in case curation
            # adds two leaves with the same role under one spec): pick the
            # open one if present, else the most recently seen.
            open_rows = [r for r in rows if r[4] == "open"]
            if open_rows:
                row = open_rows[0]
            else:
                already = [r for r in rows if r[4] == "acknowledged"]
                if already:
                    row = already[0]
                    return {
                        "ok":           False,
                        "reason":       "already_acknowledged",
                        "control_ref":  intent.control_ref,
                        "role":         intent.role,
                        "gap_summary":  row[3],
                    }
                return {"ok": False, "reason": "no_open_gap"}

            gap_id, control_id, leaf_id, gap_summary, _status = row

            cur.execute(
                """
                UPDATE tenant_evidence_gaps
                   SET status          = 'acknowledged',
                       rationale       = %s,
                       acknowledged_by = %s,
                       acknowledged_at = now(),
                       updated_at      = now()
                 WHERE id        = %s
                   AND tenant_id = %s
                """,
                (intent.rationale, acknowledged_by, gap_id, tenant_id),
            )
        pg_conn.commit()
        return {
            "ok":           True,
            "control_ref":  intent.control_ref,
            "control_id":   control_id,
            "role":         intent.role,
            "leaf_id":      leaf_id,
            "gap_summary":  gap_summary,
            "rationale":    intent.rationale,
        }
    except Exception as e:
        logger.warning("acknowledge_chat: db error: %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return {"ok": False, "reason": "db_error", "error": str(e)}


# ── Answer formatting ─────────────────────────────────────────────────────────

def render_acknowledge_answer(result: dict, intent: AcknowledgeIntent) -> str:
    """Deterministic confirmation answer — no LLM polish (the user's
    acknowledgement should be unambiguously confirmed)."""
    if result.get("ok"):
        rationale = result.get("rationale") or ""
        rat_line  = f' Reason recorded: "{rationale}".' if rationale else ""
        return (
            f'Acknowledged: {intent.control_ref} [{intent.role}] gap is now '
            f'suppressed from the headline gap list.{rat_line} The control '
            f'finding remains as-is (acknowledging a gap does not flip the '
            f'posture to Comply — posture ownership stays with you).'
        )
    reason = result.get("reason", "unknown")
    if reason == "already_acknowledged":
        return (
            f'{intent.control_ref} [{intent.role}] is already acknowledged. '
            f'Nothing changed.'
        )
    if reason == "no_match":
        return (
            f"No engine-detected gap for {intent.control_ref} "
            f"[{intent.role}] — either the control doesn't have a leaf for "
            f"that role, or you haven't uploaded the related evidence model "
            f"yet. Nothing was changed."
        )
    if reason == "no_open_gap":
        return (
            f"No open gap for {intent.control_ref} [{intent.role}] — the "
            f"engine reports this leaf as either satisfied or already "
            f"resolved. Nothing was changed."
        )
    if reason == "db_error":
        return (
            f"Couldn't record the acknowledgement due to a database error. "
            f"Please try again, and if the issue persists check the server "
            f"log."
        )
    return f"Couldn't acknowledge the gap (reason: {reason})."
