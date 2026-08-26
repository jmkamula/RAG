---
name: ship-96-prime-a-notification-kind-audit
description: Ship 96'.a — systematic audit of the 17-kind tenant_notification allowlist across 4 axes (producer / SPA humanization / SPA deep-link / external API allowlist). Applied Lesson 124 to catch other ghost UX contracts. Found 1 real ghost — the 4 Ship 14'.f risk-register kinds were absent from the external API allowlist since 2026-08-01. Fixed + added 3 parity guards that catch every future drift.
metadata:
  type: project
---

# Ship 96'.a — Notification-kind audit (2026-08-26)

## Framing

Ship 95'.b codified Lesson 124: **notification kinds without
producers are ghost UX contracts** — the schema promises "this kind
can happen"; the code never makes it happen. `auto_resolved` had
been ghost for ~13 months; Ship 95'.b wired the producer.

The natural follow-up: apply Lesson 124 systematically across the
whole allowlist to catch other ghosts. Not just the producer axis —
every kind has 4 places it must land to become a real contract:

1. **Producer** — code that INSERTs `tenant_notification` rows with
   this kind
2. **SPA humanization** — `_NOTIF_KIND_LABEL[kind]` for the inbox
   chip
3. **SPA deep-link** — `_NOTIF_KIND_META[kind]` for icon + mode +
   actionLabel
4. **External API allowlist** — `_ALLOWED_KINDS` in
   `rag/external/endpoints/notifications.py`

Missing any of these is a ghost contract of a different flavor.

## Audit

Scanned all 17 kinds in the current DB CHECK constraint (13 from
Ship 3'.a-i schemas v59/v69/v70/v74 + 4 from Ship 14'.f
schema_v88). Per-kind grep across the 4 axes:

| Kind (17) | Producer | SPA label | SPA deep-link | External API |
|---|:-:|:-:|:-:|:-:|
| `implication_overdue` | ✓ | ✓ | ✓ | ✓ |
| `followup_overdue` | ✓ | ✓ | ✓ | ✓ |
| `threshold_crossed` | ✓ | ✓ | ✓ | ✓ |
| `cascade_blocked` | ✓ | ✓ | ✓ | ✓ |
| `auto_resolved` (Ship 95'.b) | ✓ | ✓ | ✓ | ✓ |
| `freshness_expiry` | ✓ | ✓ | ✓ | ✓ |
| `nc_surfaced` | ✓ | ✓ | ✓ | ✓ |
| `upload_processed` | ✓ | ✓ | ✓ | ✓ |
| `stage2_proposal_ready` | ✓ | ✓ | ✓ | ✓ |
| `upload_failed` | ✓ | ✓ | ✓ | ✓ |
| `cite_verification_overdue` | ✓ | ✓ | ✓ | ✓ |
| `posture_flip_to_comply` | ✓ | ✓ | ✓ | ✓ |
| `api_key_expiring` | ✓ | ✓ | ✓ | ✓ |
| `risk_added` | ✓ | ✓ | ✓ | **✗** |
| `risk_treatment_overdue` | ✓ | ✓ | ✓ | **✗** |
| `residual_above_threshold` | ✓ | ✓ | ✓ | **✗** |
| `risk_review_due` | ✓ | ✓ | ✓ | **✗** |

**Ghost contract found**: the 4 Ship 14'.f risk-register kinds
never propagated to the external API's `_ALLOWED_KINDS`. Since
schema_v88 (2026-08-01), external clients hitting
`/api/external/v1/notifications?kind=risk_added` got:

    HTTP 400 — Unknown notification kind(s): ['risk_added'].
    Allowed: [...13 old kinds...]

...even though the DB emits those rows and unfiltered polls return
them. External SIEM/SOAR consumers building risk-notification
routing rules would silently get "not a valid filter, use one of
these 13" — pointing them away from a class of notifications they
absolutely can receive.

The comment on `_ALLOWED_KINDS` read `# Ship 3' arc close (13 kinds
total).` — a locked-in-time doc string that made the tuple look
intentional. That's the durability problem with these lists:
frozen intent embedded in code.

## Delivered

**Fix** — `rag/external/endpoints/notifications.py`:

- 4 risk kinds added to `_ALLOWED_KINDS`
- Comment rewritten to point at the DB CHECK constraint as source
  of truth + mark the 4 Ship 14'.f additions

**3 parity guards** — `tests/test_notification_producers.py`
(32 → 35 tests, all pass):

- `test_external_api_allowlist_matches_db_constraint` — parses the
  latest `schema_v*_*.sql` that ALTERs `tenant_notification_kind
  _check` + asserts every allowed kind is in `_ALLOWED_KINDS`.
  Would have caught this arc's ghost on the day schema_v88 landed.
- `test_spa_humanization_covers_db_constraint` — parses
  `_NOTIF_KIND_LABEL` in the SPA + asserts every DB-legal kind has
  a human label. Prevents a jargon-leak class of bug (inbox row
  renders `risk_review_due` instead of "risk review due").
- `test_spa_deep_link_meta_covers_db_constraint` — parses
  `_NOTIF_KIND_META` + asserts every DB-legal kind has a mode +
  icon + actionLabel. Prevents the class where clicking a
  notification lands on the notifications page instead of the
  actionable surface.

The tests parse each downstream consumer from source — they don't
require running services or DB access. They run in the same suite
as the producer tests (`PYTHONPATH=... python3 tests/test_
notification_producers.py`).

**Verified the guard bites**: `git stash push
rag/external/endpoints/notifications.py` (reverting the fix) →
`test_external_api_allowlist_matches_db_constraint` FAILS with the
exact 4 missing kinds surfaced by name.

## Eval

232 PASS + 1 WARN + 0 FAIL — baseline preserved.

Producer + parity tests: 35/35 pass.

## What's NOT flagged (kept in scope discipline)

- Some producer guards look thin from source-read alone (e.g.
  `nc_surfaced` fires from `_log_status_change` which the tests
  already cover). Ship 96'.a scoped to reachability parity, not
  producer-condition validation — that's already covered by the
  original Ship 3'.c test set.
- SPA label `posture_flip_to_comply → "now compliant"` uses the
  advisory-tone-flagged word "compliant". Not fixed this arc —
  the label describes the transition to the `Comply` finding
  state, so it's contextually less egregious than "you are
  compliant". A future tone-pass sub-arc could rewrite to "moved
  to Comply" for consistency with Ship 93'.c rule.
- Producer bodies were not audited for tone. Also deferred.

## Codified lessons

**Lesson 127: Parity between shared invariants needs a testable
invariant, not discipline.** The kind allowlist lives in 4 places:
DB CHECK constraint, external API tuple, SPA label map, SPA meta
map. Ship 14'.f added 4 kinds to the DB + producer + SPA maps
correctly — but the external API tuple wasn't updated, and no
mechanism forced the mistake to surface. The tests added this arc
make DB → all-3-consumers parity a testable invariant. Rule: when
the same conceptual list appears in N places, one of them is the
source of truth + the other N-1 need a parity assertion.

**Lesson 128: Locked-in-time comments harden mistakes.** The
`_ALLOWED_KINDS` comment said "Ship 3' arc close (13 kinds
total)" — a timestamped intent that made a static tuple look
authoritative. Every reader over the last month who scanned the
file saw a definitive-looking "13 kinds, that's the set" — no
prompt to update. Rule: never write a count into a comment about
a list. Write "must match X source of truth" instead. Counts age
badly; source-of-truth references stay honest.

**Lesson 129: Systematic audits earn their keep by ratio.** 17
kinds × 4 axes = 68 things to check. Manual audit found the ONE
ghost (~1.5% miss rate). But the 3 parity guards added now cover
100% of that surface forever. Rule: after codifying a bug pattern
as a Lesson, the follow-up arc that turns the pattern into a
testable invariant is disproportionately valuable — one systematic
audit + guard write locks the whole class down.

## Related

- [[ship-95-prime-b-auto-resolved-producer]] — where Lesson 124
  was codified. This arc extends the same discipline to 3 other
  parity axes.
- [[ship-14-prime-f]] — the arc that added the 4 risk-register
  kinds (schema_v88). Producer + SPA landed; external API
  allowlist missed.
- [[ship-3-prime-h]] / [[ship-3-prime-i]] — where the SPA
  humanization + deep-link maps were introduced (Ship 3'
  notifications arc)
- [[feedback-advisory-tone-not-authoritative]] — SPA label
  `"now compliant"` on `posture_flip_to_comply` is a candidate
  for a future tone pass
