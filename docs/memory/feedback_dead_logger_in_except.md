---
name: feedback-dead-logger-in-except
description: Bare logger.X() calls inside try/except blocks in rag/arion_graph.py.retrieve() would NameError if actually invoked — logger is not defined in the closure scope. Rule when touching that file.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

`retrieve()` in `rag/arion_graph.py` has bare `logger.warning(...)`
/ `logger.debug(...)` calls inside try/except blocks. There is no
`logger` symbol in the retrieve() closure scope — the module has
no top-level `logger = logging.getLogger(__name__)`. Only `get_logger`
is imported from `rag.chain_logger`.

The existing calls have been *dead* — they'd only fire on their
`except` branch, and that branch would itself raise NameError
if reached. The NameError propagates out as an unhandled node
exception, which in LangGraph surfaces as an empty/undefined
response.

Surfaced 2026-07-07 during the chat envelope migration (task
#203). Wave 1 diagnostic `logger.info(...)` called in the happy
path — which DID execute → NameError → empty answer on
"are we certified?" query. Confirmed by revert.

**Why:** the log statements look like they work because they've
never actually been reached in the happy path. Every add-a-log
temptation to that file is a footgun until logger is properly
scoped.

**How to apply:**

- **Never** add `logger.foo(...)` calls to `retrieve()` (or its
  helpers inside `_make_retrieve_node`). Use `get_logger()` from
  `rag.chain_logger` — it returns a real logger or a null-logger
  fallback:
  ```python
  (get_logger() or _NullLogger()).warning("...")
  ```
  Existing acknowledge-gap / stage1 / stage2 exception handlers
  already use this pattern (search "get_logger() or _NullLogger").
- Better: define a module-level `logger` in `arion_graph.py` and
  let `retrieve()` inherit it via closure. Wave 3 of the envelope
  arc could tackle this cleanup; until then, treat any bare
  `logger.X()` in retrieve() as a latent NameError bomb.
- Any diagnostic you're tempted to add to hunt a bug — use
  `print()` or `sys.stderr.write()` if temporary; use
  `get_logger()` if permanent. `logger.X()` there is a trap.

Related:
- [[chat-envelope-arc-2026-07-07]] — the migration that
  surfaced this
