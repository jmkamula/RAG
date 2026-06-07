---
name: classifier-posture-short-circuit
description: "SHIPPED 2026-06-06 (fa3641c): CLEAR_INTENT_PHRASES extended with 4 patterns for posture-by-ref queries; case #40 stabilised; saves 1 LLM round-trip per matching query"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

`rag/classifier.py:CLEAR_INTENT_PHRASES` now intercepts the posture-by-ref family before the LLM classifier runs.

## Patterns added

```python
# 1. "our posture/status/finding on/for <X>"  → posture_check
# 2. "what is/are our (compliance) posture/status/finding on/for <X>"  → posture_check
# 3. "is <X> a non-conformity/nc/gap/finding"  → posture_check
# 4. "are we compliant/comply/in compliance with <X>"  → posture_check
```

## Why

Case #40 ("what is our posture on Art.5?") flickered between `posture_check` and `definition` classification. The LLM classifier saw "what is" as definition-flavored and occasionally routed to the definition handler, which writes GDPR-principle narrative without ever using the literal "Art.5" substring — `must_contain=["Art.5"]` then failed. The actual_refs column extracted Art.5 correctly via retrieval, so the failure looked confusing on the surface.

The same posture-by-ref intent surfaces in several eval cases (#25, #39, #40) and almost certainly in real tenant traffic. Routing deterministically avoids the per-query LLM coin-flip.

## How to apply

- Cases #39 + #40 now deterministic; latency on #40 dropped 14.3s → 10.8s (one LLM call saved).
- When adding eval cases that match the posture-by-ref shape, they'll route to `posture_check` without LLM involvement — design `must_contain` against the deterministic posture handler's output (typically lists controls with NC/OFI/Comply pills + reason text).
- For future LLM-stochastic-classifier flickers, prefer extending `CLEAR_INTENT_PHRASES` over hoping the classifier prompt stays stable across model upgrades.

## Related

- [[stage1-detail-show-inference-chain-idea]] — related deterministic-routing thinking
