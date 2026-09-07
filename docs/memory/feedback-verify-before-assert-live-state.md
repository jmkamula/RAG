---
name: feedback-verify-before-assert-live-state
description: "Before claiming anything about live state (eval passed, grants match, drift closed, tests green), verify against actual state — never rely on \"I ran this earlier\" or on summaries of intent"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Before asserting anything about live state, verify against the actual
live state. Every claim ("eval passed," "grants match intended shape,"
"drift closed," "regression test green," "deploy landed clean") gets
verified against the real thing — the CSV, the information_schema
query, the test run, the endpoint response.

**Why:**
- Ship 119'.c deploy step 5 revealed `DELETE` on `audit_ledger_download_token`
  the schema had explicitly REVOKEd. The claim "schema_v116 REVOKEs
  DELETE" was true; the claim "the live grant is INSERT+SELECT+UPDATE"
  was false. Only running `information_schema.role_table_grants` at
  deploy time caught the gap.
- Ship 122'.a: the CI-script self-test surfaced 8 pre-existing hits
  my manual smoke testing had missed — I'd tested the regex patterns
  in isolation but not against the tree.
- Auto-compaction summaries can inflate what was actually verified.
  "We ran the test suite" and "we ran the test suite and got 4/4
  pass with these specific assertion outputs" survive compaction
  differently.

**How to apply:**
- Parse the CSV before reporting eval numbers — don't trust `grep FAIL`
  counts that filter output away.
- Query information_schema before claiming grant shape.
- Run the regression test (not just eyeball the SQL) before saying
  "regression prevented."
- Check the actual endpoint response (curl / fetch) before saying
  "endpoint registered / returns 200."
- In deploy scripts: print live state (grant matrix, row counts, table
  existence) so the deploy log itself proves the assertion — future
  readers don't have to re-run.

Related: [[feedback-arc-cadence-small-sub-arcs]] (arc close needs
verified assertions), [[feedback-eval-with-each-feature]] (the eval
suite is one specific instance of this discipline).
