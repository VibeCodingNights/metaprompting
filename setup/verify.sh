#!/usr/bin/env bash
# verify.sh — confirms Gemma 4 is reachable and that the three things we
# rely on actually work: thinking mode, structured output, tool calling.
#
# Both setup paths converge here. If this passes, you're ready for the challenges.

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Pick up cloud env if it was written by cloud.sh.
if [ -f "$REPO_ROOT/.env" ]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.env"
fi

# Activate venv if it exists. Don't fail if not — user may be on a system python.
if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.venv/bin/activate"
fi

python3 - <<'PY'
import sys
import json
import textwrap

from pydantic import BaseModel

# Import via the shared module so both backends work transparently.
sys.path.insert(0, ".")
from shared.gemma_client import chat, backend_info

info = backend_info()
print()
print(f"  backend: {info['mode']}")
print(f"  model:   {info['model']}")
print(f"  base:    {info['base']}")
print()

failures = []

# ---------- 1. Thinking mode ----------
print("1) thinking mode ............ ", end="", flush=True)
try:
    r = chat(
        messages=[{"role": "user", "content": "Briefly: what is the difference between configuration and taste?"}],
        think="medium",
    )
    has_thinking = bool(r.thinking) or bool(r.content)
    if not has_thinking:
        raise RuntimeError("empty response")
    print("OK")
    if r.thinking:
        print(textwrap.indent(r.thinking[:200].strip() + ("…" if len(r.thinking) > 200 else ""), "       "))
except Exception as e:
    print(f"FAIL — {e}")
    failures.append(("thinking", str(e)))

# ---------- 2. Structured output ----------
print("2) structured output ........ ", end="", flush=True)

class Probe(BaseModel):
    register: str
    reference: str

try:
    r = chat(
        messages=[
            {
                "role": "user",
                "content": (
                    "Describe the aesthetic register of a meditation app called Still. "
                    "Return JSON with fields `register` (one or two words) and "
                    "`reference` (one evocative sentence)."
                ),
            }
        ],
        format=Probe.model_json_schema(),
        temperature=0.4,
    )
    parsed = r.parsed(Probe)
    print("OK")
    print(f"       register={parsed.register!r}")
    print(f"       reference={parsed.reference!r}")
except Exception as e:
    print(f"FAIL — {e}")
    failures.append(("structured_output", str(e)))

# ---------- 3. Tool calling ----------
print("3) tool calling ............. ", end="", flush=True)

def write_taste_directive(dimension: str, reference: str) -> str:
    """Persist a single taste directive. Used as a probe target."""
    return f"stored {dimension}: {reference}"

try:
    r = chat(
        messages=[
            {
                "role": "user",
                "content": (
                    "Use the write_taste_directive tool to record a directive for the "
                    "dimension 'register' with a reference describing a calm meditation app."
                ),
            }
        ],
        tools=[write_taste_directive],
    )
    if not r.tool_calls:
        # Some cloud providers may inline the JSON in content. Accept that too.
        if "write_taste_directive" in (r.content or ""):
            print("OK (inline)")
        else:
            raise RuntimeError("no tool calls in response")
    else:
        print("OK")
        print(f"       called: {r.tool_calls[0]['name']}")
        print(f"       args:   {r.tool_calls[0]['arguments']}")
except Exception as e:
    print(f"FAIL — {e}")
    failures.append(("tool_calling", str(e)))

print()
if failures:
    print("Some checks failed:")
    for name, msg in failures:
        print(f"  - {name}: {msg}")
    print()
    print("Common fixes:")
    print("  - cloud:  did you source .env?  (run:  source .env)")
    print("  - cloud:  is your API key still valid?  Try a different provider via setup/cloud.sh")
    print("  - local:  is the Ollama daemon running?  curl http://localhost:11434/api/tags")
    print("  - local:  did the model finish pulling?  ollama list")
    sys.exit(1)

print("All three checks passed. You're ready.")
print("Pick a challenge:  challenges/01-surface  ·  challenges/02-loop  ·  challenges/03-vibecheck")
PY
