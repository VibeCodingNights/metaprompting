"""Unified Gemma 4 client — cloud endpoint OR local Ollama.

If GEMMA_API_BASE is set, use the OpenAI-compatible client against a cloud
provider (Google AI Studio, OpenRouter, Groq). Otherwise, use the Ollama
Python client against a local `gemma4` model.

Both paths support:
  - thinking mode (think=True or think='low'|'medium'|'high')
  - structured output (format=Model.model_json_schema())
  - tool calling (tools=[func])

Attendees: you probably don't need to touch this. Import `chat` and go.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable

# Default model name. Overridable via GEMMA_MODEL env var for people using
# a different tag (e.g. 'gemma4:27b', 'gemma-4-27b-it' on cloud providers).
DEFAULT_LOCAL_MODEL = os.environ.get("GEMMA_MODEL", "gemma4")
DEFAULT_CLOUD_MODEL = os.environ.get("GEMMA_MODEL", "gemma-4-27b-it")


@dataclass
class ChatResponse:
    """Unified response shape across both backends."""

    content: str
    thinking: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    raw: Any = None

    def parsed(self, schema_cls: Any) -> Any:
        """Parse `content` as JSON and validate against a Pydantic model."""
        data = json.loads(self.content) if isinstance(self.content, str) else self.content
        return schema_cls.model_validate(data)


def _using_cloud() -> bool:
    return bool(os.environ.get("GEMMA_API_BASE"))


def chat(
    messages: list[dict[str, str]],
    *,
    think: bool | str = False,
    format: dict | None = None,
    tools: list[Callable] | list[dict] | None = None,
    temperature: float = 0.7,
    model: str | None = None,
) -> ChatResponse:
    """Send a chat request to Gemma 4.

    Args:
        messages: OpenAI-style list of {role, content} dicts.
        think: Enable thinking. True for default, or 'low' | 'medium' | 'high'.
        format: Pydantic JSON schema for structured output. Pass
            `Model.model_json_schema()`.
        tools: List of Python functions (Ollama) or tool schemas (cloud) to expose.
        temperature: Sampling temperature. Taste extraction tolerates 0.3–0.7.
        model: Override the model name. Defaults to `gemma4` locally,
            `gemma-4-27b-it` on cloud.

    Returns:
        ChatResponse with `content`, `thinking`, and `tool_calls`.
    """
    if _using_cloud():
        return _chat_cloud(
            messages,
            think=think,
            format=format,
            tools=tools,
            temperature=temperature,
            model=model or DEFAULT_CLOUD_MODEL,
        )
    return _chat_local(
        messages,
        think=think,
        format=format,
        tools=tools,
        temperature=temperature,
        model=model or DEFAULT_LOCAL_MODEL,
    )


# --------------------------------------------------------------------------- #
# Local backend — Ollama Python client
# --------------------------------------------------------------------------- #


def _chat_local(messages, *, think, format, tools, temperature, model) -> ChatResponse:
    try:
        import ollama
    except ImportError as exc:
        raise RuntimeError(
            "ollama package not installed. Run: pip install -r setup/requirements.txt"
        ) from exc

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "options": {"temperature": temperature},
    }
    if think:
        kwargs["think"] = think
    if format is not None:
        kwargs["format"] = format
    if tools is not None:
        kwargs["tools"] = tools

    response = ollama.chat(**kwargs)
    msg = response["message"] if isinstance(response, dict) else response.message

    content = msg.get("content", "") if isinstance(msg, dict) else (msg.content or "")
    thinking = msg.get("thinking", "") if isinstance(msg, dict) else getattr(msg, "thinking", "") or ""
    tool_calls_raw = (
        msg.get("tool_calls", []) if isinstance(msg, dict) else getattr(msg, "tool_calls", []) or []
    )
    tool_calls = [
        {
            "name": (tc.get("function", {}).get("name") if isinstance(tc, dict) else tc.function.name),
            "arguments": (
                tc.get("function", {}).get("arguments") if isinstance(tc, dict) else tc.function.arguments
            ),
        }
        for tc in tool_calls_raw
    ]

    return ChatResponse(content=content, thinking=thinking, tool_calls=tool_calls, raw=response)


# --------------------------------------------------------------------------- #
# Cloud backend — OpenAI-compatible endpoint
# --------------------------------------------------------------------------- #


def _chat_cloud(messages, *, think, format, tools, temperature, model) -> ChatResponse:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai package not installed. Run: pip install -r setup/requirements.txt"
        ) from exc

    api_key = os.environ.get("GEMMA_API_KEY")
    api_base = os.environ.get("GEMMA_API_BASE")
    if not api_key or not api_base:
        raise RuntimeError(
            "GEMMA_API_KEY and GEMMA_API_BASE must be set for cloud mode. "
            "Run ./setup/cloud.sh or unset GEMMA_API_BASE for local mode."
        )

    client = OpenAI(api_key=api_key, base_url=api_base)

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    # Structured output via response_format. Most OpenAI-compatible providers
    # accept json_schema; fall back to json_object if the provider complains.
    if format is not None:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "structured_output", "schema": format, "strict": True},
        }

    # Tool calling — accept either Python callables or raw OpenAI tool specs.
    if tools is not None:
        kwargs["tools"] = [_callable_to_tool(t) if callable(t) else t for t in tools]

    # Cloud providers don't all expose thinking-mode toggles uniformly. We pass
    # it through as a hint in the system message when requested; providers that
    # support Gemini-style thinking will honor the `reasoning_effort` field.
    if think:
        level = think if isinstance(think, str) else "medium"
        kwargs["extra_body"] = {"reasoning_effort": level}

    try:
        response = client.chat.completions.create(**kwargs)
    except TypeError:
        # Older openai SDK versions don't accept extra_body — retry without it.
        kwargs.pop("extra_body", None)
        response = client.chat.completions.create(**kwargs)

    choice = response.choices[0]
    content = choice.message.content or ""
    tool_calls_raw = choice.message.tool_calls or []
    tool_calls = [
        {"name": tc.function.name, "arguments": json.loads(tc.function.arguments or "{}")}
        for tc in tool_calls_raw
    ]

    # Some cloud providers surface reasoning on the message object.
    thinking = getattr(choice.message, "reasoning", "") or ""

    return ChatResponse(content=content, thinking=thinking, tool_calls=tool_calls, raw=response)


def _callable_to_tool(func: Callable) -> dict:
    """Turn a plain Python callable into an OpenAI tool spec via its signature + docstring."""
    import inspect

    sig = inspect.signature(func)
    properties = {}
    required = []
    for name, param in sig.parameters.items():
        properties[name] = {"type": "string", "description": f"Parameter {name}"}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip() or f"Call {func.__name__}",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


# --------------------------------------------------------------------------- #
# Environment reporting
# --------------------------------------------------------------------------- #


def backend_info() -> dict[str, str]:
    """Return a one-liner about which backend is active. Used by verify.sh."""
    if _using_cloud():
        return {
            "mode": "cloud",
            "base": os.environ.get("GEMMA_API_BASE", ""),
            "model": DEFAULT_CLOUD_MODEL,
        }
    return {
        "mode": "local",
        "base": "ollama (http://localhost:11434)",
        "model": DEFAULT_LOCAL_MODEL,
    }
