"""Read and write rules files (CLAUDE.md, AGENTS.md, .cursorrules).

The contract: configuration is sacred. Taste lives in a `## Taste` section.
Anything else in the file stays untouched. We append, we never overwrite.

Use `read_rules()` to load. Use `append_taste()` to add directives.
Use `extract_taste_section()` to pull just the taste content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .taste_schema import TasteDirective

TASTE_HEADING = "## Taste"
TASTE_SECTION_RE = re.compile(
    r"(?ms)^##\s+Taste\s*$(.*?)(?=^##\s+|\Z)",
)


@dataclass
class RulesFile:
    path: Path
    raw: str
    config_lines: list[str] = field(default_factory=list)
    taste_block: str = ""

    @property
    def has_taste_section(self) -> bool:
        return bool(self.taste_block.strip())

    def count_config_rules(self) -> int:
        """Best-effort count of bullet rules outside the Taste section."""
        non_taste = TASTE_SECTION_RE.sub("", self.raw)
        return sum(1 for line in non_taste.splitlines() if line.strip().startswith(("- ", "* ", "1.", "2.")))

    def count_taste_directives(self) -> int:
        """Count `### <dimension>` subheadings inside the Taste section."""
        if not self.taste_block:
            return 0
        return len(re.findall(r"(?m)^###\s+\S+", self.taste_block))


def read_rules(path: str | Path) -> RulesFile:
    p = Path(path)
    raw = p.read_text() if p.exists() else ""
    taste_match = TASTE_SECTION_RE.search(raw)
    taste_block = taste_match.group(1).strip() if taste_match else ""
    config_lines = [
        line for line in raw.splitlines() if line.strip() and not line.strip().startswith("#")
    ]
    return RulesFile(path=p, raw=raw, config_lines=config_lines, taste_block=taste_block)


def render_directive(directive: TasteDirective) -> str:
    """Render one directive as a markdown subsection."""
    keep = ", ".join(directive.keep)
    avoid = ", ".join(directive.avoid)
    return (
        f"### {directive.dimension}\n"
        f"{directive.reference}\n\n"
        f"**Keep:** {keep}\n\n"
        f"**Avoid:** {avoid}\n"
    )


def append_taste(
    path: str | Path,
    directives: list[TasteDirective],
    *,
    dedupe: bool = True,
) -> str:
    """Append directives to the rules file's `## Taste` section.

    If the section doesn't exist, create it at the end of the file.
    Configuration above the section is left untouched.

    If `dedupe` is True, replace any existing `### <dimension>` subsection
    with the new directive instead of duplicating.

    Returns the new file contents (and writes them).
    """
    p = Path(path)
    raw = p.read_text() if p.exists() else ""

    existing = TASTE_SECTION_RE.search(raw)
    if existing:
        taste_body = existing.group(1).strip()
    else:
        taste_body = ""

    # Build a dimension → rendered string map of existing directives.
    existing_subs: dict[str, str] = {}
    if taste_body:
        parts = re.split(r"(?m)^###\s+", taste_body)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            dim = part.splitlines()[0].strip()
            existing_subs[dim] = "### " + part

    for d in directives:
        rendered = render_directive(d)
        if dedupe:
            existing_subs[d.dimension] = rendered
        else:
            existing_subs[f"{d.dimension}::{len(existing_subs)}"] = rendered

    new_taste = "\n".join(existing_subs.values()).strip()
    new_section = f"{TASTE_HEADING}\n\n{new_taste}\n"

    if existing:
        new_raw = raw[: existing.start()] + new_section + raw[existing.end() :]
    else:
        sep = "\n\n" if raw and not raw.endswith("\n") else "\n"
        new_raw = raw + sep + new_section

    p.write_text(new_raw)
    return new_raw


def extract_taste_section(path: str | Path) -> str:
    """Just give me the taste block, no config."""
    return read_rules(path).taste_block
