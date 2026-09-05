"""
Ship 119'.a — tests for rag/posture/pii_redactor.

Locks in the default redaction contract (what gets scrubbed, what
survives) so a future edit can't silently loosen the auditor-ledger
PII posture.
"""
from __future__ import annotations
from rag.posture.pii_redactor import (
    redact_pii,
    pseudonymise_user_id,
    pseudonymise_users_in_text,
    redaction_summary,
    REDACTION_LEVELS,
)


# ── Basic pattern tests ────────────────────────────────────────────

def test_email_redacted():
    out = redact_pii("Contact jane.doe@example.com for the review")
    assert 'jane.doe@example.com' not in out
    assert '<email-redacted>' in out


def test_email_with_plus_addressing():
    out = redact_pii("noreply+audit@corp.example.org sent it")
    assert 'noreply' not in out
    assert '<email-redacted>' in out


def test_us_phone_formatted():
    out = redact_pii("Call (555) 123-4567 if needed")
    assert '555' not in out
    assert '<phone-redacted>' in out


def test_international_phone():
    out = redact_pii("Reach me at +420 777 123 456")
    assert '777' not in out
    assert '<phone-redacted>' in out


def test_ssn_us():
    out = redact_pii("SSN 123-45-6789 on file")
    assert '123-45-6789' not in out
    assert '<ssn-redacted>' in out


def test_credit_card_spaced():
    out = redact_pii("Card 4111 1111 1111 1111 used")
    assert '4111 1111 1111 1111' not in out
    assert '<cc-redacted>' in out


def test_credit_card_dashed():
    out = redact_pii("Card 4111-1111-1111-1111 used")
    assert '4111-1111-1111-1111' not in out
    assert '<cc-redacted>' in out


def test_iban():
    out = redact_pii("Wire to DE89370400440532013000 today")
    assert 'DE89' not in out
    assert '<iban-redacted>' in out


def test_ipv4():
    out = redact_pii("Server at 10.0.1.85 responded")
    assert '10.0.1.85' not in out
    assert '<ipv4-redacted>' in out


def test_czech_national_id():
    out = redact_pii("Rodné číslo 850830/1234 attached")
    assert '850830/1234' not in out
    assert '<national_id_cz-redacted>' in out


def test_uk_nino():
    out = redact_pii("NINO QQ123456C on record")
    assert 'QQ123456C' not in out
    assert '<national_id_uk-redacted>' in out


# ── Non-PII survives ───────────────────────────────────────────────

def test_control_ref_not_redacted():
    out = redact_pii("A.5.15 is not compliant. Review Art.32.1.b next week.")
    assert 'A.5.15' in out
    assert 'Art.32.1.b' in out


def test_date_not_redacted():
    out = redact_pii("Review completed on 2026-03-14")
    assert '2026-03-14' in out
    assert '<' not in out


def test_names_survive_by_default():
    # Names are important compliance evidence and NOT scrubbed by default
    out = redact_pii("The DPO is Jane Doe; reviewed by John Smith.")
    assert 'Jane Doe' in out
    assert 'John Smith' in out


# ── Level semantics ────────────────────────────────────────────────

def test_level_off_passes_through():
    text = "Email: bob@example.com Phone: (555) 123-4567"
    assert redact_pii(text, level='off') == text


def test_level_strict_scrubs_ipv6():
    text = "Server 2001:0db8:85a3::8a2e:0370:7334 rejected"
    out = redact_pii(text, level='strict')
    assert '2001:0db8' not in out
    assert '<ipv6-redacted>' in out


def test_level_default_leaves_ipv6():
    text = "Server 2001:0db8:85a3::8a2e:0370:7334 rejected"
    out = redact_pii(text, level='default')
    # IPv6 not scrubbed at default level
    assert '2001:0db8' in out or '<ipv6-redacted>' not in out


def test_unknown_level_raises():
    try:
        redact_pii("hi", level='wibble')
        assert False, "should have raised"
    except ValueError as e:
        assert 'wibble' in str(e)


# ── Idempotency ────────────────────────────────────────────────────

def test_idempotent_default():
    text = "Email jane@x.com; SSN 111-22-3333; wire DE89370400440532013000"
    once  = redact_pii(text)
    twice = redact_pii(once)
    assert once == twice


# ── Pseudonymisation ───────────────────────────────────────────────

def test_pseudonym_deterministic():
    p1 = pseudonymise_user_id('user-abc-123', 'salt-xyz')
    p2 = pseudonymise_user_id('user-abc-123', 'salt-xyz')
    assert p1 == p2
    assert p1.startswith('user-')
    assert len(p1) == len('user-') + 6


def test_pseudonym_salt_scoped():
    # Same user_id across tenants → different pseudonyms
    p1 = pseudonymise_user_id('user-abc-123', 'salt-tenant-1')
    p2 = pseudonymise_user_id('user-abc-123', 'salt-tenant-2')
    assert p1 != p2


def test_pseudonym_empty_input():
    assert pseudonymise_user_id('', 'any-salt') == '<unknown-user>'


def test_pseudonymise_users_in_text():
    text = "Reviewed by user-abc-123; approved by user-def-456; user-abc-123 signed."
    out = pseudonymise_users_in_text(
        text,
        ['user-abc-123', 'user-def-456'],
        salt='tenant-salt',
    )
    assert 'user-abc-123' not in out
    assert 'user-def-456' not in out
    # Same id → same pseudonym both times
    p1 = pseudonymise_user_id('user-abc-123', 'tenant-salt')
    assert out.count(p1) == 2


def test_pseudonymise_longer_ids_first():
    """Shorter substrings shouldn't be pre-matched by longer ones."""
    text = "id abc and abcdef both appear"
    out = pseudonymise_users_in_text(
        text, ['abc', 'abcdef'], salt='s',
    )
    # Both replaced with their own pseudonyms; the longer one wasn't
    # prematurely eaten by the shorter one's pseudonym.
    p_short = pseudonymise_user_id('abc', 's')
    p_long  = pseudonymise_user_id('abcdef', 's')
    assert p_short in out
    assert p_long in out


# ── Summary ────────────────────────────────────────────────────────

def test_redaction_summary_covers_all_levels():
    for lvl in REDACTION_LEVELS:
        s = redaction_summary(lvl)
        assert isinstance(s, str)
        assert len(s) > 20


if __name__ == "__main__":
    import sys
    passed, failed = 0, []
    tests = [(k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)]
    for name, fn in tests:
        try:
            fn()
            passed += 1
        except Exception as e:
            failed.append((name, e))
    print(f"{passed}/{len(tests)} passed")
    if failed:
        for n, e in failed:
            print(f"  FAIL {n}: {e}")
        sys.exit(1)
