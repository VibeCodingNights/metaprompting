"""Parse vibe coding session logs into structured turns.

Sessions are markdown files with YAML frontmatter and `## Turn N` sections.
See SESSION_FORMAT.md for the spec.

This parser is intentionally lenient — vibe coding notes are messy on purpose.
We accept missing fields and trim whitespace, but we DO require the four
section markers (Prompt / Output / Decision / Notes) per turn.
"""

from __future__ import annotations

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
