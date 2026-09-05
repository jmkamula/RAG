"""
Ship 120' — regression test locking in the audit-table grant shape.

Two shapes, both compliance-load-bearing in different ways:

  · **Append-only auditor evidence** (INSERT + SELECT only). No
    UPDATE (no silent history rewrites). No DELETE (no silent
    history erasure). Retention flows must go through an explicit
    superuser erasure path with provenance.

  · **Diagnostic logs** (INSERT + SELECT + DELETE). NOT compliance
    evidence — retention sweeps are allowed. No UPDATE though —
    diagnostic entries reflect what actually happened at the
    moment; rewriting them is a footgun (Ship 4'.b lesson).

Why this test exists: `deploy/baseline_grants.sql` runs AFTER
`schema_v*.sql` migrations and does a blanket
`GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES`. That
silently clobbered every per-table REVOKE in schema_v21 / v79 /
v115 / v116 across every fresh customer install. Ship 120' fixed
the SQL by re-asserting per-table grants at the end of
baseline_grants.sql; this test locks that fix in place.

Fails hard on drift so a future schema change that adds a new
audit-log table doesn't ship without a Ship-120-style entry in
`baseline_grants.sql`.
"""
from __future__ import annotations

import os

import psycopg2


# ── Table classification ───────────────────────────────────────────
#
# Adding a new compliance-load-bearing audit-log table? Add it to
# APPEND_ONLY_AUDIT_TABLES and add the matching REVOKE entry to
# `deploy/baseline_grants.sql`. Both must move together — this
# test catches the mismatch.

APPEND_ONLY_AUDIT_TABLES = {
    # Ship 4'.b / v21 / v79 / v115 originals
    'posture_status_log':       {'SELECT', 'INSERT'},
    'applicability_status_log': {'SELECT', 'INSERT'},
    'client_facts_log':         {'SELECT', 'INSERT'},
    # Ship 121' additions — classified from schema inspection + comments
    'audit_log':                          {'SELECT', 'INSERT'},  # system-wide who/what/old/new
    'confirmation_log':                   {'SELECT', 'INSERT'},  # tenant posture-change confirmations
    'deletion_log':                       {'SELECT', 'INSERT'},  # deletion provenance / erasure record
    'cascade_suppression_log':            {'SELECT', 'INSERT'},  # per COMMENT: "for auditor explanation"
    'client_fact_change_log':             {'SELECT', 'INSERT'},  # per COMMENT: "Append-only audit"
    'external_evidence_verification_log': {'SELECT', 'INSERT'},  # per COMMENT: "Append-only audit history"
}

# Auditor-package tokens are append-only-with-status: INSERT + SELECT
# for the row, UPDATE for the counter + revoke fields, never DELETE.
COUNTER_AUDIT_TABLES = {
    'audit_ledger_download_token': {'SELECT', 'INSERT', 'UPDATE'},
}

# Diagnostic logs get retention (DELETE ok), but never UPDATE.
DIAGNOSTIC_LOG_TABLES = {
    'ai_call_log':        {'SELECT', 'INSERT', 'DELETE'},
    'chat_casefile_log':  {'SELECT', 'INSERT', 'DELETE'},
    'chat_consensus_log': {'SELECT', 'INSERT', 'DELETE'},
    'fact_recompute_log': {'SELECT', 'INSERT', 'DELETE'},
    'intake_trace_log':   {'SELECT', 'INSERT', 'DELETE'},
    # Ship 121' additions
    'intake_consensus_log': {'SELECT', 'INSERT', 'DELETE'},  # per COMMENT: "Diagnostic log for Ship 33"
    'request_trace_log':    {'SELECT', 'INSERT', 'DELETE'},  # chat routing observability
}

ALL_EXPECTED = {
    **APPEND_ONLY_AUDIT_TABLES,
    **COUNTER_AUDIT_TABLES,
    **DIAGNOSTIC_LOG_TABLES,
}


def _load_env():
    """Load .env if present so ARION_OWNER_PW / PG* vars resolve."""
    try:
        from dotenv import load_dotenv
        load_dotenv('/data/arioncomply/.env')
    except ImportError:
        pass


def _fetch_grants():
    """Return {table_name: set(privilege_type)} for arioncomply_app on
    the classified audit tables. Uses the OWNER role because RLS
    doesn't affect information_schema visibility; we need to see the
    grants regardless."""
    _load_env()
    conn = psycopg2.connect(
        host=os.environ.get('PGHOST', '127.0.0.1'),
        port=int(os.environ.get('PGPORT', 5432)),
        dbname='arioncomply_compliance',
        user='arioncomply',
        password=os.environ.get('ARION_OWNER_PW'),
    )
    try:
        with conn.cursor() as cur:
            table_list = tuple(ALL_EXPECTED.keys())
            cur.execute(
                """
                SELECT table_name, privilege_type
                  FROM information_schema.role_table_grants
                 WHERE grantee = 'arioncomply_app'
                   AND table_name = ANY(%s)
                """,
                (list(table_list),),
            )
            out: dict[str, set[str]] = {}
            for name, priv in cur.fetchall():
                out.setdefault(name, set()).add(priv)
            return out
    finally:
        conn.close()


def test_append_only_audit_tables_have_no_update_or_delete():
    """The compliance-load-bearing audit tables must be INSERT+SELECT
    only. Anything more is a silent-erasure vector."""
    actual = _fetch_grants()
    for table, expected in APPEND_ONLY_AUDIT_TABLES.items():
        assert table in actual, (
            f"{table} missing from grants — either the table doesn't exist "
            f"or arioncomply_app has no privileges at all. Check schema_v* "
            f"migrations."
        )
        got = actual[table]
        assert got == expected, (
            f"{table}: expected {sorted(expected)}, got {sorted(got)}. "
            f"Extra privileges = compliance drift. Check "
            f"deploy/baseline_grants.sql — its post-blanket-grant block "
            f"must REVOKE the offenders."
        )


def test_counter_audit_tables_shape():
    """audit_ledger_download_token needs UPDATE (times_used counter +
    revoke fields) but must never allow DELETE."""
    actual = _fetch_grants()
    for table, expected in COUNTER_AUDIT_TABLES.items():
        assert table in actual, f"{table} missing from grants"
        got = actual[table]
        assert got == expected, (
            f"{table}: expected {sorted(expected)}, got {sorted(got)}. "
            f"DELETE on a token table is a silent auditor-access-log "
            f"erasure vector."
        )


def test_diagnostic_logs_have_no_update():
    """Diagnostic logs get DELETE for retention, but never UPDATE —
    LLM-call / intake / consensus / casefile entries reflect what
    actually happened, not what someone later wishes had happened."""
    actual = _fetch_grants()
    for table, expected in DIAGNOSTIC_LOG_TABLES.items():
        assert table in actual, f"{table} missing from grants"
        got = actual[table]
        assert got == expected, (
            f"{table}: expected {sorted(expected)}, got {sorted(got)}. "
            f"UPDATE on a diagnostic log lets someone silently rewrite "
            f"history. Check deploy/baseline_grants.sql."
        )


def test_no_new_audit_table_slipped_in_unclassified():
    """If a future schema adds a new *_log table (or an audit-shape
    table), we want the test-suite to notice + prompt classification.
    Warns rather than hard-fails so it doesn't block unrelated work,
    but visible in CI output.
    """
    _load_env()
    conn = psycopg2.connect(
        host=os.environ.get('PGHOST', '127.0.0.1'),
        port=int(os.environ.get('PGPORT', 5432)),
        dbname='arioncomply_compliance',
        user='arioncomply',
        password=os.environ.get('ARION_OWNER_PW'),
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                  FROM information_schema.tables
                 WHERE table_schema = 'public'
                   AND (table_name LIKE '%_log' OR table_name LIKE '%_audit')
                 ORDER BY table_name
                """
            )
            all_log_shapes = {r[0] for r in cur.fetchall()}
    finally:
        conn.close()

    classified = set(ALL_EXPECTED.keys())
    # Known non-audit tables that end in _log by coincidence.
    known_non_audit = {
        'sweep_log',                  # ops health, no compliance role
        'notification_delivery_log',  # if it exists — retention-eligible
        'stage1_review_chat_log',     # historic; may not exist
        # Ship 121' — audit_log is compliance-load-bearing (classified above),
        # but its partitions are named `audit_log_YYYY_MM` and inherit grants.
        # Filter them so the soft-warn doesn't complain per partition.
    }
    # Filter partitioned children (e.g. `audit_log_2026_09`) from the
    # unclassified set — the parent table's grants cascade to partitions.
    unclassified = {
        n for n in all_log_shapes
        if n not in classified
        and n not in known_non_audit
        and not any(n.startswith(p + '_') and n[len(p) + 1:].replace('_', '').isdigit()
                    for p in classified)
    }
    if unclassified:
        # Not a hard fail — surfaces in the run output for review.
        print(
            f"\nWARNING: unclassified audit-shape tables found: "
            f"{sorted(unclassified)}. Consider adding to APPEND_ONLY_AUDIT_TABLES "
            f"/ DIAGNOSTIC_LOG_TABLES / known_non_audit."
        )


if __name__ == "__main__":
    import sys
    tests = [
        ("append_only_audit_tables", test_append_only_audit_tables_have_no_update_or_delete),
        ("counter_audit_tables",     test_counter_audit_tables_shape),
        ("diagnostic_logs_no_update", test_diagnostic_logs_have_no_update),
        ("no_new_unclassified",       test_no_new_audit_table_slipped_in_unclassified),
    ]
    passed, failed = 0, []
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"PASS {name}")
        except AssertionError as e:
            failed.append((name, str(e)))
            print(f"FAIL {name}: {e}")
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
    if failed:
        sys.exit(1)
