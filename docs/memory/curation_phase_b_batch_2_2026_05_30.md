---
name: curation-phase-b-batch-2-2026-05-30
description: "SHIPPED 2026-05-30: A.5.3/A.5.4/A.5.10/A.5.12/A.5.15 policy_program 4-leaf promotions. First time the spine carries non-policy primary artefacts (segregation matrix, management directive). A.5.15 locks the partial-evidence 1/4 multi-leaf path. Eval 49/50 → 54/55."
metadata:
  type: project
---

Second Phase B bulk drafting batch — five ISO A.5 policy/governance controls promoted from single-leaf to policy_program 4-leaf in one pass. Direct follow-up to [[curation-phase-b-batch-1-2026-05-29]] which finished the records_program family.

**Five controls promoted:**

| Control | Spine application | Primary artefact |
|---|---|---|
| A.5.3  Segregation of duties | matrix + approval + communication + review (365d) | `segregation_matrix` |
| A.5.4  Management responsibilities | directive + approval + communication + review (365d) | `management_directive` |
| A.5.10 Acceptable use | policy + approval + communication + review (365d) | `policy` |
| A.5.12 Information classification | scheme + approval + communication + review (365d) | `classification_scheme` |
| A.5.15 Access control policy | policy + approval + communication + review (365d) | `policy` |

**Spine variant note:** policy_program is the spine for "rules + approval + communicated + reviewed" patterns — but the primary artefact is whatever the rule lives in. For A.5.3 it's the matrix, not a policy doc. For A.5.4 it's a directive/mandate. The approval + communication + review siblings are mechanically the same across all five.

**Why:** ISO 27002 § 5.3 calls out the matrix explicitly as the artefact; § 5.4 calls out the management directive. Forcing them into a "policy" frame would have created a misleading evidence_type, and made the EvidenceRequirement title diverge from how auditors actually ask for the artefact. Keeping the primary evidence_type semantic preserves the audit signal.

**How to apply:** When applying policy_program to a future control, ask first: *what is the actual artefact that carries the rules?* If the standard uses a noun other than "policy" (matrix, directive, scheme, register-of-rules), preserve that nominalisation in the primary leaf's `evidence_type` and `title`. The three siblings (approval / communication_record / review_record) stay constant.

**A.5.15 partial-evidence shape (new locked behaviour):**

A.5.15 is the only control in this batch where Arion already had evidence on the primary leaf (the access control policy was uploaded as part of the legacy single-leaf intake). Engine output is therefore `OFI` at `1/4 children satisfied`, not `NC` at `0/4`. This is the first eval case that locks the partial-evidence path of the multi-leaf engine — cases 46-54 all sit at 0/4 (no evidence carried forward); case 55 is the first 1/4 case.

**Why:** Pre-batch every Phase B promotion happened to land on controls with zero existing evidence (registers, IPR procedure, segregation matrices — none of which Arion had uploaded). Without a 1/4 case the eval suite couldn't catch a regression where the engine treats partial evidence the same as no evidence. Case 55 plugs that gap.

**How to apply:** When promoting a control whose pre-promotion single-leaf was already satisfied on the tenant, add an eval case that asserts the partial-evidence engine signature ('OFI' + 'N/4 children satisfied' where N>=1) — not the default 0/N NC path.

**Eval result:** 49/50 → 54/55 PASS. Cases 51-55 added (one per promoted control). Case #25 remains the known-stale fail.

**Engine + Stage-2 verification done before commit:** All five controls re-checked via `pending engine verdict for <ref>` — A.5.3/A.5.4/A.5.10 came back NC + 0/4, A.5.12 NC + 0/4 (live was OFI not Comply — engine still proposes NC), A.5.15 OFI + 1/4.

**Loader declarative-prune statistics:** 1 MUST + 4 SHOULD edges pruned; 4 orphan items pruned. Expected — the old single-leaf A.5.3 had `coverage_scope` as SHOULD that promotes to MUST in the new shape, and A.5.4/A.5.12/A.5.15 had a handful of items whose ids were renamed to fit under the new communication/review leaves. [[loader-orphan-cleanup-followup]] handled the cleanup cleanly.

**LLM eval flakiness observed:** First eval pass showed three flake failures (#3, #21, #24) that all passed on re-run. #3 and #21 are gap-analysis / implementation queries that go through full LLM and occasionally drift in phrasing. #24 (Art.32 status) once produced an answer without the literal substring "A.5" though it referenced "ISO 27001 control 5.26" — i.e. the LLM stripped the "A." prefix from the ref. Re-run baseline is 54/55 PASS, 1 FAIL (#25 only).

**Phase B remaining (post-batch tally):**
- ISO 27001: ~102 thin single-leaf controls remaining (107 from batch 1 minus 5 this batch)
- GDPR: ~297 empty articles still untouched (unchanged this batch)
- Cumulative Phase B progress: 10 controls / 5+5 batches

**Spine model after this batch:** unchanged structurally — policy_program ratified for non-policy primary artefacts (matrix, directive) is a *variant* application, not a new spine. Still five+one validated spines: policy_program, operational_process, technical_control, derived_spec, profile_fact, records_program.

**Next-likely batch candidates:**
- Remaining policy_program in A.5: A.5.7 threat intel (could be operational), A.5.16 identity_management (procedure, operational), A.5.17 authentication info (could be either)
- Or switch to operational_process: A.5.19 supplier risk, A.5.20 supplier agreements, A.5.21 ICT supply chain, A.5.22 supplier review (these are a tight 4-pack), A.5.25 event triage, A.5.26 incident response, A.5.29 disruption response
- Or step into A.6 (8 controls) or A.7 (14 controls) before continuing in A.5

Reviewer fatigue point: 5 controls/batch is a good pace; one batch per session is sustainable. Have done two batches in two days; either spine choice for next session is viable.
