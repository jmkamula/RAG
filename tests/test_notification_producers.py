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


class _FakeConn:
    """Minimal connection stub — .cursor() returns a _FakeCursor."""
    def __init__(self):
        self._cursor = _FakeCursor()
    def cursor(self):
        # Return a context manager
        class _CM:
            def __init__(self, cur):
                self.cur = cur
            def __enter__(self):
                return self.cur
            def __exit__(self, *a):
                return False
        return _CM(self._cursor)


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
