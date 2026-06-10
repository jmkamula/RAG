---
name: postgres-pool-pre-ping
description: "SHIPPED 2026-06-10 (36e85e1): _PrePingPool wrapper around psycopg2.pool.ThreadedConnectionPool runs SELECT 1 before each checkout. Postgres reaps idle TCP conns (cloud middleboxes, idle_in_transaction_session_timeout), and the base pool serves them anyway, raising `connection is closed` on first query. Bit twice in 24h."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The base `psycopg2.pool.ThreadedConnectionPool` holds connections
opened at startup and reuses them indefinitely. Postgres-side (or
network-side: Azure middleboxes, kernel TCP keepalive, etc.) reaps
idle TCP connections after some timeout. The pool doesn't notice.
First query on a stale checkout raises `OperationalError: the
connection is closed` with no automatic recovery — only an API
restart unwedges it.

Hit twice in 24h:
  - 2026-06-09 ~09:00 mid-day, after ~14h uptime
  - 2026-06-10 ~07:40 morning, after ~15h uptime

The clean-room API was always vulnerable to this; tenant uploads
hadn't yet exercised the path enough to surface it. Now it has.

## What ships

`_PrePingPool` in `api_server.py:88` — drop-in wrapper around
`ThreadedConnectionPool` with identical interface (`getconn`,
`putconn`, `closeall`). `getconn` validates each conn with
`SELECT 1` before returning it. On failure (`OperationalError`,
`InterfaceError`, or `conn.closed` truthy), it discards the conn
via `putconn(conn, close=True)` so the pool refills lazily, then
retries.

Bounded retry: up to `maxconn` (10) iterations. Worst case all
pool conns are stale and we replace them all in one batch. After
that the pool is fresh.

Cost: ~1-2ms ping per request checkout. Acceptable for our
throughput.

## How to apply

- When adding a new long-lived connection pool, prefer pre-ping
  unless you have a strong reason not to. Cloud-hosted databases
  with idle-timeout reapers (Azure, RDS, Cloud SQL) make stale
  conns inevitable.
- When debugging an `OperationalError: connection is closed` in
  the future, FIRST check that the pool is `_PrePingPool` and the
  helper is being used. If not, the pre-ping was lost in a
  refactor.
- The pre-ping is silent on success. Stale-conn discards are
  logged at WARNING — `grep "pg_pool: discarding stale" /tmp/api.log`
  shows how often the wrapper saves us. Frequent hits = consider
  shortening the discard threshold or shipping conn-keepalive
  (`tcp_keepalives_idle` connection parameter).

## Related

- [[engine-verdict-verification-snippet]] — manual psycopg conns
  outside the pool don't benefit from pre-ping. For scripts /
  ad-hoc work the conn lifetime is short enough that staleness
  isn't an issue.
