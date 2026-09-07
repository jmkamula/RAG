"""
Ship 126'.b — regression test locking in PII redaction on the 3
diagnostic-log write paths.

For each of ai_call_log / chat_consensus_log / chat_casefile_log,
craft a synthetic input containing common PII patterns (email +
phone + IBAN + IPv4) then verify the persisted row's text fields
have the PII replaced with the pii_redactor's markers.

This test doesn't require a running API — it exercises the writers
directly with test doubles for the payload objects. Uses a real
Postgres connection (ARION_OWNER_PW) + inserts to a real tenant
context; rolls back so no persistent state is left behind.
"""
from __future__ import annotations

import os
import psycopg2

try:
    from dotenv import load_dotenv
    load_dotenv('/data/arioncomply/.env')
except ImportError:
    pass


POISONED_QUERY = (
    "Do we have a breach affecting employee jane.doe@example.com "
    "at +420 777 123 456 with IBAN DE89370400440532013000 "
    "from 10.0.1.85?"
)

# These strings must NOT appear anywhere in the persisted row.
FORBIDDEN_SUBSTRINGS = [
    'jane.doe@example.com',
    '777 123 456',
    'DE89370400440532013000',
    '10.0.1.85',
]

# At least one of these markers must appear in the redacted field.
EXPECTED_MARKERS = [
    '<email-redacted>',
    '<phone-redacted>',
    '<iban-redacted>',
    '<ipv4-redacted>',
]


def _connect():
    return psycopg2.connect(
        host=os.environ.get('PGHOST', '127.0.0.1'),
        port=int(os.environ.get('PGPORT', 5432)),
        dbname='arioncomply_compliance',
        user='arioncomply',
        password=os.environ['ARION_OWNER_PW'],
    )


def _assert_redacted(field_value: str, field_name: str):
    for s in FORBIDDEN_SUBSTRINGS:
        assert s not in field_value, (
            f"{field_name} contains unredacted PII: {s!r} still present. "
            f"Full value (first 500): {field_value[:500]!r}"
        )
    assert any(m in field_value for m in EXPECTED_MARKERS), (
        f"{field_name} has no redaction marker (expected any of "
        f"{EXPECTED_MARKERS}). Value: {field_value[:200]!r}"
    )


def test_ai_call_log_preview_redacts_pii():
    """ai_trace._preview() must scrub PII before storing."""
    from rag.ai_trace import _preview
    out = _preview(POISONED_QUERY)
    _assert_redacted(out, "ai_call_log preview")


def test_consensus_log_redacts_query():
    """log_consensus() must scrub PII from `query` before insert."""
    from rag.consensus.log import log_consensus
    from rag.consensus.types import ConsensusResult

    conn = _connect()
    try:
        # Use a throwaway tenant UUID + wrap in transaction for cleanup
        # Use the dedicated test tenant (schema_v78 seeded this for
        # external-API tests). Same tenant + auto-cleanup via rollback.
        tenant_id = '77777777-7777-7777-7777-777777777777'
        with conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_id,),
            )

        # Minimal ConsensusResult — all-kwargs matches dataclass field
        # ordering in rag/consensus/types.py (verdict + refs +
        # question_type + framework + top_ref_confidence + corroborators
        # + signals + disagreement_notes + clarification +
        # llm_fallback_needed + latency_ms).
        result = ConsensusResult(
            verdict='confident',
            refs=['A.5.15'],
            question_type='definition',
            framework='iso27001_2022',
            top_ref_confidence=0.9,
            corroborators=2,
            signals=[],
            disagreement_notes=[],
            clarification=None,
            llm_fallback_needed=False,
            latency_ms=100,
        )

        row_id = log_consensus(
            conn, tenant_id, POISONED_QUERY, result,
            session_id='test-session', request_id='test-req',
        )
        assert row_id, "log_consensus returned no row_id (silent-fail path)"

        with conn.cursor() as cur:
            cur.execute(
                "SELECT query FROM chat_consensus_log WHERE id = %s::uuid",
                (row_id,),
            )
            stored = cur.fetchone()[0]

        _assert_redacted(stored, "chat_consensus_log.query")
    finally:
        conn.rollback()
        conn.close()


def test_casefile_log_redacts_query_and_answer():
    """log_casefile() must scrub PII from BOTH `query` and `answer_text`.

    CaseFile has many fields typed `Any` (intent/resolved/session/tenant).
    We construct with the minimum surface log_casefile actually reads:
    query, question_type (via `case_file.question_type` accessor), and
    session_id. See `CaseFile` in rag/casefile/types.py.
    """
    from rag.casefile.log    import log_casefile
    from rag.casefile.types  import CaseFile
    from rag.casefile.repair import RepairResult

    conn = _connect()
    try:
        # Use the dedicated test tenant (schema_v78 seeded this for
        # external-API tests). Same tenant + auto-cleanup via rollback.
        tenant_id = '77777777-7777-7777-7777-777777777777'
        with conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_id,),
            )

        # log_casefile reads: case_file.summary(), .question_type, .query
        # Construct with correct dataclass shape.
        cf = CaseFile(
            query=POISONED_QUERY,
            intent={'question_type': 'definition', 'cited_refs': [], 'standards_scope': []},
            resolved=None,
            session=None,
            tenant=None,
            last_entity=None,
            incidents=[],
            risks=[],
            bridge_counts={},
        )
        repair = RepairResult(text='', events=[], footers_added=[])
        poisoned_answer = (
            "Per our records, jane.doe@example.com reported "
            "the issue from 10.0.1.85."
        )
        row_id = log_casefile(
            conn, tenant_id, cf,
            system_prompt_tokens=100,
            user_digest_tokens=200,
            repair_result=repair,
            answer_text=poisoned_answer,
            session_id='test-session',
            request_id='test-req',
        )
        assert row_id, "log_casefile returned no row_id"

        with conn.cursor() as cur:
            cur.execute(
                "SELECT query, answer_text FROM chat_casefile_log WHERE id = %s::uuid",
                (row_id,),
            )
            q_stored, a_stored = cur.fetchone()

        _assert_redacted(q_stored, "chat_casefile_log.query")
        _assert_redacted(a_stored, "chat_casefile_log.answer_text")
    finally:
        conn.rollback()
        conn.close()


if __name__ == '__main__':
    import sys
    tests = [
        ('ai_call_log_preview', test_ai_call_log_preview_redacts_pii),
        ('chat_consensus_log',  test_consensus_log_redacts_query),
        ('chat_casefile_log',   test_casefile_log_redacts_query_and_answer),
    ]
    passed = 0
    failed = []
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
    sys.exit(0 if passed == len(tests) else 1)
