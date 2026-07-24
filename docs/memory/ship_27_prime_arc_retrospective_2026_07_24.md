---
name: ship-27-prime-arc-retrospective-2026-07-24
description: "Ship 27' arc closer — post-Ship-17 finding-quality audit; two surprises reframed the arc (approve-rate not persisted; grounding_method is the real quality signal); 89.2% deterministic grounding validates Ship 17 catalog fix"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 27' arc retrospective — 3 sub-arcs across one day
(2026-07-24) delivering the post-Ship-17 finding-quality
audit that had been deferred by ~10 arcs. Pure data
investigation; no pipeline code changes. Two surprises
reframed the arc mid-flight into a codified observability
discipline shift.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 27'.a + 27'.b | Design memo + reusable audit script + first-run findings | 3addc57 |
| **27'.c** | **Interpretation + eval + retrospective (this doc)** | pending |

## The two surprises

### Surprise 1: Ship 10's "49% approve" isn't in the DB

Original plan: measure current approve-rate on the Ship 10
5-doc corpus and compare to Ship 10 baseline (48/97=49%).

Reality: `review_status` has only `approved` and `pending`
distinct values on the demo tenant. Zero `rejected` states.
The 720 soft-deleted findings across the 5 docs (78% of
923 all-time rows) are ALL dev-time supersessions —
`critic_ab_run` (208), `wave3-fix` (60), `wave4a-llm-fix`
(60), `wave1-corroboration-test` (59), etc. Zero tenant-
authored HITL rejects.

**Ship 10's original numbers were computed in-flight during
that arc's review pass and never persisted as first-class
signal.** The approve-rate comparison can't be reconstructed
from the current DB.

### Surprise 2: grounding_method IS the quality signal

Ship 6'.b (2026-07-19) added `document_findings.grounding_
method` — a CHECK-allowlisted column tracking how each
finding was grounded. **Ship 27 is the first arc to actually
USE it as a quality metric.**

Post-Ship-17 distribution across the 5-doc corpus (203
active findings):

| Grounding | N | % |
|---|---|---|
| fingerprint | 146 | **71.9%** |
| extractor_verbatim | 35 | **17.2%** |
| unknown / null (pre-Ship-6'.b) | 22 | 10.8% |

**89.2% of active findings are deterministically grounded.**

## The interpretation — Ship 17 catalog fix DID improve quality

Multiple signals converge on the same answer:

1. **2x finding volume** at the same doc corpus (97 → 203
   active).
2. **89% deterministic grounding** — Ship 17's topic-anchor
   catalog fix + Ship 6'.b's substring-verifier gate together
   push nearly every finding into a deterministic bucket.
3. **~50% Stage-1 approve-rate** on reviewed findings —
   consistent with Ship 10's ~49% baseline. The extra 100+
   findings Ship 17 surfaced are NOT lower-signal.
4. **Per-doc pattern** confirms Ship 17's mechanism:
   * Consent Management: 43 active, 42 fingerprint (98%) —
     the doc that Ship 10 processed as 28 all-LLM findings
     now yields 42 deterministic catalog matches.
   * Processor Operations: 124 active, 98 fingerprint (79%) —
     4x growth, mostly via fingerprints.
   * DPIA / Data Quality / RoPA: 8-17 findings each; more
     verbatim than fingerprint (less structured content).

The reframed picture: Ship 17 didn't change extraction
volume (as Ship 17'.d already measured — flat), but it DID
change the **grounding-method composition** dramatically.
Findings that used to require LLM extraction with critic
verification now come from deterministic fingerprint matches
against the topic-anchor-augmented catalog.

## Codified insight — grounding_method is the quality signal

**The right quality metric for an extraction pipeline is
`grounding_method` distribution, NOT `review_status`
approve-rate.**

Why:
- Review status is a moving tenant workflow — pending
  backlog inflates whenever re-extraction outpaces HITL
  action. It measures TENANT ACTIVITY not pipeline quality.
- Grounding method is a first-class finding attribute
  captured at extraction time. It measures HOW the pipeline
  surfaced the finding: deterministic catalog match, LLM
  extraction with strict gate, or legacy unknown.
- Approve rates are stable across corpus changes (Ship 10
  49% → Ship 27 50%) — that stability tells us extraction
  quality is preserved. Grounding distribution captures
  what CHANGED between them (LLM-heavy → deterministic-
  heavy).

Ship 6'.b's provenance column is now **load-bearing for
observability**. The Ship 27 audit surfaces it as the
primary signal for any future extractor / catalog / gate
change.

## Eval outcome

**231/232 PASS + 1 WARN (#200) + 0 FAIL** — identical to all
prior baselines. Pure audit arc with zero pipeline changes;
baseline trivially held as expected.

## Codified 4 lessons

### 1. Persisted signals beat in-flight labeling

Ship 10's "49 rejected" was never a database row. It was a
number written on a design memo during the review pass.
Ten arcs later that signal is unrecoverable. Rule: **if a
metric matters for future comparison, make it a first-class
column with a NOT NULL DEFAULT.** Ship 6'.b's grounding_
method is the counter-example — it lives in the DB, it's
CHECK-allowlisted, and Ship 27 could measure it 5 days
later without any specialised export.

### 2. The right metric emerges from the data, not the plan

Ship 27'.a's plan was "measure approve-rate vs Ship 10
baseline". The data revealed the metric didn't exist and
another metric (grounding_method) was more informative.
The audit-first pattern (Ship 23, Ship 24) delivered again:
investigate before implementing. The Ship 27'.a memo
captured both the failed measurement plan AND the reframed
insight; that documentation is the arc's actual value.

### 3. Long-latent columns get their proof of value years later

Ship 6'.b added `grounding_method` in Ship 6' — an arc
focused on grounding provenance. That column sat mostly
unused (populated correctly at extraction but not surfaced
as a quality metric) for ~5 days across Ship 7-26. Ship 27
turned it into the primary quality signal for the entire
extraction pipeline. The lesson: **provenance columns are
worth adding even when the query isn't obvious yet.** The
right query surfaces once the surrounding infrastructure
matures.

### 4. Reusable audit scripts pay dividends immediately

`scripts/audit_finding_quality.py` (Ship 27'.b) is 200
lines. Future arcs touching the catalog / extractor / gates
can re-run it against the same or different doc corpora
with different tenant IDs. Same pattern as Ship 23'.a's
`audit_cross_role_edges.py` — audit tooling costs a
sub-arc; benefits every subsequent arc that touches the
same domain.

## What Ship 27 did NOT do

- **Fix anything** — pure investigation
- **Backfill grounding_method** for the 22 pre-Ship-6'.b
  findings — those are HITL-approved legacy findings; the
  original extraction context is lost
- **Backfill deletion_reason** for the 67 null-reason
  soft-deletes — pre-Ship-11 wave signal is lost
- **Recover Ship 10's rejected-set** — dev-time labeling
  never persisted; unrecoverable

## Deferred / follow-on candidates from Ship 27

- **Single-token fingerprint fix (Ship 17 deferred)** —
  556 fingerprints still single-token; broader generator
  rewrite. Ship 27's audit tool gives clean before/after
  measurement for whatever this arc delivers.
- **Retire prose `answer` field + migrate eval to
  structured shape** — now that grounding_method proves
  Ship 17's fix worked, the structural shift makes even
  more sense.
- **HITL rejection tracking** — extending `review_status`
  with a `rejected` state (or a `rejection_reason` column
  distinct from `deletion_reason`) so tenant HITL rejects
  become a first-class persisted signal for future audits.

## Ship 27 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 27'.a | Design memo + audit script + first-run findings | Two surprises reframed the arc mid-flight; audit tool delivered |
| 27'.b | Audit script (bundled with 27'.a discovery) | ✓ |
| **27'.c** | **Interpretation + eval + retrospective (this)** | **Codified 4 lessons; grounding_method now the quality signal** |

## Related

- Ship 6'.b (2026-07-19) — the arc that added
  `grounding_method`; Ship 27 first uses it as a quality
  metric
- [[ship-17-prime-arc-retrospective-2026-07-23]] — the
  catalog regen arc Ship 27 validates
- [[ship-23-prime-a-audit-2026-07-24]] — audit-first pattern
  Ship 27 extends
- Ship 10 (2026-07-08 — 07-10) — the 5-doc corpus + HITL
  baseline whose metrics can't be recovered
