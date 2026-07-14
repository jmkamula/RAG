"""
Signal D — tenant posture priority boost.

Re-weights candidate refs by the tenant's current posture status.
Refs that are currently NC/OFI for the tenant get a small boost —
these are the controls the tenant is most likely asking about
("how do we close the audit?", "prepare for surveillance", etc.).
Refs with Comply/N/A/Not-yet-assessed status get no boost.

Role in consensus:
  - Personalisation. Without this, retrieval scores are corpus-wide
    (which control best matches the query semantically) and don't
    reflect which controls actually matter for THIS tenant.
  - Adds posture_boost_weight (0.15) to any candidate ref whose
    current finding is NC or OFI.
  - Never adds new candidates — only modifies existing ones.
  - Metadata records the finding attached to each boosted ref so
    the aggregator can surface it in diagnostics.
"""
from __future__ import annotations

from typing import Optional

from rag.consensus.types import SignalOutput, ConsensusConfig


# Findings that indicate the tenant has an OPEN gap on this control.
# Boost only these; Comply/N/A/Not-yet-assessed get no boost.
_BOOSTED_FINDINGS = {"NC", "OFI"}


def posture_boost(
    candidate_refs: list[str],
    tenant_posture: Optional[dict],
    cfg:            Optional[ConsensusConfig] = None,
) -> SignalOutput:
    """Boost candidate refs whose tenant posture is NC or OFI.

    Args:
        candidate_refs: refs from other signals — the union of
                        retrieval + explicit_refs + curated_lexicon.
        tenant_posture: The tenant's posture dict. Two shapes are
                        supported for compatibility:
                          - {ref: {"finding": "NC", ...}, ...}
                            (posture_by_ref shape)
                          - {node_id: {"control_ref": "A.5.18",
                                        "finding": "NC", ...}, ...}
                            (posture_loader raw shape)
                        The signal auto-detects which shape.
        cfg:            ConsensusConfig; None → defaults.

    Returns:
        SignalOutput with refs = [(ref, +posture_boost_weight), ...]
        for refs that had an OPEN finding (NC or OFI). Refs without
        an OPEN finding are omitted (the aggregator won't count them
        toward corroborators for THIS signal, but they still exist
        via retrieval / explicit_refs).
    """
    cfg = cfg or ConsensusConfig()
    if not candidate_refs or not tenant_posture:
        return SignalOutput(name="posture_boost", fired=False)

    # Detect shape — posture_by_ref keys look like refs (A.5.18, Art.32);
    # raw posture keys look like node_ids (e.g. "ISO27001:2022:A.5.18").
    posture_by_ref: dict[str, dict] = {}
    any_key = next(iter(tenant_posture), None)
    if any_key is None:
        return SignalOutput(name="posture_boost", fired=False)

    if ":" in str(any_key) and len(str(any_key).split(":")) >= 3:
        # Raw shape — extract control_ref
        for _nid, rec in tenant_posture.items():
            ref = (rec or {}).get("control_ref")
            if ref:
                posture_by_ref[ref] = rec
    else:
        posture_by_ref = tenant_posture

    weight = cfg.posture_boost_weight
    refs_out: list[tuple[str, float]] = []
    findings_by_ref: dict[str, str] = {}

    for ref in candidate_refs:
        rec = posture_by_ref.get(ref)
        if not rec:
            continue
        finding = rec.get("finding") if isinstance(rec, dict) else None
        if finding in _BOOSTED_FINDINGS:
            refs_out.append((ref, weight))
            findings_by_ref[ref] = finding

    if not refs_out:
        return SignalOutput(
            name="posture_boost",
            fired=False,
            metadata={"n_candidates": len(candidate_refs),
                      "n_boosted":    0,
                      "reason":       "no open findings on candidates"},
        )

    return SignalOutput(
        name       = "posture_boost",
        refs       = refs_out,
        metadata   = {
            "n_candidates":    len(candidate_refs),
            "n_boosted":       len(refs_out),
            "findings_by_ref": findings_by_ref,
            "boost_weight":    weight,
        },
        fired      = True,
    )
