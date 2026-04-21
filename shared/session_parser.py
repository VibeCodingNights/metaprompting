"""Parse vibe coding session logs into structured turns.

Sessions are markdown files with YAML frontmatter and `## Turn N` sections.
See SESSION_FORMAT.md for the spec.

This parser is intentionally lenient — vibe coding notes are messy on purpose.
We accept missing fields and trim whitespace, but we DO require the four
section markers (Prompt / Output / Decision / Notes) per turn.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

DECISIONS = {"kept", "revised", "discarded"}


@dataclass
class Turn:
    index: int
    prompt: str
    output: str
    decision: str
    notes: str

    def to_prompt_block(self) -> str:
        """Compact representation, used when feeding turns into Gemma 4."""
        return (
            f"### Turn {self.index}\n"
            f"PROMPT: {self.prompt.strip()}\n"
            f"OUTPUT (trimmed): {self.output.strip()[:600]}\n"
            f"DECISION: {self.decision}\n"
            f"NOTES: {self.notes.strip()}\n"
        )


@dataclass
class Session:
    title: str
    context: str
    surface: str
    turns: list[Turn] = field(default_factory=list)
    source_path: str = ""

    def to_prompt_block(self) -> str:
        """Format the whole session for the model. Keep it within token budgets."""
        header = (
            f"SESSION: {self.title}\n"
            f"CONTEXT: {self.context}\n"
            f"SURFACE: {self.surface}\n"
            f"TURNS: {len(self.turns)}\n"
        )
        body = "\n".join(t.to_prompt_block() for t in self.turns)
        return f"{header}\n{body}"


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_TURN_RE = re.compile(r"^##\s+Turn\s+(\d+)\s*$", re.MULTILINE)
_FIELD_RE = re.compile(
    r"\*\*(Prompt|Output|Decision|Notes):\*\*\s*\n?(.*?)(?=\n\*\*(?:Prompt|Output|Decision|Notes):\*\*|\Z)",
    re.DOTALL,
)


def parse_session(path: str | Path) -> Session:
    text = Path(path).read_text()

    title, context, surface = "untitled", "", "other"
    fm = _FRONTMATTER_RE.match(text)
    if fm:
        for line in fm.group(1).splitlines():
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            k, v = k.strip().lower(), v.strip()
            if k == "title":
                title = v
            elif k == "context":
                context = v
            elif k == "surface":
                surface = v
        text = text[fm.end() :]

    turns: list[Turn] = []
    turn_starts = list(_TURN_RE.finditer(text))
    for i, m in enumerate(turn_starts):
        idx = int(m.group(1))
        start = m.end()
        end = turn_starts[i + 1].start() if i + 1 < len(turn_starts) else len(text)
        chunk = text[start:end]

        fields = {fname.lower(): _strip_block(body) for fname, body in _FIELD_RE.findall(chunk)}
        decision = fields.get("decision", "").lower().strip().split()[0] if fields.get("decision") else ""
        if decision not in DECISIONS:
            decision = "kept"  # be lenient on input but flag downstream

        turns.append(
            Turn(
                index=idx,
                prompt=fields.get("prompt", ""),
                output=fields.get("output", ""),
                decision=decision,
                notes=fields.get("notes", ""),
            )
        )

    return Session(
        title=title,
        context=context,
        surface=surface,
        turns=turns,
        source_path=str(path),
    )


def _strip_block(text: str) -> str:
    """Drop trailing `---` separators, leading blockquote markers, and excess whitespace."""
    text = text.strip()
    text = re.sub(r"\n---\s*$", "", text)
    # Strip leading "> " from each line — the session format renders prompts as
    # blockquotes for readability, but the model wants clean text.
    text = "\n".join(re.sub(r"^>\s?", "", line) for line in text.splitlines())
    return text.strip()


def load_all_sessions(directory: str | Path) -> list[Session]:
    """Load every .md session in a directory, sorted by filename."""
    return [parse_session(p) for p in sorted(Path(directory).glob("*.md"))]


# ---------------------------------------------------------------------------
# Claude Code JSONL session support
#
# Claude Code records every session to ~/.claude/projects/<encoded-cwd>/<uuid>.jsonl
# Each line is an event; only `user` and `assistant` events carry conversational
# signal. We trim aggressively so downstream code sees something shaped like a
# vibe coding session even though no one wrote decision/notes by hand.
# ---------------------------------------------------------------------------

# Tool calls whose *input* is where generated code actually lives — preserve full.
_CODE_TOOLS = {"Write", "Edit", "NotebookEdit"}
# Read-y / search-y tools — abbreviate to a single line.
_NAV_TOOLS = {"Bash", "Read", "Grep", "Glob", "WebFetch", "WebSearch"}


def _encode_cwd(cwd: Path) -> str:
    """Claude Code projects directory uses non-alphanumeric -> '-' on the absolute cwd."""
    absolute = str(Path(cwd).resolve())
    return re.sub(r"[^A-Za-z0-9]", "-", absolute)


def discover_current_session(cwd: Path) -> Path | None:
    """Find the most-recently-modified .jsonl session file for this cwd.

    Returns None if the project directory doesn't exist or contains no session
    files. Skips hidden files, sub-directories, and the `.continuation_cache.json`
    noise file.
    """
    projects_root = Path.home() / ".claude" / "projects" / _encode_cwd(Path(cwd))
    if not projects_root.is_dir():
        return None

    candidates: list[Path] = []
    for p in projects_root.iterdir():
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.name == "continuation_cache.json":
            continue
        if p.suffix != ".jsonl":
            continue
        candidates.append(p)

    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _abbreviate_tool(name: str, inp: dict) -> str:
    """One-line summary of a nav/search tool call."""
    if not isinstance(inp, dict):
        return f"[tool] {name}: {str(inp)[:80]}"
    # Pull the most human-readable field we can find.
    for key in ("description", "command", "query", "pattern", "url", "file_path", "path"):
        if key in inp and isinstance(inp[key], str) and inp[key].strip():
            return f"[tool] {name}: {inp[key].strip()[:80]}"
    return f"[tool] {name}: {json.dumps(inp, default=str)[:80]}"


def _render_assistant_blocks(blocks: list) -> str:
    """Concatenate the kept assistant-content blocks into a single string.

    - text blocks: kept full
    - tool_use Write/Edit/NotebookEdit: kept full (this is where code lives)
    - tool_use nav/search tools: one-line abbreviation
    - tool_use other: one-line abbreviation of json.dumps(input)
    - thinking blocks: dropped
    - empty text: dropped
    """
    parts: list[str] = []
    for b in blocks:
        if not isinstance(b, dict):
            continue
        btype = b.get("type")
        if btype == "text":
            text = (b.get("text") or "").strip()
            if text:
                parts.append(text)
        elif btype == "tool_use":
            name = b.get("name") or "UnknownTool"
            inp = b.get("input") or {}
            if name in _CODE_TOOLS:
                try:
                    pretty = json.dumps(inp, indent=2, default=str)
                except (TypeError, ValueError):
                    pretty = str(inp)
                parts.append(f"[tool] {name}:\n{pretty}")
            elif name in _NAV_TOOLS:
                parts.append(_abbreviate_tool(name, inp))
            else:
                try:
                    blob = json.dumps(inp, default=str)
                except (TypeError, ValueError):
                    blob = str(inp)
                parts.append(f"[tool] {name}: {blob[:80]}")
        # thinking + everything else -> drop
    return "\n\n".join(parts).strip()


def _extract_user_prompt(ev: dict) -> str | None:
    """Pull a real user prompt from a `user` event, or None if it's tool_result noise.

    - string content -> return as prompt
    - list content -> drop, unless it contains a real `text` block alongside
      tool_results (rare, but in that case keep only the text)
    """
    msg = ev.get("message") or {}
    content = msg.get("content")
    if isinstance(content, str):
        stripped = content.strip()
        return stripped or None
    if isinstance(content, list):
        texts = [
            (b.get("text") or "").strip()
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        texts = [t for t in texts if t]
        if texts:
            return "\n\n".join(texts)
        return None
    return None


def parse_jsonl_session(
    path: Path,
    *,
    window_turns: int = 5,
    title: str | None = None,
) -> Session:
    """Parse a Claude Code JSONL session file into a Session.

    Lossy but usable: we group events into turns anchored on real user prompts,
    keep the assistant's text + code-writing tool calls, and abbreviate
    nav/search tool calls. Decision defaults to "kept" because Claude Code
    doesn't record explicit keep/discard markers.
    """
    path = Path(path)
    events: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # lenient — skip malformed lines

    # Group events into turns. A turn starts at a user plain-text event and
    # runs until the next one (or EOF). Events that aren't user/assistant are
    # ignored. User events that are pure tool_result noise are also ignored —
    # they don't start or break a turn.
    turns_raw: list[dict] = []  # {"prompt": str, "assistant_blocks": list[list]}
    current: dict | None = None

    for ev in events:
        etype = ev.get("type")
        if etype not in ("user", "assistant"):
            continue

        if etype == "user":
            prompt = _extract_user_prompt(ev)
            if prompt is None:
                # tool_result noise — doesn't start a turn
                continue
            if current is not None:
                turns_raw.append(current)
            current = {"prompt": prompt, "assistant_blocks": []}
        else:  # assistant
            if current is None:
                # assistant content with no preceding user prompt — skip
                continue
            msg = ev.get("message") or {}
            blocks = msg.get("content")
            if isinstance(blocks, list):
                current["assistant_blocks"].append(blocks)

    if current is not None:
        turns_raw.append(current)

    # Apply windowing: keep only the last N turns.
    if window_turns > 0:
        windowed = turns_raw[-window_turns:]
    else:
        windowed = turns_raw

    # Render each turn's assistant blocks; drop turns where the assistant
    # contributed no kept content after trimming would leave us with nothing —
    # but the spec says drop *assistant events* with no kept content, not whole
    # turns. An empty-output turn (e.g. user's last message before session end)
    # is still useful signal, so we keep the turn with an empty output.
    turns: list[Turn] = []
    for idx, t in enumerate(windowed, start=1):
        rendered_chunks: list[str] = []
        for blocks in t["assistant_blocks"]:
            rendered = _render_assistant_blocks(blocks)
            if rendered:
                rendered_chunks.append(rendered)
        output = "\n\n".join(rendered_chunks)
        turns.append(
            Turn(
                index=idx,
                prompt=t["prompt"],
                output=output,
                decision="kept",
                notes="",
            )
        )

    # Title: explicit > first prompt (80 chars) > fallback with file stem.
    if title:
        resolved_title = title
    elif turns_raw and turns_raw[0]["prompt"].strip():
        first = turns_raw[0]["prompt"].strip().splitlines()[0]
        resolved_title = first[:80]
    else:
        resolved_title = f"claude code session {path.stem[:8]}"

    # Surface: cheap inference from cwd recorded in events; otherwise "claude-code".
    surface = "claude-code"
    for ev in events:
        cwd = ev.get("cwd")
        if not cwd:
            continue
        low = cwd.lower()
        if any(hint in low for hint in ("/web", "site", "frontend", "ui")):
            surface = "web"
            break
        if any(hint in low for hint in ("/cli", "command", "tool")):
            surface = "cli"
            break
        if any(hint in low for hint in ("data", "dashboard", "analytics")):
            surface = "data"
            break

    return Session(
        title=resolved_title,
        context=f"Claude Code session from {path.name}",
        surface=surface,
        turns=turns,
        source_path=str(path),
    )
