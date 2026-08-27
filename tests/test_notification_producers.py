"""
Tests for Ship 3'.c notification producers.

Two producers wired in rag/intake/posture_writer.py:
  - nc_surfaced        (fired inside _log_status_change when the live
                        finding transitions INTO 'NC' from any non-NC
                        state)
  - upload_processed   (fired at write_findings() return when
                        written > 0 and doc_id is set)

Tests verify the CONTROL-FLOW guards, not the DB write itself:
- Correct-condition path fires notify()
- Wrong-condition path skips notify()

The notify() function itself is validated by rag/cascade/notify —
we monkey-patch it to capture calls.

Run:
    PYTHONPATH=/data/arioncomply python3 tests/test_notification_producers.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── Test scaffolding ──────────────────────────────────────────────────

class _FakeCursor:
    """Minimal cursor stub — records execute() calls; returns nothing.

    _log_status_change's INSERT runs against this before the notify hook
    fires. We don't care about the SQL content; we care about the hook
    being reached (or not).
    """
    def __init__(self):
        self.executes: list[str] = []
    def execute(self, sql, params=None):
        self.executes.append(sql)
    def fetchone(self):
        return None
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


def _install_notify_capture():
    """Monkey-patch rag.cascade.notify.notify to append calls to a
    list. Returns (capture_list, restore_fn)."""
    from rag.cascade import notify as _notify_mod
    original = _notify_mod.notify
    captured: list[dict] = []
    def fake_notify(pg_cursor, **kw):
        captured.append(dict(kw))
        return "fake-notif-id"
    _notify_mod.notify = fake_notify
    def restore():
        _notify_mod.notify = original
    return captured, restore


# ── nc_surfaced producer tests ────────────────────────────────────────

def test_nc_surfaced_fires_on_transition_from_ofi_to_nc():
    from rag.intake.posture_writer import _log_status_change
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _log_status_change(
            cur,
            tenant_id       = "00000000-0000-0000-0000-000000000001",
            posture_id      = "11111111-1111-1111-1111-111111111111",
            control_ref     = "A.5.18",
            standard_id     = "ISO27001:2022",
            status_before   = "OFI",
            status_after    = "NC",
            confidence      = "high",
            evidence        = None,
            source_upload_id= None,
        )
        return _ok(
            len(captured) == 1
            and captured[0]["kind"] == "nc_surfaced"
            and captured[0]["related_control_ref"] == "A.5.18"
            and captured[0]["severity"] == "high",
            f"captured={captured}",
        )
    finally:
        restore()


def test_nc_surfaced_fires_on_transition_from_none_to_nc():
    from rag.intake.posture_writer import _log_status_change
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _log_status_change(
            cur,
            tenant_id       = "00000000-0000-0000-0000-000000000001",
            posture_id      = "22222222-2222-2222-2222-222222222222",
            control_ref     = "A.6.4",
            standard_id     = "ISO27001:2022",
            status_before   = None,          # fresh assessment
            status_after    = "NC",
            confidence      = None,
            evidence        = None,
            source_upload_id= None,
        )
        return _ok(len(captured) == 1)
    finally:
        restore()


def test_nc_surfaced_does_not_fire_when_already_nc():
    from rag.intake.posture_writer import _log_status_change
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _log_status_change(
            cur,
            tenant_id       = "00000000-0000-0000-0000-000000000001",
            posture_id      = "33333333-3333-3333-3333-333333333333",
            control_ref     = "A.5.18",
            standard_id     = "ISO27001:2022",
            status_before   = "NC",       # already NC — not a new surfacing
            status_after    = "NC",
            confidence      = "high",
            evidence        = None,
            source_upload_id= None,
        )
        return _ok(len(captured) == 0, f"unexpected fire: {captured}")
    finally:
        restore()


def test_nc_surfaced_does_not_fire_on_transition_to_ofi():
    from rag.intake.posture_writer import _log_status_change
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _log_status_change(
            cur,
            tenant_id       = "00000000-0000-0000-0000-000000000001",
            posture_id      = "44444444-4444-4444-4444-444444444444",
            control_ref     = "A.5.18",
            standard_id     = "ISO27001:2022",
            status_before   = "NC",
            status_after    = "OFI",     # remediation progress — not a new NC
            confidence      = "high",
            evidence        = None,
            source_upload_id= None,
        )
        return _ok(len(captured) == 0, f"unexpected fire: {captured}")
    finally:
        restore()


def test_nc_surfaced_carries_correct_related_fields():
    from rag.intake.posture_writer import _log_status_change
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _log_status_change(
            cur,
            tenant_id       = "00000000-0000-0000-0000-000000000001",
            posture_id      = "55555555-5555-5555-5555-555555555555",
            control_ref     = "Art.32",
            standard_id     = "GDPR:2016/679",
            status_before   = "Comply",
            status_after    = "NC",
            confidence      = "medium",
            evidence        = None,
            source_upload_id= None,
        )
        return _ok(
            captured[0]["related_entity_kind"] == "posture_control"
            and captured[0]["related_entity_id"] == "55555555-5555-5555-5555-555555555555"
            and captured[0]["related_event_type"] == "nc_surfaced"
            and "Art.32" in (captured[0].get("title") or "")
            and "Comply" in (captured[0].get("body") or "")
        )
    finally:
        restore()


# ── upload_processed producer tests ───────────────────────────────────
# (write_findings has heavier setup; test the guard shape via a
# lightweight seam-verify — the notify call site inside the
# `if written > 0 and doc_id` block is straightforward.)

def test_upload_processed_producer_guard_semantics():
    """The producer's guard is `written > 0 and doc_id`. Verify by
    reading the source and asserting the guard exists — no runtime
    setup can reasonably mock the full write_findings path."""
    import rag.intake.posture_writer as pw
    src = Path(pw.__file__).read_text()
    # Guard pattern
    has_guard = "if written > 0 and doc_id:" in src
    has_kind  = 'kind                = "upload_processed"' in src
    has_dedup = 'related_entity_id   = doc_id' in src
    return _ok(
        has_guard and has_kind and has_dedup,
        f"guard={has_guard} kind={has_kind} dedup={has_dedup}",
    )


# ── stage2_proposal_ready producer tests (Ship 3'.e) ──────────────────
# The producer fires inside _persist_engine_proposals AFTER the
# set_assertion write for a pending Stage-2 verdict. Testing the DB
# integration requires a full posture load — we verify the wiring
# statically (source-read) + confirm severity + dedup semantics.

def test_stage2_proposal_ready_wiring():
    """Producer sits inside the write_status == 'pending' branch of
    _persist_engine_proposals and dedups via posture_row_id."""
    import rag.posture_loader as pl
    src = Path(pl.__file__).read_text()
    has_kind    = 'kind                = "stage2_proposal_ready"' in src
    has_dedup   = 'related_entity_id   = posture_row_id' in src
    has_control = 'related_control_ref = control_ref' in src
    # Severity ladder — high when engine NC over live Comply
    has_sev_high = '"high" if (' in src and 'posture == "NC"' in src
    return _ok(
        has_kind and has_dedup and has_control and has_sev_high,
        f"kind={has_kind} dedup={has_dedup} control={has_control} sev={has_sev_high}",
    )


def test_stage2_proposal_ready_gated_on_pending():
    """Producer must NOT fire on 'active' concurrence writes — those
    are engine-agrees-with-live and don't need a Stage-2 review."""
    import rag.posture_loader as pl
    src = Path(pl.__file__).read_text()
    # The producer block sits INSIDE the `if write_status == "pending":`
    # branch. Find the producer block and walk back — the last
    # `if write_status == "pending":` marker should precede it.
    prod_idx = src.find('kind                = "stage2_proposal_ready"')
    gate_idx = src.rfind('if write_status == "pending":', 0, prod_idx)
    return _ok(
        gate_idx > 0 and gate_idx < prod_idx,
        f"gate_idx={gate_idx} prod_idx={prod_idx}",
    )


# ── upload_failed producer tests (Ship 3'.e) ──────────────────────────

def test_upload_failed_wiring():
    """Producer sits inside the pipeline exception handler AFTER
    _update_status(...,'failed',...) and dedups via upload_id."""
    import rag.intake.doc_pipeline as dp
    src = Path(dp.__file__).read_text()
    has_kind    = 'kind                = "upload_failed"' in src
    has_dedup   = 'related_entity_id   = upload_id' in src
    has_kind_e  = 'related_entity_kind = "document_upload"' in src
    has_severity = '"medium"' in src
    return _ok(
        has_kind and has_dedup and has_kind_e and has_severity,
        f"kind={has_kind} dedup={has_dedup} kind_entity={has_kind_e} sev={has_severity}",
    )


def test_upload_failed_gated_on_not_dry_run():
    """Producer must NOT fire on dry-run — those paths never wrote
    a document_uploads row so there's no real failure to notify about."""
    import rag.intake.doc_pipeline as dp
    src = Path(dp.__file__).read_text()
    prod_idx = src.find('kind                = "upload_failed"')
    gate_idx = src.rfind('if not self.dry_run:', 0, prod_idx)
    return _ok(
        gate_idx > 0 and gate_idx < prod_idx,
        f"gate_idx={gate_idx} prod_idx={prod_idx}",
    )


TESTS = [
    test_nc_surfaced_fires_on_transition_from_ofi_to_nc,
    test_nc_surfaced_fires_on_transition_from_none_to_nc,
    test_nc_surfaced_does_not_fire_when_already_nc,
    test_nc_surfaced_does_not_fire_on_transition_to_ofi,
    test_nc_surfaced_carries_correct_related_fields,
    test_upload_processed_producer_guard_semantics,
    test_stage2_proposal_ready_wiring,
    test_stage2_proposal_ready_gated_on_pending,
    test_upload_failed_wiring,
    test_upload_failed_gated_on_not_dry_run,
]


# ── overdue_followups producer tests (Ship 3'.f) ──────────────────────
# The sweep is a backstop that mirrors engine.py's write-path notify.
# Testing is source-read based (heavy DB setup would replicate the
# smoke test that already ran in the arc). What matters here:
#   - both notification kinds are wired
#   - expected_followup_event rows flip to 'overdue' status before notify
#   - severity ladder for triggered_implication maps to cascade_depth
#   - the dry_run branch short-circuits before any writes

def test_overdue_followups_covers_both_kinds():
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        'kind                = "followup_overdue"' in src
        and 'kind                = "implication_overdue"' in src,
        "one of the two producer kinds missing",
    )


def test_overdue_followups_flips_expected_status():
    """The sweep marks expected_followup_event.status='overdue' BEFORE
    notifying, mirroring the write-path in engine.py:1085. Without the
    flip, a subsequent sweep would double-notify."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    # The UPDATE-then-RETURNING pattern is the guard against the race
    return _ok(
        "SET status      = 'overdue'" in src
        and "AND status = 'pending'" in src
        and "RETURNING id" in src,
        "expected_followup_event flip pattern missing",
    )


def test_overdue_followups_severity_by_depth():
    """triggered_implication severity depends on cascade_depth —
    depth 0-1 is critical (parent SLA slipping), deeper is high."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        'severity = "critical" if depth <= 1 else "high"' in src,
        "depth-based severity ladder missing",
    )


def test_overdue_followups_dry_run_short_circuits():
    """dry_run must return before any writes. Guard sits between the
    Step-1 SELECT gather and the Step-2 per-tenant loop."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    # Look for the early-return sentinel
    return _ok(
        "if dry_run or not all_tenants:" in src
        and 'return {"work_type": "overdue_followups"' in src,
        "dry_run short-circuit missing",
    )


def test_overdue_followups_uses_partial_index_dedup():
    """The producer relies on tenant_notification's partial unique index
    for dedup, calling _notify() (which uses ON CONFLICT DO NOTHING).
    No manual SELECT-then-INSERT dedup guard should be present because
    related_entity_id (the followup/implication id) is stable and
    unique to the source row."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    # The producer block calls _notify with related_entity_id
    return _ok(
        "related_entity_id   = fid" in src
        and "related_entity_id   = impl_id" in src,
        "notify() call sites missing related_entity_id dedup key",
    )


TESTS += [
    test_overdue_followups_covers_both_kinds,
    test_overdue_followups_flips_expected_status,
    test_overdue_followups_severity_by_depth,
    test_overdue_followups_dry_run_short_circuits,
    test_overdue_followups_uses_partial_index_dedup,
]


# ── cite_verification_overdue producer tests (Ship 3'.g) ──────────────

def test_cite_verification_overdue_wiring():
    """The sweep is registered in _WORK_TYPES and its function is
    defined."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        'def sweep_cite_verification_overdue(' in src
        and '"cite_verification_overdue":' in src
        and 'kind                = "cite_verification_overdue"' in src,
        "wiring incomplete",
    )


def test_cite_verification_overdue_severity_ladder():
    """Never-verified past due → critical; verified but past due by
    >1 cadence → critical; past due by ≤1 cadence → high. Cite
    verification skews harder than freshness_expiry because there's
    no in-product artefact."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        'if last_verified_at is None:\n                        severity = "critical"' in src
        and 'elif ratio > 1.0:\n                        severity = "critical"' in src
        and 'severity = "high"' in src,
        "severity ladder missing",
    )


def test_cite_verification_overdue_dedup_window():
    """The 7-day dedup window is belt-and-braces on top of the partial
    unique index — catches the case where the tenant dismissed a prior
    notification but the source is still overdue. We respect the
    dismissal for the window."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        "_CITE_VERIFICATION_DEDUP_DAYS = 7" in src
        and "make_interval(days => %s)" in src
        and "AND read_at IS NULL AND dismissed_at IS NULL" in src,
        "dedup pattern missing",
    )


def test_cite_verification_overdue_control_ref_extraction():
    """leaf_id format is `req:CONTROL_REF:LEAF_KEY` → control_ref = middle segment."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        'parts = leaf_id.split(":", 2)' in src
        and 'control_ref = parts[1]' in src,
        "control_ref extraction missing",
    )


def test_cite_verification_overdue_dry_run_short_circuits():
    """dry_run + no data both short-circuit before writes."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        "if dry_run or not by_tenant:" in src,
        "dry_run guard missing",
    )


TESTS += [
    test_cite_verification_overdue_wiring,
    test_cite_verification_overdue_severity_ladder,
    test_cite_verification_overdue_dedup_window,
    test_cite_verification_overdue_control_ref_extraction,
    test_cite_verification_overdue_dry_run_short_circuits,
]


# ── posture_flip_to_comply producer tests (Ship 3'.i) ─────────────────
# Mirror of the nc_surfaced tests — same patterns, inverted direction.

def test_posture_flip_to_comply_fires_from_ofi():
    from rag.intake.posture_writer import _log_status_change
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _log_status_change(
            cur,
            tenant_id       = "00000000-0000-0000-0000-000000000001",
            posture_id      = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            control_ref     = "A.5.18",
            standard_id     = "ISO27001:2022",
            status_before   = "OFI",
            status_after    = "Comply",
            confidence      = "high",
            evidence        = None,
            source_upload_id= None,
        )
        hit = [c for c in captured if c["kind"] == "posture_flip_to_comply"]
        return _ok(
            len(hit) == 1
            and hit[0]["severity"] == "low"
            and hit[0]["related_control_ref"] == "A.5.18",
            f"captured={captured}",
        )
    finally:
        restore()


def test_posture_flip_to_comply_fires_from_nc():
    """NC → Comply is the remediation-success case worth surfacing."""
    from rag.intake.posture_writer import _log_status_change
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _log_status_change(
            cur,
            tenant_id       = "00000000-0000-0000-0000-000000000001",
            posture_id      = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            control_ref     = "A.6.4",
            standard_id     = "ISO27001:2022",
            status_before   = "NC",
            status_after    = "Comply",
            confidence      = "high",
            evidence        = None,
            source_upload_id= None,
        )
        hit = [c for c in captured if c["kind"] == "posture_flip_to_comply"]
        return _ok(len(hit) == 1, f"captured={captured}")
    finally:
        restore()


def test_posture_flip_to_comply_skips_when_already_comply():
    from rag.intake.posture_writer import _log_status_change
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _log_status_change(
            cur,
            tenant_id       = "00000000-0000-0000-0000-000000000001",
            posture_id      = "cccccccc-cccc-cccc-cccc-cccccccccccc",
            control_ref     = "A.5.18",
            standard_id     = "ISO27001:2022",
            status_before   = "Comply",   # already Comply
            status_after    = "Comply",
            confidence      = "high",
            evidence        = None,
            source_upload_id= None,
        )
        hit = [c for c in captured if c["kind"] == "posture_flip_to_comply"]
        return _ok(len(hit) == 0, f"unexpected fire: {captured}")
    finally:
        restore()


def test_posture_flip_to_comply_skips_regression():
    """Comply → OFI is regression, not a positive-news event."""
    from rag.intake.posture_writer import _log_status_change
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _log_status_change(
            cur,
            tenant_id       = "00000000-0000-0000-0000-000000000001",
            posture_id      = "dddddddd-dddd-dddd-dddd-dddddddddddd",
            control_ref     = "A.5.18",
            standard_id     = "ISO27001:2022",
            status_before   = "Comply",
            status_after    = "OFI",
            confidence      = "high",
            evidence        = None,
            source_upload_id= None,
        )
        hit = [c for c in captured if c["kind"] == "posture_flip_to_comply"]
        return _ok(len(hit) == 0, f"unexpected fire: {captured}")
    finally:
        restore()


# ── api_key_expiring producer tests (Ship 3'.i) ───────────────────────

def test_api_key_expiring_wiring():
    """Sweep function + _WORK_TYPES registration + notify wiring."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        'def sweep_api_key_expiring(' in src
        and '"api_key_expiring":' in src
        and 'kind                = "api_key_expiring"' in src,
        "wiring incomplete",
    )


def test_api_key_expiring_severity_buckets():
    """Three escalating buckets: 30d → medium, 7d → high, 1d → critical."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        '("1d",  1,  "critical")' in src
        and '("7d",  7,  "high")' in src
        and '("30d", 30, "medium")' in src,
        "severity buckets missing",
    )


def test_api_key_expiring_bucket_dedup_key():
    """The partial unique index dedupes on
    (kind, related_entity_id, related_control_ref); the bucket label
    goes into related_control_ref so each of the 3 buckets can fire
    once per key without collision."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        "related_control_ref = bucket" in src
        and "related_entity_id   = key_id" in src,
        "bucket dedup key missing",
    )


def test_api_key_expiring_excludes_expired_and_null():
    """Keys past `expires_at` shouldn't warn (they're dead, not
    expiring). Keys with NULL expires_at shouldn't warn (never
    expiring)."""
    import rag.scheduler.tick as tk
    src = Path(tk.__file__).read_text()
    return _ok(
        "AND expires_at IS NOT NULL" in src
        and "AND expires_at > NOW()" in src,
        "expiry-boundary guards missing",
    )


TESTS += [
    test_posture_flip_to_comply_fires_from_ofi,
    test_posture_flip_to_comply_fires_from_nc,
    test_posture_flip_to_comply_skips_when_already_comply,
    test_posture_flip_to_comply_skips_regression,
    test_api_key_expiring_wiring,
    test_api_key_expiring_severity_buckets,
    test_api_key_expiring_bucket_dedup_key,
    test_api_key_expiring_excludes_expired_and_null,
]


# ── auto_resolved producer tests (Ship 95'.b) ─────────────────────────
# Producer sits in rag/cascade/engine.py at the tail of the S3m
# auto-resolve loop. schema_v70 has had the 'auto_resolved' kind in the
# allowlist since 2026-07 but no producer wrote it, so the "Auto-closed"
# retro tile on the Dashboard surfaced zeros even when the underlying
# UPDATE fired. Ship 95'.a retired the tile; Ship 95'.b restores
# reachability via the Notifications inbox.

def test_auto_resolved_fires_one_per_impl_id():
    from rag.cascade.engine import _emit_auto_resolved_notifications
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        n = _emit_auto_resolved_notifications(
            cur,
            tenant_id  = "00000000-0000-0000-0000-000000000001",
            req_id     = "ISO27001:2022:A.5.16",
            event_type = "personnel_offboarded",
            impl_ids   = ["aaaa1111-1111-1111-1111-111111111111",
                          "bbbb2222-2222-2222-2222-222222222222"],
        )
        return _ok(
            n == 2
            and len(captured) == 2
            and captured[0]["kind"] == "auto_resolved"
            and captured[0]["related_control_ref"] == "A.5.16"
            and captured[0]["severity"] == "low"
            and captured[0]["related_entity_kind"] == "triggered_implication"
            and captured[0]["related_event_type"] == "personnel_offboarded",
            f"n={n} captured={captured}",
        )
    finally:
        restore()


def test_auto_resolved_no_impl_ids_no_call():
    """Producer must be a no-op when no implications resolved this pass.
    Otherwise we'd write a spurious FYI notification whenever
    apply_verification walked TRIGGERS_OBLIGATION but found nothing
    open to close."""
    from rag.cascade.engine import _emit_auto_resolved_notifications
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        n = _emit_auto_resolved_notifications(
            cur,
            tenant_id  = "00000000-0000-0000-0000-000000000001",
            req_id     = "ISO27001:2022:A.5.16",
            event_type = "personnel_offboarded",
            impl_ids   = [],
        )
        return _ok(n == 0 and captured == [], f"n={n} captured={captured}")
    finally:
        restore()


def test_auto_resolved_control_ref_split_from_full_req_id():
    """Body prose + related_control_ref must use the tail control_ref
    ('A.5.16'), not the full requirement id ('ISO27001:2022:A.5.16').
    The tenant reads the notification in-inbox; the full req_id is
    system jargon."""
    from rag.cascade.engine import _emit_auto_resolved_notifications
    captured, restore = _install_notify_capture()
    try:
        cur = _FakeCursor()
        _emit_auto_resolved_notifications(
            cur,
            tenant_id  = "00000000-0000-0000-0000-000000000001",
            req_id     = "ISO27001:2022:A.5.16",
            event_type = "personnel_offboarded",
            impl_ids   = ["aaaa1111-1111-1111-1111-111111111111"],
        )
        row = captured[0]
        return _ok(
            row["related_control_ref"] == "A.5.16"
            and "A.5.16" in row["title"]
            and "A.5.16" in row["body"]
            and "ISO27001:2022:A.5.16" not in row["title"]
            and "ISO27001:2022:A.5.16" not in row["body"],
            f"captured={row}",
        )
    finally:
        restore()


def test_auto_resolved_survives_notify_exception():
    """Producer must swallow notify() exceptions so cascade engine's
    own error path never triggers on inbox-write failures. Ship 3'.c
    notify.py is best-effort by contract."""
    from rag.cascade import notify as _notify_mod
    original = _notify_mod.notify
    def raising(*a, **k):
        raise RuntimeError("simulated inbox write failure")
    _notify_mod.notify = raising
    try:
        from rag.cascade.engine import _emit_auto_resolved_notifications
        cur = _FakeCursor()
        n = _emit_auto_resolved_notifications(
            cur,
            tenant_id  = "00000000-0000-0000-0000-000000000001",
            req_id     = "ISO27001:2022:A.5.16",
            event_type = "personnel_offboarded",
            impl_ids   = ["aaaa1111-1111-1111-1111-111111111111"],
        )
        return _ok(n == 0, f"n={n} (expected 0 after simulated failure)")
    finally:
        _notify_mod.notify = original


TESTS += [
    test_auto_resolved_fires_one_per_impl_id,
    test_auto_resolved_no_impl_ids_no_call,
    test_auto_resolved_control_ref_split_from_full_req_id,
    test_auto_resolved_survives_notify_exception,
]


# ── Notification-kind allowlist parity (Ship 96'.a) ────────────────────
# Regression guard against the ghost-contract class of bug caught in
# this arc: schema_v88 added 4 risk-register kinds to the DB CHECK
# constraint but the external API's _ALLOWED_KINDS tuple stayed frozen
# at 13. Result: external clients got a 400 "Unknown notification
# kind" when trying to filter for risk_added / risk_review_due /
# risk_treatment_overdue / residual_above_threshold even though those
# rows flowed through unfiltered polls just fine. These tests parity-
# check all 3 downstream consumers against the DB constraint.

def _parse_check_constraint_kinds():
    """Read the latest schema migration that ALTERs the
    tenant_notification_kind_check constraint. Returns the sorted set
    of kinds it allows."""
    import re
    from pathlib import Path
    db_dir = Path(__file__).parent.parent / "db"
    # Find every schema_*.sql that touches the kind CHECK constraint,
    # pick the one with the highest schema number.
    candidates = []
    for path in db_dir.glob("schema_v*.sql"):
        src = path.read_text()
        if "tenant_notification_kind_check" in src and "kind = ANY" in src:
            # Extract the vN from schema_vN_*.sql
            m = re.match(r"schema_v(\d+)_", path.name)
            if m:
                candidates.append((int(m.group(1)), path))
    if not candidates:
        return set()
    _, latest = max(candidates)
    src = latest.read_text()
    # Match the ARRAY[ ... ] body for kind check specifically
    m = re.search(
        r"tenant_notification_kind_check.*?CHECK\s*\(kind\s*=\s*ANY\s*\(ARRAY\[(.*?)\]\)\)",
        src, re.DOTALL,
    )
    if not m:
        return set()
    body = m.group(1)
    # Strip SQL line comments
    body = re.sub(r"--[^\n]*", "", body)
    kinds = {q for q in re.findall(r"'([^']+)'", body)}
    return kinds


def test_external_api_allowlist_matches_db_constraint():
    """The DB CHECK constraint is the source of truth for legal
    notification kinds. Every entry there must also appear in the
    external API's _ALLOWED_KINDS tuple, else external clients get
    an artificial 400 when filtering for a kind the system emits."""
    from rag.external.endpoints.notifications import _ALLOWED_KINDS
    db_kinds = _parse_check_constraint_kinds()
    api_kinds = set(_ALLOWED_KINDS)
    missing_in_api = db_kinds - api_kinds
    return _ok(
        not missing_in_api,
        f"kinds in DB but missing from external API: {sorted(missing_in_api)}",
    )


def test_spa_humanization_covers_db_constraint():
    """Every DB-legal kind must have a human-readable label in the
    SPA's _NOTIF_KIND_LABEL map. Without it the inbox row shows the
    raw snake_case kind slug — jargon leak."""
    import re
    from pathlib import Path
    src = (Path(__file__).parent.parent / "static" / "arioncomply.html").read_text()
    m = re.search(r"_NOTIF_KIND_LABEL\s*=\s*\{(.*?)\}", src, re.DOTALL)
    if not m:
        return _ok(False, "_NOTIF_KIND_LABEL map not found in SPA")
    body = m.group(1)
    # Strip JS line comments so risk-kind comment lines don't confuse the parse
    body = re.sub(r"//[^\n]*", "", body)
    spa_kinds = set(re.findall(r"^\s*(\w+):", body, re.MULTILINE))
    db_kinds = _parse_check_constraint_kinds()
    missing = db_kinds - spa_kinds
    return _ok(
        not missing,
        f"kinds in DB but missing from SPA _NOTIF_KIND_LABEL: {sorted(missing)}",
    )


def test_spa_deep_link_meta_covers_db_constraint():
    """Every DB-legal kind must have a mode + icon + actionLabel in
    the SPA's _NOTIF_KIND_META map. Without it the inbox row falls
    back to a generic bell + 'inbox' — the tenant clicks and lands
    on the notifications page again."""
    import re
    from pathlib import Path
    src = (Path(__file__).parent.parent / "static" / "arioncomply.html").read_text()
    m = re.search(r"_NOTIF_KIND_META\s*=\s*\{(.*?)\};", src, re.DOTALL)
    if not m:
        return _ok(False, "_NOTIF_KIND_META map not found in SPA")
    body = m.group(1)
    body = re.sub(r"//[^\n]*", "", body)
    spa_kinds = set(re.findall(r"^\s*(\w+):", body, re.MULTILINE))
    db_kinds = _parse_check_constraint_kinds()
    missing = db_kinds - spa_kinds
    return _ok(
        not missing,
        f"kinds in DB but missing from SPA _NOTIF_KIND_META: {sorted(missing)}",
    )


TESTS += [
    test_external_api_allowlist_matches_db_constraint,
    test_spa_humanization_covers_db_constraint,
    test_spa_deep_link_meta_covers_db_constraint,
]


# ── Advisory-tone regression guards (Ship 96'.c) ──────────────────────
# Ship 93'.c codified [[feedback-advisory-tone-not-authoritative]]:
# tenant-facing prose is advisor voice, not authority voice — no
# "compliant / certified / verified by ArionComply / audit-ready".
# Ship 96'.c fixed the two remaining offenders on the notification
# surface (SPA label + stage2 producer prose). These narrow guards
# stop the exact fixed strings from drifting back in a future edit.

def test_no_flagged_tone_in_spa_notif_labels():
    """SPA notification labels shouldn't contain 'compliant' or
    'engine proposal' — both flagged by the advisory-tone rule.
    Codified specifically after Ship 96'.c fixed
    posture_flip_to_comply + stage2_proposal_ready."""
    from pathlib import Path
    import re
    src = (Path(__file__).parent.parent / "static" / "arioncomply.html").read_text()
    m = re.search(r"_NOTIF_KIND_LABEL\s*=\s*\{(.*?)\}", src, re.DOTALL)
    if not m:
        return _ok(False, "_NOTIF_KIND_LABEL map not found in SPA")
    body_map = m.group(1)
    # Strip JS line comments so 'compliant' in a comment isn't flagged
    body_map = re.sub(r"//[^\n]*", "", body_map)
    forbidden = ["compliant", "engine proposal"]
    hits = [w for w in forbidden if w in body_map.lower()]
    return _ok(
        not hits,
        f"advisory-tone violations in _NOTIF_KIND_LABEL: {hits}",
    )


def test_stage2_producer_body_uses_posture_proposal_language():
    """The stage2_proposal_ready producer body must call it a
    'posture proposal', not an 'engine proposal'. CLAUDE.md
    dejargonize-ux-pass mandates the rename; Ship 96'.c applied it
    to this producer's title + body."""
    from pathlib import Path
    src = (Path(__file__).parent.parent / "rag" / "posture_loader.py").read_text()
    # Isolate the stage2_proposal_ready producer block
    idx = src.find('kind                = "stage2_proposal_ready"')
    if idx < 0:
        return _ok(False, "stage2_proposal_ready producer not found")
    window = src[idx:idx + 600]
    return _ok(
        "engine proposal" not in window
        and "Engine proposes" not in window
        and "posture proposal" in window,
        f"stage2 producer prose tone drift; window={window[:400]!r}",
    )


TESTS += [
    test_no_flagged_tone_in_spa_notif_labels,
    test_stage2_producer_body_uses_posture_proposal_language,
]


# ── SPA drill-in tone regression guards (Ship 97'.a) ──────────────────
# Ship 97'.a operator feedback: the control drill-in panel + topic
# detail card still leaked auditor-prep frame ("Auditor-defensibility
# depends on...", "What auditors expect", "Note for audit trail...").
# The product principle is that ArionComply helps the tenant stay
# compliant 24×7 and defend their posture at time of impact —
# auditor readiness is a downstream consequence, not the framing.
# Guards below target the specific fixed strings to prevent
# copy-paste-style regression, per Lesson 133.

def _spa_body_text():
    from pathlib import Path
    return (Path(__file__).parent.parent / "static" / "arioncomply.html").read_text()


def test_no_auditor_defensibility_string_in_spa():
    """The drill-in bridge chip was reworded from 'Auditor-defensibility
    depends on...' to a tenant-frame that leads with 'How strongly
    they defend this posture'. Guard against the old phrasing
    reappearing."""
    src = _spa_body_text()
    return _ok(
        "Auditor-defensibility" not in src
        and "auditor-defensibility" not in src.lower(),
        "'Auditor-defensibility' phrasing still present in SPA",
    )


def test_no_what_auditors_expect_header_in_spa():
    """The topic-detail card was reworded from 'What auditors expect'
    to 'What good coverage looks like'."""
    src = _spa_body_text()
    return _ok(
        "What auditors expect" not in src,
        "'What auditors expect' header still present in SPA",
    )


def test_no_note_for_audit_trail_placeholder_in_spa():
    """The two confirm-reason textareas were reworded from
    'Note for audit trail...' to 'Note for the record...'."""
    src = _spa_body_text()
    return _ok(
        "Note for audit trail" not in src,
        "'Note for audit trail' placeholder still present in SPA",
    )


TESTS += [
    test_no_auditor_defensibility_string_in_spa,
    test_no_what_auditors_expect_header_in_spa,
    test_no_note_for_audit_trail_placeholder_in_spa,
]


# ── Ship 98'.c: engine-proposal SSoT guard ────────────────────────────
# Ship 66'.a codified: N/A is a scoping decision that lives in
# posture_controls.applicability_status. `_persist_engine_proposals`
# must skip controls where the tenant has scoped out via
# applicability_status='na' — otherwise Stage-2 queue fills with
# proposals the tenant already decided are out of scope. Surfaced
# on Arion 2026-08-27: 18 stale N/A proposals (14 A.7 physicals on
# cloud-only tenant + 4 more).

def test_persist_engine_proposals_selects_applicability_status():
    """Guard against reverting Ship 98'.c fix: the SELECT must include
    applicability_status so the skip check has data to check against."""
    import rag.posture_loader as pl
    src = Path(pl.__file__).read_text()
    idx = src.find("def _persist_engine_proposals")
    if idx < 0:
        return _ok(False, "_persist_engine_proposals not found")
    body = src[idx:idx + 5000]
    return _ok(
        "applicability_status" in body,
        "_persist_engine_proposals doesn't select applicability_status "
        "— Ship 66'.a SSoT will silently be ignored",
    )


def test_persist_engine_proposals_skips_na_applicability():
    """Guard against reverting Ship 98'.c fix: the fix must actually
    branch on applicability_status == 'na' and continue."""
    import rag.posture_loader as pl
    src = Path(pl.__file__).read_text()
    idx = src.find("def _persist_engine_proposals")
    if idx < 0:
        return _ok(False, "_persist_engine_proposals not found")
    body = src[idx:idx + 5000]
    return _ok(
        "applicability_status == 'na'" in body and "continue" in body,
        "_persist_engine_proposals doesn't skip N/A controls — "
        "Ship 66'.a SSoT ignored",
    )


TESTS += [
    test_persist_engine_proposals_selects_applicability_status,
    test_persist_engine_proposals_skips_na_applicability,
]


def main():
    print("─" * 70)
    print("  Notification producer tests (Ship 3'.c)")
    print("─" * 70)
    failures = 0
    for t in TESTS:
        try:
            ok, msg = t()
        except Exception as e:
            import traceback
            ok = False
            msg = f"raised {type(e).__name__}: {e}\n{traceback.format_exc()}"
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {t.__name__}")
        if not ok:
            print(f"         {msg}")
            failures += 1
    print("─" * 70)
    print(f"  {len(TESTS) - failures}/{len(TESTS)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
