"""
Extraction consensus gatekeeper — bounded LLM arbiter for
arbiter-zone candidates.

Mirrors rag/consensus/gatekeeper.py's discipline:
- Bounded — cannot invent candidates, cannot override auto-accept
  or auto-drop verdicts. Only decides accept/reject on candidates
  the aggregator marked as arbiter (score in 0.40..0.75).
- Batched — one LLM call per doc (up to N candidates per batch),
  not one call per candidate. Keeps cost bounded (~$0.05/doc
  for the arbiter pass).
- Fail-open: on LLM error / malformed JSON, defaults to reject
  (safer to drop uncertain candidates than promote them).

Cost profile:
  - ~200 tokens per candidate (doc excerpt + MUST text + signals)
  - Batch ~40 candidates → ~8-10K tokens input, ~2-3K output
  - GPT-4o-mini: ~$0.03/batch
  - Latency: ~2-4s per batch
"""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

from rag.intake.consensus_extraction.types import (
    CandidateVerdict,
    ExtractionConsensusResult,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
)


logger = logging.getLogger(__name__)

# Batch size — 40 candidates per LLM call. Empirical: keeps prompt
# under 10K tokens with typical excerpts + MUST descriptions.
_ARBITER_BATCH_SIZE = 40


_GATEKEEPER_SYSTEM = """\
You are a bounded compliance-extraction arbiter. Your job is to
decide which candidate findings represent evidence of a control
being addressed in a document.

Think like a real auditor doing document review. Two disciplines
guide every verdict:

1. **Auditor-realistic touch-evidence** (Ship 78'.c): accept
   when the excerpt mentions the MUST's subject in a way you
   could trace to further inquiry. Real docs don't quote MUSTs
   verbatim; broad strokes count.

2. **Artefact discipline** (Ship 79'.b — NEW): but ONLY for
   MUSTs that BELONG TO the artefact this document IS. A DPIA
   procedure doc is evidence for DPIA MUSTs (Art.35, A.7.2.5) —
   NOT for access-rights MUSTs (Art.15), NOT for privacy-policy
   MUSTs (A.5.34), NOT for security-policy MUSTs (Art.32).

You will see a batch of candidates. For each, you have:
- The doc excerpt matched by keyword fingerprints (or empty)
- The MUST item's canonical text (what the item requires)
- The deterministic consensus score
- Which signals fired (fingerprint, doc_mappings, semantic, etc.)

For each candidate, output a single JSON object with:
- candidate_id: the numeric id from the input
- verdict: "accept" (correct-artefact + touch-evidence)
           or "reject" (wrong-artefact OR clearly not about this MUST)
- reason: short (< 10 words) rationale

Output shape:
{
  "verdicts": [
    {"candidate_id": 1, "verdict": "accept", "reason": "policy on required topic"},
    {"candidate_id": 2, "verdict": "reject", "reason": "wrong artefact (DPIA proc vs A.5.34 policy)"},
    ...
  ]
}

DO NOT:
- Invent new candidates
- Change candidate_ids
- Emit any text outside the JSON object

## Artefact discipline — how to reject wrong-artefact candidates

Every document IS one primary artefact. Common artefact
categories:
- **DPIA procedure** — how the org conducts DPIAs (Art.35,
  A.7.2.5 mirror). NOT evidence for Art.15/Art.16/Art.32/A.5.34
  unless the excerpt specifically addresses THOSE topics.
- **RoPA procedure / register** — records of processing activities
  (Art.30, A.7.2.8, B.8.2.6). NOT evidence for privacy policy
  MUSTs unless the excerpt IS a policy statement.
- **Consent procedure** — consent lifecycle (Art.7, A.7.2.3,
  A.7.3.4). NOT evidence for Art.5 principles unless the excerpt
  IS a principles statement.
- **Processor Operations procedure** — how the org acts as
  processor (Art.28, B.8.2.x, B.8.5.x). NOT evidence for
  controller-side MUSTs unless the excerpt explicitly addresses
  them.
- **Data Quality / Accuracy procedure** — accuracy discipline
  (Art.5.1.d, A.7.4.3, Art.16). NOT evidence for minimization
  (A.7.4.4) unless the excerpt IS about minimization.
- **Privacy policy / notice** — org's public privacy stance
  (A.5.34's `privacy_and_pii_protection_policy` leaf, Art.13/14).
- **Security policy** — Art.32 measures + A.5.1 policy family.
- **Access control policy / procedure** — A.5.15, A.5.16-18,
  Art.32.1.b.

Judge the document's artefact from the doc title, section
headings, and content shape. Then reject candidates whose MUST
belongs to a DIFFERENT artefact class.

**Example rejects (wrong artefact)**:
- DPIA proc excerpt "This procedure defines how Arion conducts
  DPIAs" cited as Art.15 evidence → REJECT (Art.15 is right of
  access; DPIA proc isn't a DSAR procedure).
- DPIA proc excerpt cited as A.5.34:privacy_and_pii_protection_policy
  → REJECT (DPIA proc isn't a privacy policy doc).
- Consent proc excerpt cited as Art.5.1.a principles → REJECT
  UNLESS the excerpt IS a principles statement.

**Example accepts (correct artefact + touch-evidence)**:
- DPIA proc excerpt "Consult residual-risk option" cited as
  Art.35:art36_escalation → ACCEPT (Art.35 is DPIA; the excerpt
  IS the escalation mechanism).
- RoPA proc excerpt "International Transfers field" cited as
  Art.30:transfers → ACCEPT (Art.30 is RoPA; the excerpt IS a
  register field).
- Consent proc excerpt "Freely given: Not tied to unrelated
  services" cited as Art.7:no_conditionality → ACCEPT.

## Also reject (structural / adversarial)

- Standalone section header with no body ("## 4. Roles" alone)
- TOC entry, page footer, table-of-contents line
- Empty / whitespace-only excerpts
- Explicit CONTRADICTION ("we do NOT do X")

## Do accept (correct-artefact touch-evidence)

- Excerpt mentions the MUST's subject at all
- Policy statement, procedure step, or role assignment
  on the MUST's topic
- Bullet-list item spelling out the MUST's requirement
- Register field mention matching the MUST's expected field
- Named artefact / procedure that addresses the MUST

Ship 34'.c HITL: 20/20 correct-drops in the aggregator's drop
zone — the deterministic drops are trustworthy. Your job is to
catch WRONG-ARTEFACT candidates the aggregator's signals
attributed via cross-doc keyword hits. Fingerprint matches on
generic intro/scope prose cross-attribute across many refs; the
aggregator can't tell which ones belong to the doc's actual
artefact. That's your job.
"""


def _build_arbiter_prompt(
    doc_name:   str,
    batch:      list[tuple[int, CandidateVerdict, str]],
) -> str:
    """Build the user message for one batch.

    `batch` is [(candidate_id, verdict, must_text), ...]. must_text
    is the canonical text of the MUST (looked up from cache by
    caller).
    """
    lines: list[str] = []
    lines.append(f"Document: {doc_name}")
    lines.append("")
    lines.append(f"Batch of {len(batch)} borderline candidates:")
    lines.append("")
    for cand_id, verdict, must_text in batch:
        (leaf_id, must_id) = verdict.candidate
        excerpt = (verdict.fingerprint_excerpt or "").strip()
        excerpt_snip = (excerpt[:280] + "…") if len(excerpt) > 280 else excerpt
        must_snip = (must_text[:200] + "…") if len(must_text) > 200 else must_text
        signals_str = ", ".join(verdict.signals)
        lines.append(f"--- candidate_id: {cand_id} ---")
        lines.append(f"  MUST: {must_id}")
        lines.append(f"  requires: {must_snip}")
        lines.append(f"  doc excerpt: {excerpt_snip if excerpt else '(no excerpt)'}")
        lines.append(f"  score: {verdict.score}  signals: {signals_str}")
        lines.append("")
    lines.append("Output JSON:")
    return "\n".join(lines)


def _extract_json_object(text: str) -> Optional[dict]:
    """Pull the first JSON object out of the model response. Tolerates
    code-fence wrappers + leading/trailing prose."""
    if not text:
        return None
    # Strip common code-fence wrappers
    text = re.sub(r"^\s*```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```\s*$", "", text)
    # Find first { and match brace depth
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start:i + 1]
                try:
                    return json.loads(candidate)
                except Exception:
                    return None
    return None


def arbitrate_batch(
    doc_name:      str,
    verdicts:      list[CandidateVerdict],
    must_texts:    dict[str, str],
) -> list[CandidateVerdict]:
    """Run the LLM arbiter on a batch of arbiter-zone verdicts.

    Returns the same list of CandidateVerdicts with their `verdict`
    field updated to 'accept' or 'drop' based on LLM output. On any
    error, leaves the input list unchanged (still 'arbiter') — caller
    can decide how to treat unresolved arbiter verdicts.

    `must_texts` is a preloaded dict of {must_id: canonical text}
    for the MUSTs in this batch.
    """
    if not verdicts:
        return verdicts

    # Build indexed batch
    indexed = [(i + 1, v, must_texts.get(v.candidate[1] or "", ""))
               for i, v in enumerate(verdicts)]
    user_msg = _build_arbiter_prompt(doc_name, indexed)

    # LLM call via existing client
    try:
        from rag.llm_client import call as llm_call
        from rag.llm_models import MODEL_CHAT_ANSWER

        response = llm_call(
            system          = _GATEKEEPER_SYSTEM,
            user            = user_msg,
            model           = MODEL_CHAT_ANSWER,
            purpose         = "consensus_gatekeeper",   # ai_call_log CHECK includes this
            temperature     = 0.0,
            max_tokens      = 3000,     # up to 40 verdicts × ~40 tokens each
            response_format = {"type": "json_object"},
        )
    except Exception as e:
        logger.warning("extraction arbiter LLM call failed: %s", e)
        return verdicts

    # LlmResponse.text is the response body; .error is populated on failure
    if getattr(response, "error", None):
        logger.warning("extraction arbiter returned error: %s", response.error)
        return verdicts
    text = getattr(response, "text", "") or ""

    parsed = _extract_json_object(text)
    if not parsed or "verdicts" not in parsed:
        logger.warning("extraction arbiter: malformed JSON response for %s",
                       doc_name)
        return verdicts

    llm_verdicts_by_id = {}
    for entry in parsed.get("verdicts", []):
        if not isinstance(entry, dict):
            continue
        cid = entry.get("candidate_id")
        v   = entry.get("verdict", "").strip().lower()
        if cid is not None and v in ("accept", "reject"):
            llm_verdicts_by_id[int(cid)] = v

    # Apply verdicts
    for cand_id, verdict, _must in indexed:
        llm_v = llm_verdicts_by_id.get(cand_id)
        if llm_v == "accept":
            verdict.verdict = "accept"
        elif llm_v == "reject":
            verdict.verdict = "drop"
        # Else: leave as 'arbiter' (fail-open on missing verdicts)

    return verdicts


def arbitrate(
    doc_name:   str,
    result:     ExtractionConsensusResult,
) -> ExtractionConsensusResult:
    """Run the LLM arbiter across all arbiter-zone verdicts in the
    result. Mutates the result in place — n_accept, n_arbiter, n_drop
    updated to reflect the LLM's decisions.
    """
    arbiter_verdicts = [v for v in result.verdicts if v.verdict == "arbiter"]
    if not arbiter_verdicts:
        return result

    # Preload MUST texts for the batch
    must_ids = list({v.candidate[1] for v in arbiter_verdicts if v.candidate[1]})
    from rag.intake.consensus_extraction.signals.semantic_fit_gate import (
        _fetch_must_texts,
    )
    must_texts = _fetch_must_texts(must_ids)

    # Batch and process
    for i in range(0, len(arbiter_verdicts), _ARBITER_BATCH_SIZE):
        batch = arbiter_verdicts[i:i + _ARBITER_BATCH_SIZE]
        arbitrate_batch(doc_name, batch, must_texts)

    # Recount
    result.n_accept  = sum(1 for v in result.verdicts if v.verdict == "accept")
    result.n_arbiter = sum(1 for v in result.verdicts if v.verdict == "arbiter")
    result.n_drop    = sum(1 for v in result.verdicts if v.verdict == "drop")
    return result
