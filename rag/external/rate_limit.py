"""
Fixed-window per-key rate limiting for /api/external/v1/*.

Design:
  * 60 requests/minute per api_key (default, tunable per-key later).
  * Single row per key in `api_rate_limit_bucket` — atomic upsert:
      INSERT ... ON CONFLICT (key_id) DO UPDATE ...
    The DO UPDATE branch checks whether `window_start` still points
    at the current minute — if yes, increment; if the minute rolled
    over, reset to 1.
  * check_and_bump() returns (allowed, remaining, reset_epoch) so the
    caller can attach `X-RateLimit-*` response headers.

Concurrency notes:
  * INSERT ... ON CONFLICT is atomic under a single-statement, no
    lock contention at 60/min throughput.
  * Multiple app processes can hit the same key row without
    additional locking; Postgres serializes the ON CONFLICT branch.

Later work (not shipped in Ship 4'.a):
  * Per-key quota override (e.g. some partners get 300/min). Add a
    `rate_limit_per_min` column to api_keys and consume it here.
  * Burst limits distinct from sustained (would need a second
    counter or a token-bucket state).
  * Retention sweep for stale bucket rows. Not urgent — one row per
    active key stays tiny.
"""
from __future__ import annotations

import time
from dataclasses import dataclass


DEFAULT_RATE_LIMIT_PER_MIN = 60


@dataclass
class RateLimitState:
    allowed:      bool
    remaining:    int      # non-negative
    reset_epoch:  int      # unix ts when the current window closes
    limit:        int      # the applicable ceiling
    retry_after:  int      # seconds until reset (0 when allowed)


def check_and_bump(pg_cursor, key_id: str, limit: int = DEFAULT_RATE_LIMIT_PER_MIN) -> RateLimitState:
    """Increment the caller's counter in the current minute window.
    Returns a RateLimitState reflecting the state AFTER the bump.

    If the count exceeds `limit`, `allowed` is False and the caller
    should short-circuit with a 429. The counter is still incremented
    (fixed-window semantics — over-limit requests count too, so a
    hammered key doesn't recover mid-window).

    Concurrency: safe under multiple concurrent requests to the same
    key. The INSERT ... ON CONFLICT DO UPDATE is atomic; Postgres
    serializes the update within the statement.
    """
    pg_cursor.execute(
        """
        INSERT INTO api_rate_limit_bucket (key_id, window_start, count, updated_at)
        VALUES (%s::uuid, date_trunc('minute', NOW()), 1, NOW())
        ON CONFLICT (key_id) DO UPDATE
           SET count = CASE
                 WHEN api_rate_limit_bucket.window_start = date_trunc('minute', NOW())
                     THEN api_rate_limit_bucket.count + 1
                 ELSE 1
               END,
               window_start = date_trunc('minute', NOW()),
               updated_at   = NOW()
        RETURNING count, EXTRACT(EPOCH FROM window_start)::bigint + 60
        """,
        (key_id,),
    )
    count, reset_epoch = pg_cursor.fetchone()
    reset_epoch = int(reset_epoch)

    remaining = max(limit - count, 0)
    allowed   = count <= limit
    retry_after = 0 if allowed else max(reset_epoch - int(time.time()), 1)

    return RateLimitState(
        allowed      = allowed,
        remaining    = remaining,
        reset_epoch  = reset_epoch,
        limit        = limit,
        retry_after  = retry_after,
    )
