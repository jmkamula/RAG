"""
Ship 130'.a — regression test locking `rag/scheduler/tick.py` loads
`.env` at import time.

The bug this catches: prior to Ship 130'.a, tick.py's `_connect()`
read `PG*` env vars via `os.getenv` but never called `load_dotenv`.
Under systemd's `EnvironmentFile=` directive, the env vars were
populated externally. But any bare-shell invocation of
`python3 -m rag.scheduler.tick` silently failed auth. Surfaced
during Ship 129'.e ops-script iteration (5 fix attempts before
tracing the right layer).

The fix is a 3-line load_dotenv call at module load. This test
verifies:
  1. The load_dotenv call exists and runs at import time
  2. DATABASE_URL is preferred over PG* vars (handles URL-encoded
     passwords automatically via psycopg2)
  3. `_connect()` returns a live connection with only .env present
     (no pre-exported PG vars)

Run:
    PYTHONPATH=/data/arioncomply python3 tests/test_tick_env_loading.py
"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))


def test_tick_module_calls_load_dotenv_at_import():
    """Static check: the file contains a load_dotenv call at module
    level (not inside a function). Fast, no subprocess needed."""
    src = (_ROOT / "rag" / "scheduler" / "tick.py").read_text()
    assert "load_dotenv" in src, \
        "tick.py must call load_dotenv (regressed to systemd-only)"
    # load_dotenv must be at module scope, not inside _connect() or a
    # helper — otherwise import-time env loading doesn't happen.
    lines_before_first_def = []
    for line in src.splitlines():
        if line.startswith("def "):
            break
        lines_before_first_def.append(line)
    preamble = "\n".join(lines_before_first_def)
    assert "load_dotenv(" in preamble, \
        "load_dotenv call must be at module scope (before first `def`)"


def test_tick_connect_uses_database_url_when_present():
    """Static check: _connect() prefers DATABASE_URL. Handles the
    URL-encoded password case that broke Ship 129'.e ops script."""
    src = (_ROOT / "rag" / "scheduler" / "tick.py").read_text()
    assert 'os.getenv("DATABASE_URL"' in src or \
           "os.getenv('DATABASE_URL'" in src, \
        "_connect must prefer DATABASE_URL to handle URL-encoded pwds"


def test_tick_dry_run_from_stripped_shell():
    """Behavioral: `python3 -m rag.scheduler.tick --dry-run` succeeds
    from an environment stripped of PG* variables — only HOME + PATH
    kept. Reproduces the exact PoC failure mode from Ship 129'.e."""
    # Skip if .env doesn't exist (fresh dev tree, no local secrets)
    if not (_ROOT / ".env").exists():
        print("SKIP  no .env present — behavioral check needs a real .env")
        return
    minimal_env = {
        "HOME": os.environ.get("HOME", "/tmp"),
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    }
    result = subprocess.run(
        [sys.executable, "-m", "rag.scheduler.tick",
         "--work", "enrolment_nudge", "--dry-run", "--json"],
        env={**minimal_env, "PYTHONPATH": str(_ROOT)},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, \
        f"tick --dry-run failed with stripped env:\n" \
        f"stdout: {result.stdout[-500:]}\n" \
        f"stderr: {result.stderr[-500:]}"
    assert "tick_id" in result.stdout, \
        f"tick output missing tick_id: {result.stdout[-500:]}"
    # If auth failed, the error appears in stderr as psycopg2.
    assert "no password supplied" not in result.stderr, \
        "PGPASSWORD missing — .env not loaded"
    assert "password authentication failed" not in result.stderr, \
        "PGPASSWORD wrong — DATABASE_URL parse issue"


# ── Runner ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        ("tick.py contains load_dotenv at module scope",
         test_tick_module_calls_load_dotenv_at_import),
        ("_connect prefers DATABASE_URL",
         test_tick_connect_uses_database_url_when_present),
        ("tick --dry-run works from stripped shell",
         test_tick_dry_run_from_stripped_shell),
    ]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {name}\n      {e}")
            failed += 1
        except Exception as e:
            import traceback
            print(f"ERROR {name}\n      {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{passed + failed} PASS")
    sys.exit(0 if failed == 0 else 1)
