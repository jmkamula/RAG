"""
ArionComply — Cascade engine (S3, synchronous v1)

When a cite verification carries `structured_events`, this engine
walks the Neo4j event graph and writes `triggered_implication` rows
per the meditation patterns:

  P1 (cross-domain handoff)    — EMITS_EVENT edges, recurse with depth cap
  P9 (cascade depth budget)    — depth cap = 4, cycle detection
  P10 (implication grouping)   — every row stamped with
                                 (source_verification_id, source_event_type,
                                  cascade_path, cascade_depth)

Direct cascade (TRIGGERS_OBLIGATION) is 1-hop from each Event:
  Event -[:TRIGGERS_OBLIGATION]-> RequirementNode  (writes implication)

EMITS_EVENT cascade recurses up to depth 4:
  Event A -[:EMITS_EVENT]-> Event B -[:EMITS_EVENT]-> Event C ...
  Each visited Event then fires its own TRIGGERS_OBLIGATION 1-hop.

What this v1 engine does NOT do (deferred to S3b/later):
  - EXPECTS_FOLLOWUP_EVENT enforcement (needs background sweep)
  - UPDATES_FACT processing (needs ClientFact mutation + applicability)
  - EXPANDS_SCOPE re-evaluation (needs scope re-walk)
  - CASCADES_REVIEW handling (needs control set re-eval)
  - BLOCKS_WHEN suppression (needs blocker state lookup)
  - Threshold aggregation (P5)
  - applies_when evaluation on EMITS_EVENT edges (always fires)
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from typing import Optional


# Max depth for EMITS_EVENT cascade (P9 from the meditation).
MAX_DEPTH = 4

# Parse the various deadline strings used on TRIGGERS_OBLIGATION edges
# into a timedelta. Returns None when the deadline is empty / unknown /
# semantic (e.g. "before", "immediate", "same-day").
_DURATION_RE = re.compile(r"^\s*(\d+)\s*([a-z]+)\s*$", re.IGNORECASE)
_UNIT_DAYS = {
    "h": 1 / 24, "hour": 1 / 24, "hours": 1 / 24,
    "d": 1, "day": 1, "days": 1,
    "w": 7, "week": 7, "weeks": 7,
    "m": 30, "month": 30, "months": 30,
    "y": 365, "year": 365, "years": 365,
}

_SEMANTIC_DEADLINES = {
    "":            None,
    "immediate":   0,
    "same-day":    0,
    "by_start":    0,
    "by start date": 0,
    "before":      0,
    "before_start": 0,
    "by last day": 0,
    "without_undue_delay": 1,
    "at collection": 0,
    "at_collection": 0,
}


def parse_deadline_days(deadline: str | None) -> Optional[float]:
    """Convert a deadline string into days (float, may be fractional).
    Returns None when no deadline can be computed.
    """
    if not deadline:
        return None
    s = deadline.strip().lower()
    if s in _SEMANTIC_DEADLINES:
        return _SEMANTIC_DEADLINES[s]
    # "72h" / "30 days" / "1 month" / etc.
    m = _DURATION_RE.match(s)
    if m:
        n = int(m.group(1))
        unit = m.group(2).rstrip("s")
        if unit in _UNIT_DAYS:
            return n * _UNIT_DAYS[unit]
        # Try with trailing 's' restored
        unit_full = m.group(2)
        if unit_full in _UNIT_DAYS:
            return n * _UNIT_DAYS[unit_full]
    return None


@dataclass
class ImplicationRow:
    """In-memory representation of one cascade-output row before
    it's INSERTed into triggered_implication. Mirrors the schema."""
    source_event_type:    str
    cascade_path:         list[str]
    cascade_depth:        int
    target_control_ref:   str
    target_standard_id:   str
    target_requirement_id: str
    expected_action:      str          # evidence_required | review_required | ...
    deadline_string:      str
    deadline_days:        Optional[float]
    rationale:            str


def _split_requirement_id(req_id: str) -> tuple[str, str]:
    """Split 'ISO27001:2022:A.6.3' -> ('ISO27001:2022', 'A.6.3').
    The standard_id may contain colons (e.g. 'GDPR:2016/679'). The
    LAST colon separates standard from ref.
    """
    idx = req_id.rfind(":")
    if idx < 0:
        return "", req_id
    return req_id[:idx], req_id[idx + 1:]


def walk_cascade(
    neo_session,
    event_type: str,
    *,
    metadata: dict | None = None,
) -> tuple[list[ImplicationRow], list[dict]]:
    """For one structured-event emission (single event_type), walk
    the Neo4j event graph and return all implication rows plus any
    EMITS_EVENT suppressions (applies_when evaluated false).

    Returns (impl_rows, suppressions). Suppression dict shape:
      {source_event_type, target_event_type, applies_when,
       evaluation_note, cascade_path}.

    Walks:
      - TRIGGERS_OBLIGATION on this event (depth 0, expected_action='evidence_required')
      - CASCADES_REVIEW   on this event (depth 0, expected_action='review_required')
      - EMITS_EVENT downstream events + their TRIGGERS_OBLIGATION /
        CASCADES_REVIEW (depth 1..MAX_DEPTH, with cycle detection)

    EMITS_EVENT edges with non-empty applies_when are evaluated against
    `metadata` (the top-level structured event's metadata dict). Edges
    that fail evaluation are logged as suppressions and the downstream
    walk skips that branch.
    """
    metadata = metadata or {}
    rows: list[ImplicationRow] = []
    suppressions: list[dict] = []
    visited: set[str] = set()
    # BFS over EMITS_EVENT, capturing path
    queue: list[tuple[str, list[str], int]] = [(event_type, [event_type], 0)]
    while queue:
        current, path, depth = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        # ── Direct cascade: TRIGGERS_OBLIGATION from current event ──
        result = neo_session.run(
            """
            MATCH (e:Event {event_type: $et})-[r:TRIGGERS_OBLIGATION]->(n:RequirementNode)
            RETURN n.id          AS req_id,
                   r.deadline    AS deadline,
                   r.rationale   AS rationale,
                   coalesce(r.mandatory, true) AS mandatory
            """,
            et=current,
        )
        for rec in result:
            std_id, ref = _split_requirement_id(rec["req_id"])
            rows.append(ImplicationRow(
                source_event_type     = current,
                cascade_path          = list(path),
                cascade_depth         = depth,
                target_control_ref    = ref,
                target_standard_id    = std_id,
                target_requirement_id = rec["req_id"],
                expected_action       = "evidence_required",
                deadline_string       = rec["deadline"] or "",
                deadline_days         = parse_deadline_days(rec["deadline"]),
                rationale             = rec["rationale"] or "",
            ))

        # ── Review cascade: CASCADES_REVIEW from current event (S3b) ──
        # Semantics differ from TRIGGERS_OBLIGATION: the obligation must
        # be RE-EVALUATED against new state, not freshly proven. No
        # deadline on the edge today; we treat review_required as
        # open-ended (due_date NULL) until a review-cadence convention is
        # established.
        result = neo_session.run(
            """
            MATCH (e:Event {event_type: $et})-[r:CASCADES_REVIEW]->(n:RequirementNode)
            RETURN n.id AS req_id
            """,
            et=current,
        )
        for rec in result:
            std_id, ref = _split_requirement_id(rec["req_id"])
            rows.append(ImplicationRow(
                source_event_type     = current,
                cascade_path          = list(path),
                cascade_depth         = depth,
                target_control_ref    = ref,
                target_standard_id    = std_id,
                target_requirement_id = rec["req_id"],
                expected_action       = "review_required",
                deadline_string       = "",
                deadline_days         = None,
                rationale             = "Re-evaluate this control against the new state",
            ))

        # ── Cross-domain cascade: EMITS_EVENT downstream ──
        if depth >= MAX_DEPTH:
            continue
        result = neo_session.run(
            """
            MATCH (a:Event {event_type: $et})-[r:EMITS_EVENT]->(b:Event)
            RETURN b.event_type AS next_event,
                   r.applies_when AS applies_when
            """,
            et=current,
        )
        for rec in result:
            applies_when = rec["applies_when"] or ""
            # S3d: evaluate applies_when against top-level metadata.
            passes, note = evaluate_applies_when(applies_when, metadata)
            if not passes:
                suppressions.append({
                    "source_event_type": current,
                    "target_event_type": rec["next_event"],
                    "applies_when":      applies_when,
                    "evaluation_note":   note,
                    "cascade_path":      list(path),
                })
                continue
            queue.append((rec["next_event"], path + [rec["next_event"]], depth + 1))

    return rows, suppressions


def fetch_followups_for_event(neo_session, event_type: str) -> list[dict]:
    """Return all EXPECTS_FOLLOWUP_EVENT edges for an event_type.

    Each dict: {target_event_type, window_days, rationale}.
    """
    result = neo_session.run(
        """
        MATCH (a:Event {event_type: $et})-[r:EXPECTS_FOLLOWUP_EVENT]->(b:Event)
        RETURN b.event_type   AS target,
               r.window_days  AS window_days,
               r.rationale    AS rationale
        """,
        et=event_type,
    )
    return [{"target_event_type": r["target"],
             "window_days":       int(r["window_days"] or 0),
             "rationale":         r["rationale"] or ""} for r in result]


def fetch_fact_updates_for_event(neo_session, event_type: str) -> list[dict]:
    """Return all UPDATES_FACT edges for an event_type.

    Each dict: {fact_id, operation, rationale}.
    """
    result = neo_session.run(
        """
        MATCH (a:Event {event_type: $et})-[r:UPDATES_FACT]->(f:ClientFact)
        RETURN f.id          AS fact_id,
               r.operation   AS operation,
               r.rationale   AS rationale
        """,
        et=event_type,
    )
    return [{"fact_id":   r["fact_id"],
             "operation": r["operation"] or "set",
             "rationale": r["rationale"] or ""} for r in result]


def load_cascade_overrides(pg_cursor, tenant_id: str) -> dict:
    """Load active per-tenant cascade overrides keyed by event_type.

    Returns dict[event_type, dict] where each value carries:
      {
        "mute_event":          bool,
        "muted_targets":       set[str],   # target_requirement_id strings
        "reason_event":        str | None,
        "reason_targets":      dict[str, str],  # target_req_id -> reason
      }
    """
    pg_cursor.execute(
        """
        SELECT override_kind, event_type, target_requirement_id, reason
          FROM tenant_cascade_override
         WHERE tenant_id = %s::uuid
           AND is_active = TRUE
        """,
        (tenant_id,),
    )
    out: dict[str, dict] = {}
    for kind, et, tgt, reason in pg_cursor.fetchall():
        rec = out.setdefault(et, {
            "mute_event":      False,
            "muted_targets":   set(),
            "reason_event":    None,
            "reason_targets":  {},
        })
        if kind == "mute_event":
            rec["mute_event"]   = True
            rec["reason_event"] = reason or ""
        elif kind == "mute_event_target":
            rec["muted_targets"].add(tgt)
            rec["reason_targets"][tgt] = reason or ""
    return out


def fetch_blockers_for_control(neo_session, requirement_id: str) -> list[dict]:
    """Return all BLOCKS_WHEN edges on a control (the SOURCE of the
    edge is the control whose implications are suppressible).

    Each dict: {applies_when, rationale, target_requirement_id}.
    """
    result = neo_session.run(
        """
        MATCH (a:RequirementNode {id: $id})-[r:BLOCKS_WHEN]->(b:RequirementNode)
        RETURN r.applies_when AS applies_when,
               r.rationale    AS rationale,
               b.id           AS target_id
        """,
        id=requirement_id,
    )
    return [{"applies_when":         rec["applies_when"] or "",
             "rationale":            rec["rationale"] or "",
             "target_requirement_id": rec["target_id"]} for rec in result]


def fetch_scope_expansions_for_event(neo_session, event_type: str) -> list[dict]:
    """Return all EXPANDS_SCOPE edges for an event_type.

    Each dict: {target_requirement_id, scope_kind, rationale}.
    """
    result = neo_session.run(
        """
        MATCH (a:Event {event_type: $et})-[r:EXPANDS_SCOPE]->(n:RequirementNode)
        RETURN n.id          AS req_id,
               r.scope_kind  AS scope_kind,
               r.rationale   AS rationale
        """,
        et=event_type,
    )
    return [{"target_requirement_id": r["req_id"],
             "scope_kind":            r["scope_kind"] or "",
             "rationale":             r["rationale"] or ""} for r in result]


# Map fact_id (e.g. 'fact:employee_count_250_plus') to the column name
# on the `client_facts` table. Single source of truth: strip the
# 'fact:' prefix; the column name matches the suffix exactly.
def _fact_column(fact_id: str) -> str:
    if fact_id.startswith("fact:"):
        return fact_id[5:]
    return fact_id


# Whitelist of valid client_facts columns the cascade is allowed to
# mutate. Lifted from the table schema; gated to prevent SQL-injection
# via crafted fact_ids and to surface unknown facts loudly.
# ── S3d: applies_when expression evaluator ────────────────────────────
#
# Supported syntax (kept deliberately small to avoid embedding a full DSL):
#   <field> == <value>
#   <field> != <value>
#   <field>                            (truthy check)
# where <field> may have a scope-prefix like `asset.contains_personal_data`
# which is stripped before lookup. <value> is `true`, `false`, or a
# string literal (single or double-quoted).
#
# Lookup is against the `metadata` dict on the structured-event that
# fired the cascade (the top-level event, propagated down the BFS).
#
# Returns True when condition is satisfied (cascade should fire) or
# when the field is absent (default-permissive: missing metadata
# doesn't suppress the cascade). Returns False ONLY when the field is
# present AND the comparison is explicit and fails.

_APPLIES_WHEN_RE = re.compile(
    r"""^\s*
        ([A-Za-z_][\w.]*)            # field path (incl. scope prefix)
        \s*
        (?:
          (==|!=)                    # operator
          \s*
          (true|false|"[^"]*"|'[^']*'|\S+)
        )?
        \s*$""",
    re.VERBOSE,
)


def evaluate_applies_when(expr: str, metadata: dict,
                          default_for_missing: bool = True) -> tuple[bool, str]:
    """Evaluate an applies_when expression against a metadata dict.

    Returns (passes, evaluation_note). `passes` is False only when the
    expression explicitly evaluates to false against a present field.

    `default_for_missing` controls behaviour when the field is absent:
      True (default): used by EMITS_EVENT applies_when — "fire the
        cascade unless explicitly suppressed". Missing field is
        treated as pass.
      False: used by BLOCKS_WHEN — "suppress only when explicitly
        asserted". Missing field is treated as NOT matching.
    """
    if not expr or not expr.strip():
        return default_for_missing, "no-condition"
    m = _APPLIES_WHEN_RE.match(expr)
    if not m:
        return default_for_missing, f"unparseable: {expr!r}"
    field = m.group(1)
    op    = m.group(2)
    rhs   = m.group(3)
    # Strip scope prefix: 'asset.contains_personal_data' -> 'contains_personal_data'
    if "." in field:
        field = field.split(".")[-1]
    if field not in metadata:
        return default_for_missing, f"field-absent: {field}"
    actual = metadata[field]
    if op is None:
        # Truthy check
        return bool(actual), f"truthy: {field}={actual!r}"
    # Normalise literal
    if rhs == "true":
        expected = True
    elif rhs == "false":
        expected = False
    elif rhs and rhs[0] in ('"', "'") and rhs[-1] == rhs[0]:
        expected = rhs[1:-1]
    else:
        # Treat as quoted string literal even without quotes (lenient)
        expected = rhs
    if op == "==":
        passes = (actual == expected)
    else:  # !=
        passes = (actual != expected)
    return passes, f"{field}={actual!r} {op} {expected!r}"


def _event_spec_for(event_type: str):
    """Look up an Event spec by event_type from the catalog.
    Lazy-import to avoid cycles; cached at module level after first call.
    Returns None if event_type not in catalog (defensive).
    """
    global _EVENT_SPEC_CACHE
    if not hasattr(_event_spec_for, "_cache"):
        try:
            from enrichment.events.event_nodes import ALL_EVENTS
            _event_spec_for._cache = {e.event_type: e for e in ALL_EVENTS}
        except Exception:
            _event_spec_for._cache = {}
    return _event_spec_for._cache.get(event_type)


_CLIENT_FACTS_COLUMNS = {
    "processes_personal_data", "eu_data_subjects", "uk_data_subjects",
    "role_controller", "role_processor", "role_joint_controller",
    "special_category_data", "criminal_conviction_data", "childrens_data",
    "automated_decision_making", "profiling", "large_scale_processing",
    "systematic_monitoring", "high_risk_processing",
    "employee_count_250_plus", "public_authority",
    "uses_processors", "uses_cloud_services", "transfers_data_outside_eu",
    "develops_software", "has_remote_workers", "has_physical_premises",
}


def fire_cascade(
    pg_cursor,
    neo_session,
    *,
    tenant_id: str,
    verification_log_id: str,
    verified_at,   # datetime
    structured_events: list[dict],
) -> dict:
    """Synchronously walk each emitted event and INSERT rows into
    triggered_implication + expected_followup_event. Also matches
    incoming events against pre-existing pending followups.

    Returns dict with counts: {implications, followups_written,
    followups_satisfied}.

    Caller is responsible for the surrounding transaction + setting
    app.tenant_id GUC via set_session.
    """
    from datetime import timedelta
    impl_count       = 0
    followup_count   = 0
    matched_count    = 0
    seen_targets: set[tuple[str, str, tuple]] = set()
    # Dedup key: (target_requirement_id, expected_action, cascade_path tuple).
    # Same target via two different paths writes TWO rows (auditor can
    # see both justifications); same target via same path + action collapses.

    visited_event_types: set[str] = set()
    # For followup writing: any event_type seen during this fire,
    # whether direct or via EMITS_EVENT, gets its EXPECTS_FOLLOWUP_EVENT
    # edges materialised. Avoids duplicate followup rows when the
    # same downstream event appears via two distinct paths.

    # S3n: load per-tenant cascade overrides up-front
    cascade_overrides = load_cascade_overrides(pg_cursor, tenant_id)

    # S3j: aggregation expansion. Walk structured_events and, for each
    # event with aggregation config (threshold + period), count matching
    # events in the rolling window from the verification log. If the
    # NEW count crosses the threshold AND no recent fire of the
    # aggregation_emits event exists within the window, expand the
    # current verification's structured_events list with the synthetic
    # threshold-crossed event so the cascade engine processes it like
    # any tenant-emitted event.
    expanded_events: list[dict] = list(structured_events)
    for ev in list(structured_events):
        top_et = ev.get("event_type")
        if not top_et:
            continue
        spec = _event_spec_for(top_et)
        if not (spec and spec.aggregation_threshold
                and spec.aggregation_period_days
                and spec.aggregation_emits):
            continue
        threshold = int(spec.aggregation_threshold)
        period_d  = int(spec.aggregation_period_days)
        emit_et   = spec.aggregation_emits
        cnt = ev.get("count", 1)

        # Count matching events from prior verifications in window
        pg_cursor.execute(
            """
            SELECT coalesce(SUM((se->>'count')::int), 0) AS total
              FROM external_evidence_verification_log v
              CROSS JOIN LATERAL jsonb_array_elements(v.structured_events) se
             WHERE v.tenant_id = %s::uuid
               AND v.id        <> %s::uuid
               AND v.verified_at >= now() - make_interval(days => %s)
               AND se->>'event_type' = %s
            """,
            (tenant_id, verification_log_id, period_d, top_et),
        )
        row = pg_cursor.fetchone()
        prior = int(row[0] or 0)
        new_total = prior + int(cnt)

        if prior >= threshold:
            # Threshold was already crossed in the window — skip
            continue
        if new_total < threshold:
            # Not yet crossed
            continue
        # Threshold just crossed by this verification. Synthesize the
        # downstream event and let the regular processing handle it.
        expanded_events.append({
            "event_type": emit_et,
            "count":      1,
            "metadata":   {
                "_aggregation_source": top_et,
                "_aggregation_count":  new_total,
                "_aggregation_window_days": period_d,
            },
        })
        # S3t: notify on threshold crossing
        try:
            from rag.cascade.notify import notify as _notify
            _notify(
                pg_cursor,
                tenant_id           = tenant_id,
                kind                = "threshold_crossed",
                title               = (f"Threshold crossed: {top_et} reached "
                                       f"{new_total} in {period_d}-day window"),
                body                = (f"Threshold of {threshold} crossed. "
                                       f"Cascade engine synthesised {emit_et} → "
                                       f"firing its TRIGGERS_OBLIGATION targets."),
                severity            = "medium",
                related_entity_kind = "external_evidence_verification_log",
                related_entity_id   = verification_log_id,
                related_event_type  = top_et,
            )
        except Exception:
            pass

    structured_events = expanded_events

    for ev in structured_events:
        top_et = ev.get("event_type")
        if not top_et:
            continue

        # S3h: clock attribution. If the tenant supplied occurred_at
        # (event-actually-happened timestamp), use it to anchor the
        # deadline clock. Otherwise fall back to verified_at.
        clock_anchor = "verified_at"
        clock_t = verified_at
        oa_raw = ev.get("occurred_at")
        if oa_raw:
            from datetime import datetime, timezone
            try:
                oa = datetime.fromisoformat(str(oa_raw).replace("Z", "+00:00"))
                if oa.tzinfo is None:
                    oa = oa.replace(tzinfo=timezone.utc)
                clock_t = oa
                clock_anchor = "occurred_at"
            except ValueError:
                # Defensive: validation should have caught this at the
                # endpoint. If we reach here, log and fall back to
                # verified_at silently.
                pass

        # ── Match against pending followups (P2 missing-event detection) ──
        # Every incoming structured event may satisfy a pending
        # expected_followup_event row. Match by event_type within tenant.
        pg_cursor.execute(
            """
            UPDATE expected_followup_event
               SET status                   = 'satisfied',
                   resolved_at              = %s,
                   resolved_verification_id = %s::uuid
             WHERE tenant_id           = %s::uuid
               AND status              = 'pending'
               AND expected_event_type = %s
               AND expires_at         >= %s
            RETURNING id
            """,
            (verified_at, verification_log_id, tenant_id, top_et, verified_at),
        )
        matched_count += len(pg_cursor.fetchall())

        # ── S3g: effectiveness proof check ───────────────────────────
        # If this event's spec requires effectiveness proof AND the
        # tenant didn't supply 'effectiveness_evidence' in metadata,
        # emit closure_proof_missing implications on the TRIGGERS_
        # OBLIGATION targets. Reuses 'attestation_required' action.
        ev_metadata = ev.get("metadata") or {}
        event_spec = _event_spec_for(top_et)
        if event_spec and event_spec.requires_effectiveness_proof:
            proof = ev_metadata.get("effectiveness_evidence")
            if not proof:
                # Walk this event's triggers + emit "proof missing" rows.
                # Separate from walk_cascade output so the rationale is
                # distinctive and the cascade_path marks the proof-missing
                # branch explicitly.
                proof_targets = neo_session.run(
                    """
                    MATCH (e:Event {event_type: $et})-[r:TRIGGERS_OBLIGATION]->(n:RequirementNode)
                    RETURN n.id        AS req_id,
                           r.rationale AS rationale
                    """,
                    et=top_et,
                )
                for rec in proof_targets:
                    std_id, ref = _split_requirement_id(rec["req_id"])
                    key = (rec["req_id"], "attestation_required",
                           (top_et, f"{top_et}:proof_missing"))
                    if key in seen_targets:
                        continue
                    seen_targets.add(key)
                    pg_cursor.execute(
                        """
                        INSERT INTO triggered_implication
                            (tenant_id, source_verification_id, source_event_type,
                             cascade_path, cascade_depth,
                             target_control_ref, target_standard_id, target_requirement_id,
                             expected_action,
                             fired_at, due_date,
                             deadline_string, rationale, clock_anchor)
                        VALUES (%s::uuid, %s::uuid, %s,
                                %s::jsonb, 0,
                                %s, %s, %s,
                                'attestation_required',
                                %s, %s,
                                '', %s, %s)
                        """,
                        (tenant_id, verification_log_id, top_et,
                         json.dumps([top_et, f"{top_et}:proof_missing"]),
                         ref, std_id, rec["req_id"],
                         verified_at, verified_at,  # due immediately — closure already filed
                         f"Closure proof missing: {top_et} requires "
                         f"effectiveness_evidence in metadata; "
                         f"{rec['rationale']}",
                         clock_anchor),
                    )
                    impl_count += 1

        # ── Walk cascade for implications + collect visited events ──
        rows, suppressions = walk_cascade(
            neo_session, top_et, metadata=ev_metadata,
        )
        # Persist suppressions for audit
        for sp in suppressions:
            pg_cursor.execute(
                """
                INSERT INTO cascade_suppression_log
                    (tenant_id, source_verification_id,
                     source_event_type, target_event_type,
                     applies_when, evaluation_context, cascade_path,
                     fired_at)
                VALUES (%s::uuid, %s::uuid,
                        %s, %s,
                        %s, %s::jsonb, %s::jsonb,
                        %s)
                """,
                (tenant_id, verification_log_id,
                 sp["source_event_type"], sp["target_event_type"],
                 sp["applies_when"],
                 json.dumps(ev.get("metadata") or {}),
                 json.dumps(sp["cascade_path"]),
                 verified_at),
            )
        for r in rows:
            visited_event_types.add(r.source_event_type)
            key = (r.target_requirement_id, r.expected_action, tuple(r.cascade_path))
            if key in seen_targets:
                continue
            seen_targets.add(key)

            due_date = None
            if r.deadline_days is not None:
                # S3h: anchor deadline on occurred_at when supplied,
                # else on verified_at (default behaviour).
                due_date = clock_t + timedelta(days=float(r.deadline_days))

            # S3n: per-tenant policy override check — does the tenant
            # mute this event (or specific event-target pair)?
            override = cascade_overrides.get(r.source_event_type)
            if override and (
                override["mute_event"] or
                r.target_requirement_id in override["muted_targets"]
            ):
                if override["mute_event"]:
                    reason = override.get("reason_event") or "tenant policy: muted event"
                else:
                    reason = override["reason_targets"].get(
                        r.target_requirement_id, "tenant policy: muted target"
                    )
                pg_cursor.execute(
                    """
                    INSERT INTO cascade_suppression_log
                        (tenant_id, source_verification_id,
                         source_event_type, target_event_type,
                         applies_when, evaluation_context, cascade_path,
                         fired_at,
                         suppression_kind, target_requirement_id)
                    VALUES (%s::uuid, %s::uuid,
                            %s, NULL,
                            %s, %s::jsonb, %s::jsonb,
                            %s,
                            'policy_override', %s)
                    """,
                    (tenant_id, verification_log_id,
                     r.source_event_type,
                     f"policy_override: {reason[:200]}",
                     json.dumps(ev_metadata),
                     json.dumps(r.cascade_path),
                     verified_at,
                     r.target_requirement_id),
                )
                continue

            # S3i: BLOCKS_WHEN check — does the target control have a
            # blocker that suppresses this implication given the
            # cascade metadata?
            blocked = False
            blockers = fetch_blockers_for_control(
                neo_session, r.target_requirement_id,
            )
            for b in blockers:
                # BLOCKS_WHEN: strict eval (missing field = NOT blocking)
                is_blocking, _note = evaluate_applies_when(
                    b["applies_when"], ev_metadata,
                    default_for_missing=False,
                )
                if is_blocking:
                    pg_cursor.execute(
                        """
                        INSERT INTO cascade_suppression_log
                            (tenant_id, source_verification_id,
                             source_event_type, target_event_type,
                             applies_when, evaluation_context, cascade_path,
                             fired_at,
                             suppression_kind, target_requirement_id)
                        VALUES (%s::uuid, %s::uuid,
                                %s, NULL,
                                %s, %s::jsonb, %s::jsonb,
                                %s,
                                'blocks_when', %s)
                        """,
                        (tenant_id, verification_log_id,
                         r.source_event_type,
                         b["applies_when"],
                         json.dumps(ev_metadata),
                         json.dumps(r.cascade_path),
                         verified_at,
                         r.target_requirement_id),
                    )
                    blocked = True
                    # S3t: notify on cascade blocked
                    try:
                        from rag.cascade.notify import notify as _notify
                        _notify(
                            pg_cursor,
                            tenant_id           = tenant_id,
                            kind                = "cascade_blocked",
                            title               = (f"Cascade blocked: {r.target_control_ref} "
                                                   f"({b['applies_when']})"),
                            body                = (f"Implication on {r.target_requirement_id} "
                                                   f"was suppressed because the BLOCKS_WHEN "
                                                   f"condition {b['applies_when']!r} matched "
                                                   f"the verification metadata. Verify the "
                                                   f"blocker remains active."),
                            severity            = "medium",
                            related_entity_kind = "cascade_suppression_log",
                            related_control_ref = r.target_control_ref,
                            related_event_type  = r.source_event_type,
                        )
                    except Exception:
                        pass
                    break
            if blocked:
                continue

            pg_cursor.execute(
                """
                INSERT INTO triggered_implication
                    (tenant_id, source_verification_id, source_event_type,
                     cascade_path, cascade_depth,
                     target_control_ref, target_standard_id, target_requirement_id,
                     expected_action,
                     fired_at, due_date,
                     deadline_string, rationale, clock_anchor)
                VALUES (%s::uuid, %s::uuid, %s,
                        %s::jsonb, %s,
                        %s, %s, %s,
                        %s,
                        %s, %s,
                        %s, %s, %s)
                """,
                (tenant_id, verification_log_id, r.source_event_type,
                 json.dumps(r.cascade_path), r.cascade_depth,
                 r.target_control_ref, r.target_standard_id, r.target_requirement_id,
                 r.expected_action,
                 verified_at, due_date,
                 r.deadline_string, r.rationale, clock_anchor),
            )
            impl_count += 1

    # ── Write expected_followup_event rows for every visited event ────
    seen_followup_keys: set[tuple[str, str]] = set()
    for et in visited_event_types:
        followups = fetch_followups_for_event(neo_session, et)
        for f in followups:
            key = (et, f["target_event_type"])
            if key in seen_followup_keys:
                continue
            seen_followup_keys.add(key)
            expires = verified_at + timedelta(days=int(f["window_days"]))
            pg_cursor.execute(
                """
                INSERT INTO expected_followup_event
                    (tenant_id, source_verification_id, source_event_type,
                     expected_event_type, window_days,
                     fired_at, expires_at, rationale)
                VALUES (%s::uuid, %s::uuid, %s,
                        %s, %s,
                        %s, %s, %s)
                """,
                (tenant_id, verification_log_id, et,
                 f["target_event_type"], f["window_days"],
                 verified_at, expires, f["rationale"]),
            )
            followup_count += 1

    # ── S3c: UPDATES_FACT processing ─────────────────────────────────
    seen_fact_keys: set[tuple[str, str]] = set()
    fact_changes_applied = 0
    fact_changes_logged  = 0
    for et in visited_event_types:
        fact_updates = fetch_fact_updates_for_event(neo_session, et)
        for fu in fact_updates:
            key = (et, fu["fact_id"])
            if key in seen_fact_keys:
                continue
            seen_fact_keys.add(key)

            col = _fact_column(fu["fact_id"])
            op  = fu["operation"]

            if op not in ("set", "clear", "recompute"):
                # Unknown operation — log without applying
                op = "recompute"  # safest fallback: observational only

            applied = False
            old_value = None
            new_value = None

            if op in ("set", "clear") and col in _CLIENT_FACTS_COLUMNS:
                desired = (op == "set")
                # Read current value
                pg_cursor.execute(
                    f"SELECT {col} FROM client_facts "
                    f"WHERE tenant_id = %s::uuid AND is_active = TRUE LIMIT 1",
                    (tenant_id,),
                )
                row = pg_cursor.fetchone()
                if row is not None:
                    old_value = bool(row[0])
                    if old_value != desired:
                        pg_cursor.execute(
                            f"UPDATE client_facts "
                            f"   SET {col} = %s, "
                            f"       last_updated = %s, "
                            f"       updated_by = NULL "
                            f" WHERE tenant_id = %s::uuid AND is_active = TRUE",
                            (desired, verified_at, tenant_id),
                        )
                        applied = True
                        new_value = desired
                        fact_changes_applied += 1
                    else:
                        # Already matches desired — log as no-op
                        new_value = desired
            elif op == "recompute":
                # Observational only in v1; surface to admin via change log
                pass

            pg_cursor.execute(
                """
                INSERT INTO client_fact_change_log
                    (tenant_id, fact_id, operation,
                     old_value, new_value, applied,
                     source_verification_id, source_event_type, rationale,
                     fired_at)
                VALUES (%s::uuid, %s, %s,
                        %s, %s, %s,
                        %s::uuid, %s, %s,
                        %s)
                """,
                (tenant_id, fu["fact_id"], op,
                 old_value, new_value, applied,
                 verification_log_id, et, fu["rationale"],
                 verified_at),
            )
            fact_changes_logged += 1

    # ── S3c: EXPANDS_SCOPE processing ────────────────────────────────
    # For each EXPANDS_SCOPE edge on a visited event, emit a
    # triggered_implication with expected_action='review_required' and
    # scope_kind populated. Dedup against existing implication rows
    # (since CASCADES_REVIEW may have already written some).
    scope_impl_count = 0
    seen_scope_keys: set[tuple[str, str, str]] = set()
    for et in visited_event_types:
        expansions = fetch_scope_expansions_for_event(neo_session, et)
        for ex in expansions:
            key = (et, ex["target_requirement_id"], ex["scope_kind"])
            if key in seen_scope_keys:
                continue
            seen_scope_keys.add(key)

            std_id, ref = _split_requirement_id(ex["target_requirement_id"])
            pg_cursor.execute(
                """
                INSERT INTO triggered_implication
                    (tenant_id, source_verification_id, source_event_type,
                     cascade_path, cascade_depth,
                     target_control_ref, target_standard_id, target_requirement_id,
                     expected_action, scope_kind,
                     fired_at, due_date,
                     deadline_string, rationale, clock_anchor)
                VALUES (%s::uuid, %s::uuid, %s,
                        %s::jsonb, 0,
                        %s, %s, %s,
                        'review_required', %s,
                        %s, NULL,
                        '', %s, %s)
                """,
                (tenant_id, verification_log_id, et,
                 json.dumps([et]),
                 ref, std_id, ex["target_requirement_id"],
                 ex["scope_kind"],
                 verified_at,
                 ex["rationale"], clock_anchor),
            )
            scope_impl_count += 1

    # Count suppressions written via the cursor's rowcount (the above
    # insertions wrote one row per suppression). For accuracy without
    # re-querying, count what we accumulated in-loop.
    pg_cursor.execute(
        "SELECT count(*) FROM cascade_suppression_log "
        "WHERE source_verification_id = %s::uuid",
        (verification_log_id,),
    )
    suppression_count = pg_cursor.fetchone()[0]

    # ── S3m: auto-resolve open implications via cite ──────────────────
    # For each structured event whose metadata carries
    # 'effectiveness_evidence', walk its TRIGGERS_OBLIGATION targets
    # in Neo4j and resolve any open implications matching those
    # targets on this tenant. The current verification is recorded as
    # the resolving evidence so the auditor can trace the closure.
    auto_resolved = 0
    seen_resolve_targets: set[str] = set()
    for ev in structured_events:
        et = ev.get("event_type")
        md = ev.get("metadata") or {}
        if not et or not md.get("effectiveness_evidence"):
            continue
        result = neo_session.run(
            """
            MATCH (e:Event {event_type: $et})-[r:TRIGGERS_OBLIGATION]->(n:RequirementNode)
            RETURN n.id AS req_id
            """,
            et=et,
        )
        for rec in result:
            req_id = rec["req_id"]
            if req_id in seen_resolve_targets:
                continue
            seen_resolve_targets.add(req_id)
            # Resolve any OPEN pending implications matching this control,
            # excluding this verification's own freshly-written rows.
            pg_cursor.execute(
                """
                UPDATE triggered_implication
                   SET status                 = 'satisfied',
                       resolved_at            = %s,
                       resolved_evidence_kind = 'cite',
                       resolved_evidence_id   = %s::uuid
                 WHERE tenant_id              = %s::uuid
                   AND target_requirement_id  = %s
                   AND status                 = 'pending'
                   AND source_verification_id <> %s::uuid
                RETURNING id
                """,
                (verified_at, verification_log_id,
                 tenant_id, req_id, verification_log_id),
            )
            auto_resolved += len(pg_cursor.fetchall())

    return {
        "implications":           impl_count + scope_impl_count,
        "followups_written":      followup_count,
        "followups_satisfied":    matched_count,
        "fact_changes_applied":   fact_changes_applied,
        "fact_changes_logged":    fact_changes_logged,
        "scope_implications":     scope_impl_count,
        "suppressions":           suppression_count,
        "auto_resolved":          auto_resolved,
    }


def sweep_overdue_followups(
    pg_cursor,
    *,
    tenant_id: str,
    neo_session=None,
) -> dict:
    """Periodic / on-demand sweep: mark pending expected_followup rows
    whose window has elapsed as 'overdue'. Returns dict with counts.

    S3f: when neo_session is supplied, ALSO writes triggered_implication
    rows for each overdue followup — targeting the controls that the
    MISSING (expected) event would have satisfied via its
    TRIGGERS_OBLIGATION edges. The implications carry
    expected_action='attestation_required' and a 2-step cascade_path
    [source_event, expected_event] to indicate the SLA breach pattern.

    Returns:
      {"overdue_marked": N, "sla_implications_written": M}
    """
    # Step 1: flip pending → overdue, retain rows for follow-on processing
    pg_cursor.execute(
        """
        UPDATE expected_followup_event
           SET status      = 'overdue',
               resolved_at = now()
         WHERE tenant_id = %s::uuid
           AND status    = 'pending'
           AND expires_at < now()
        RETURNING id::text, source_verification_id::text,
                  source_event_type, expected_event_type,
                  window_days, fired_at
        """,
        (tenant_id,),
    )
    overdue_rows = pg_cursor.fetchall()
    overdue_count = len(overdue_rows)
    impl_written  = 0

    # S3t: notify on each overdue followup
    if overdue_count > 0:
        from rag.cascade.notify import notify as _notify
        for (fid, src_vid, src_event, exp_event, window_d, fired_at) in overdue_rows:
            _notify(
                pg_cursor,
                tenant_id           = tenant_id,
                kind                = "followup_overdue",
                title               = (f"Expected followup overdue: "
                                       f"{src_event} → {exp_event}"),
                body                = (f"Window of {window_d} day(s) elapsed without a "
                                       f"matching {exp_event} verification. Cascade "
                                       f"engine wrote SLA-breach implications on the "
                                       f"controls this event would have satisfied."),
                severity            = "high",
                related_entity_kind = "expected_followup_event",
                related_entity_id   = fid,
                related_event_type  = src_event,
            )

    # Step 2: optional cascade impl propagation
    if neo_session is None or overdue_count == 0:
        return {
            "overdue_marked":            overdue_count,
            "sla_implications_written":  0,
        }

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    seen_targets: set[tuple[str, str, str]] = set()
    # Dedup: (verification_id, expected_event_type, target_requirement_id)

    for (_fid, src_verification_id, src_event, exp_event,
         _window, fired_at) in overdue_rows:
        # Walk TRIGGERS_OBLIGATION on the expected (missing) event —
        # those are the controls whose MUSTs the followup was meant
        # to fulfil. The SLA-breach implication fires on each.
        result = neo_session.run(
            """
            MATCH (e:Event {event_type: $et})-[r:TRIGGERS_OBLIGATION]->(n:RequirementNode)
            RETURN n.id        AS req_id,
                   r.rationale AS rationale
            """,
            et=exp_event,
        )
        for rec in result:
            key = (src_verification_id, exp_event, rec["req_id"])
            if key in seen_targets:
                continue
            seen_targets.add(key)

            std_id, ref = _split_requirement_id(rec["req_id"])
            pg_cursor.execute(
                """
                INSERT INTO triggered_implication
                    (tenant_id, source_verification_id, source_event_type,
                     cascade_path, cascade_depth,
                     target_control_ref, target_standard_id, target_requirement_id,
                     expected_action,
                     fired_at, due_date,
                     deadline_string, rationale)
                VALUES (%s::uuid, %s::uuid, %s,
                        %s::jsonb, 1,
                        %s, %s, %s,
                        'attestation_required',
                        %s, %s,
                        '', %s)
                """,
                (tenant_id, src_verification_id, src_event,
                 json.dumps([src_event, f"{exp_event}:overdue"]),
                 ref, std_id, rec["req_id"],
                 now, now,   # due immediately — SLA already breached
                 f"SLA breach: expected {exp_event} did not arrive within window; "
                 f"{rec['rationale']}"),
            )
            impl_written += 1

    return {
        "overdue_marked":           overdue_count,
        "sla_implications_written": impl_written,
    }
