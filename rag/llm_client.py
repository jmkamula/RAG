"""
Provider-neutral LLM client — raw HTTP, no SDK dependency.

One entry point: `call(system, user, model, purpose, ...)`. Model prefix
picks the wire protocol; endpoint URL comes from env so a local
vLLM/ollama/Together deployment can be swapped in without touching code.

Two wire protocols supported:

  openai-compatible  POST {api_base}/chat/completions
    Works with:
      - OpenAI cloud    LLM_ENDPOINT_OPENAI=https://api.openai.com/v1
      - vLLM local      LLM_ENDPOINT_OPENAI=http://mistral.internal:8000/v1
      - ollama local    LLM_ENDPOINT_OPENAI=http://localhost:11434/v1
      - Together / Anyscale / Groq / others exposing OpenAI protocol
    Wire format: ChatML messages array (system role as message).

  anthropic          POST {api_base}/messages
    Claude native — system as top-level field, usage.input_tokens etc.
    Env: LLM_ENDPOINT_ANTHROPIC=https://api.anthropic.com/v1

Model prefix routing:
  claude-*  → anthropic
  else      → openai-compatible (gpt-*, mistral-*, llama-*, qwen-*, ...)

Ai_call_log write happens INSIDE this function — callsites don't
repeat trace boilerplate.

Return: LlmResponse. On error, `error` is set and `text=''`. Never
raises — caller inspects .error.
"""
from __future__ import annotations
import json
import logging
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from rag.ai_trace import log_llm_call

logger = logging.getLogger(__name__)


LLM_ENDPOINT_OPENAI    = os.getenv("LLM_ENDPOINT_OPENAI",    "https://api.openai.com/v1")
LLM_ENDPOINT_ANTHROPIC = os.getenv("LLM_ENDPOINT_ANTHROPIC", "https://api.anthropic.com/v1")

# API-key resolution — first-non-empty wins. LLM_API_KEY lets a local
# deployment use a single key regardless of "provider" branding.
_OPENAI_KEY_ENVS    = ("OPENAI_API_KEY", "LLM_API_KEY")
_ANTHROPIC_KEY_ENVS = ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "LLM_API_KEY")


@dataclass
class LlmResponse:
    """Return value of `call()`. On success, `text` is the model's
    reply and `tokens_in`/`out` come from the provider's usage block.
    On error, `text=""` and `error` carries `<Type>: <detail>`."""
    text:       str
    tokens_in:  Optional[int]
    tokens_out: Optional[int]
    model:      str
    latency_ms: int
    error:      Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


def _wire_for(model: str) -> str:
    """Return 'anthropic' for claude-* models, 'openai-compatible' for
    everything else. Explicit prefix beats implicit — a local Mistral
    served via vLLM's OpenAI shim is still openai-compatible."""
    m = (model or "").lower()
    if m.startswith("claude-"):
        return "anthropic"
    return "openai-compatible"


def _first_env(names: tuple[str, ...]) -> str:
    for n in names:
        v = os.getenv(n)
        if v:
            return v
    return ""


def call(
    system:      str,
    user:        str,
    model:       str,
    *,
    purpose:     str,
    max_tokens:  int   = 1500,
    temperature: float = 0.4,
    timeout_s:   float = 60.0,
    messages:    Optional[list[dict]] = None,
    tenant_id:   Optional[str]  = None,
    upload_id:   Optional[str]  = None,
    session_id:  Optional[str]  = None,
    request_id:  Optional[str]  = None,
    metadata:    Optional[dict] = None,
    response_format: Optional[dict] = None,
) -> LlmResponse:
    """Provider-neutral LLM call. Auto-logs to ai_call_log.

    `system` + `user` is the common case. For multi-turn / few-shot
    patterns, pass `messages` (a full ChatML-style array); when set,
    it overrides system + user in the request body (with the `system`
    argument still used to seed the top-level system field for
    Anthropic — Claude separates system from messages).

    On any error (HTTP, network, auth, malformed response) returns an
    LlmResponse with `error` populated and `text=""` — never raises.
    """
    wire = _wire_for(model)
    t0   = time.time()

    text        = ""
    tokens_in   = None
    tokens_out  = None
    error_type  = None
    error_detail: Optional[str] = None

    try:
        if wire == "anthropic":
            text, tokens_in, tokens_out = _call_anthropic(
                system     = system,
                user       = user,
                model      = model,
                max_tokens = max_tokens,
                temperature= temperature,
                timeout_s  = timeout_s,
                messages   = messages,
            )
        else:
            text, tokens_in, tokens_out = _call_openai_compatible(
                system          = system,
                user            = user,
                model           = model,
                max_tokens      = max_tokens,
                temperature     = temperature,
                timeout_s       = timeout_s,
                messages        = messages,
                response_format = response_format,
            )
    except urllib.error.HTTPError as e:
        error_type = "HTTPError"
        try:
            body_snip = e.read().decode()[:200]
        except Exception:
            body_snip = ""
        error_detail = f"HTTP {e.code}: {body_snip}"
    except urllib.error.URLError as e:
        error_type   = "URLError"
        error_detail = str(e)[:200]
    except Exception as e:
        error_type   = type(e).__name__
        error_detail = str(e)[:200]

    latency_ms = int((time.time() - t0) * 1000)

    # Trace — silent-fail via log_llm_call
    _prompt_for_log = _serialize_prompt(system, user, messages)
    log_llm_call(
        purpose      = purpose,
        provider     = "anthropic" if wire == "anthropic" else "openai",
        model        = model,
        latency_ms   = latency_ms,
        tokens_in    = tokens_in,
        tokens_out   = tokens_out,
        prompt       = _prompt_for_log,
        response     = text or None,
        error_type   = error_type,
        error_detail = error_detail,
        tenant_id    = tenant_id,
        upload_id    = upload_id,
        session_id   = session_id,
        request_id   = request_id,
        metadata     = metadata,
    )

    return LlmResponse(
        text       = text,
        tokens_in  = tokens_in,
        tokens_out = tokens_out,
        model      = model,
        latency_ms = latency_ms,
        error      = (f"{error_type}: {error_detail}" if error_type else None),
    )


def _serialize_prompt(system: str, user: str, messages: Optional[list[dict]]) -> str:
    """Text form of the prompt for the ai_call_log preview. Keeps
    system + user readable even in the messages= case."""
    if messages:
        parts = [f"[{m.get('role')}] {m.get('content','')}" for m in messages]
        if system and not any(m.get("role") == "system" for m in messages):
            parts.insert(0, f"[system] {system}")
        return "\n\n".join(parts)
    return f"[system] {system}\n\n[user] {user}"


def _call_anthropic(
    *,
    system:      str,
    user:        str,
    model:       str,
    max_tokens:  int,
    temperature: float,
    timeout_s:   float,
    messages:    Optional[list[dict]],
) -> tuple[str, Optional[int], Optional[int]]:
    api_key = _first_env(_ANTHROPIC_KEY_ENVS)
    if not api_key:
        raise RuntimeError("no anthropic API key (set ANTHROPIC_API_KEY)")
    # Anthropic uses `system` as a top-level field; only user/assistant
    # messages go in the array. If caller supplied messages including a
    # system role, hoist it into the top-level.
    api_messages: list[dict]
    top_system = system
    if messages:
        filtered: list[dict] = []
        for m in messages:
            if m.get("role") == "system":
                if not top_system:
                    top_system = m.get("content", "")
                continue
            filtered.append({"role": m["role"], "content": m.get("content", "")})
        api_messages = filtered
    else:
        api_messages = [{"role": "user", "content": user}]
    payload = {
        "model":       model,
        "max_tokens":  max_tokens,
        "temperature": temperature,
        "messages":    api_messages,
    }
    if top_system:
        payload["system"] = top_system
    req = urllib.request.Request(
        f"{LLM_ENDPOINT_ANTHROPIC}/messages",
        data    = json.dumps(payload).encode("utf-8"),
        headers = {
            "Content-Type":      "application/json",
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        data = json.loads(resp.read())
    text = ""
    if data.get("content"):
        # Anthropic messages/response contains a list of content blocks;
        # take the first text block.
        for block in data["content"]:
            if block.get("type") == "text":
                text = block.get("text", "")
                break
        if not text:
            text = data["content"][0].get("text", "")
    usage = data.get("usage") or {}
    return text, usage.get("input_tokens"), usage.get("output_tokens")


def _call_openai_compatible(
    *,
    system:      str,
    user:        str,
    model:       str,
    max_tokens:  int,
    temperature: float,
    timeout_s:   float,
    messages:    Optional[list[dict]],
    response_format: Optional[dict] = None,
) -> tuple[str, Optional[int], Optional[int]]:
    api_key = _first_env(_OPENAI_KEY_ENVS)
    if not api_key:
        raise RuntimeError("no openai-compatible API key (set OPENAI_API_KEY or LLM_API_KEY)")
    if messages is not None:
        api_messages = list(messages)
    else:
        api_messages = []
        if system:
            api_messages.append({"role": "system", "content": system})
        api_messages.append({"role": "user", "content": user})
    payload = {
        "model":       model,
        "max_tokens":  max_tokens,
        "temperature": temperature,
        "messages":    api_messages,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    req = urllib.request.Request(
        f"{LLM_ENDPOINT_OPENAI}/chat/completions",
        data    = json.dumps(payload).encode("utf-8"),
        headers = {
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        data = json.loads(resp.read())
    choices = data.get("choices") or []
    text    = ""
    if choices:
        msg = choices[0].get("message") or {}
        text = msg.get("content") or ""
    usage = data.get("usage") or {}
    return text, usage.get("prompt_tokens"), usage.get("completion_tokens")
