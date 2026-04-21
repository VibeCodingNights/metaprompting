"""Read and write rules files (CLAUDE.md, AGENTS.md, .cursorrules).

The contract: configuration is sacred. Taste lives in a `## Taste` section.
Anything else in the file stays untouched. We append, we never overwrite.

Use `read_rules()` to load. Use `append_taste()` to add directives.
Use `extract_taste_section()` to pull just the taste content.

For Claude Code's nested context hierarchy, use `amend_scoped()` to write to
the right CLAUDE.md (global / project / nested directory / subagent). Use
`suggest_scope()` to pick the scope heuristically from session metadata.
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


# --- Scope-aware amend ---------------------------------------------------------
#
# Claude Code loads CLAUDE.md at multiple scopes: global (~/.claude/CLAUDE.md),
# project (<cwd>/CLAUDE.md), nested (<subdir>/CLAUDE.md — loaded on-demand from
# the working dir), and subagent (<cwd>/.claude/agents/<name>.md). Keeping taste
# relevant to scope means a "landing page density" directive lives in web/, not
# at project root.

_VALID_SCOPES = ("global", "project", "nested", "subagent")

_CLAUDE_MD_SCAFFOLD = "# Rules\n\n## Taste\n\n"


def _subagent_scaffold(name: str) -> str:
    """Minimal YAML-frontmatter scaffold for a Claude Code subagent file."""
    return (
        "---\n"
        f"name: {name}\n"
        f"description: Taste-scoped subagent — aesthetic directives for {name}.\n"
        "---\n\n"
        "# Instructions\n\n"
        "Follow the taste directives below when producing output.\n\n"
        "## Taste\n\n"
    )


def _resolve_scope_path(
    *,
    cwd: Path,
    scope: str,
    subagent_name: str | None,
    nested_dir: Path | None,
) -> Path:
    """Map (scope, args) → target file path. Raises ValueError on bad input."""
    if scope not in _VALID_SCOPES:
        raise ValueError(
            f"unknown scope {scope!r}; expected one of {_VALID_SCOPES}"
        )

    if scope == "global":
        return Path.home() / ".claude" / "CLAUDE.md"

    if scope == "project":
        return cwd / "CLAUDE.md"

    if scope == "nested":
        if nested_dir is None:
            raise ValueError("scope='nested' requires nested_dir=Path(...)")
        nd = Path(nested_dir)
        # Absolute paths bypass cwd — caller's responsibility, document it.
        if nd.is_absolute():
            return nd / "CLAUDE.md"
        # Relative paths: check `..` escapes via resolve(), but return the
        # unresolved cwd/nd form so the returned path matches the caller's cwd
        # shape (avoids macOS /var → /private/var symlink surprises).
        resolved = (cwd / nd).resolve()
        cwd_resolved = cwd.resolve()
        if not (resolved == cwd_resolved or cwd_resolved in resolved.parents):
            raise ValueError(
                f"nested_dir must stay within cwd: {nd!r} resolves outside {cwd}"
            )
        return cwd / nd / "CLAUDE.md"

    # scope == "subagent"
    if not subagent_name:
        raise ValueError("scope='subagent' requires subagent_name='...'")
    # Sanitize strictly — subagent names become filenames, so lock to a safe charset.
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", subagent_name):
        raise ValueError(
            f"subagent_name must match [A-Za-z0-9_-]+: {subagent_name!r}"
        )
    return cwd / ".claude" / "agents" / f"{subagent_name}.md"


def amend_scoped(
    directives: list[TasteDirective],
    *,
    cwd: Path,
    scope: str,
    subagent_name: str | None = None,
    nested_dir: Path | None = None,
    dedupe: bool = True,
) -> Path:
    """Append directives to a CLAUDE.md at the requested scope.

    Scopes:
        global   — ~/.claude/CLAUDE.md (cross-project register)
        project  — <cwd>/CLAUDE.md
        nested   — <nested_dir>/CLAUDE.md (e.g. web/ or cli/ subdirectories).
                   Relative paths resolve against cwd. Absolute paths are
                   allowed but bypass cwd — caller's responsibility.
        subagent — <cwd>/.claude/agents/<subagent_name>.md

    Creates parent directories and a minimal scaffold if the target doesn't
    exist yet. CLAUDE.md files get "# Rules" + "## Taste" headers; subagent
    files get YAML frontmatter (name, description) plus the taste section.

    Reuses `append_taste()` internally for dedupe / section management.

    Returns the path written.
    """
    target = _resolve_scope_path(
        cwd=cwd,
        scope=scope,
        subagent_name=subagent_name,
        nested_dir=nested_dir,
    )

    target.parent.mkdir(parents=True, exist_ok=True)

    # Scaffold if missing — append_taste treats "no file" as "empty string"
    # and would produce a file starting with "## Taste". For subagents we
    # need the YAML frontmatter, so we must write scaffold first.
    if not target.exists():
        if scope == "subagent":
            target.write_text(_subagent_scaffold(subagent_name or ""))
        else:
            target.write_text(_CLAUDE_MD_SCAFFOLD)

    append_taste(target, directives, dedupe=dedupe)
    return target


# --- Scope suggestion ----------------------------------------------------------

# Keyword sets are intentionally small and readable. This is a hackathon
# starter — attendees should feel invited to extend it, not to reverse-engineer
# a classifier.
_WEB_SESSION_HINTS = (
    "landing",
    "dashboard",
    "trading",
    "table",
    "page",
    "site",
    "web",
)
_CLI_SESSION_HINTS = (
    "cli",
    "sysadmin",
    "command",
    "terminal",
    "shell",
    "tui",
)
_WEB_PATH_HINTS = ("/web/", "/frontend/", "/dashboard/", "/site/", "/app/")
_CLI_PATH_HINTS = ("/cli/", "/cmd/", "/bin/", "/scripts/")


def suggest_scope(
    directives: list[TasteDirective],
    *,
    session_title: str = "",
    session_cwd: Path | None = None,
) -> tuple[str, dict]:
    """Heuristic scope picker for a set of directives.

    Returns (scope, kwargs) where kwargs carries the extra args amend_scoped
    needs beyond cwd and scope (e.g. {"nested_dir": Path("web")}).

    Default is ("project", {}) — when unsure, don't be clever.
    """
    dims = {d.dimension.lower() for d in directives}
    title = session_title.lower()
    cwd_str = str(session_cwd).lower() if session_cwd is not None else ""

    # Visual / layout dimensions strongly suggest web surfaces.
    web_dims = {"density", "grid", "motion", "palette", "typography", "rhythm"}
    # Text / interaction dimensions for command-line work.
    cli_dims = {"voice", "verbosity", "output"}

    has_web_dim = bool(dims & web_dims)
    has_cli_dim = bool(dims & cli_dims)

    # Title signals dominate when present — session metadata is authoritative.
    title_is_web = any(h in title for h in _WEB_SESSION_HINTS)
    title_is_cli = any(h in title for h in _CLI_SESSION_HINTS)

    # Path signals are secondary hints when title is ambiguous.
    path_is_web = any(h in cwd_str for h in _WEB_PATH_HINTS)
    path_is_cli = any(h in cwd_str for h in _CLI_PATH_HINTS)

    # density + dashboard/trading/table → web/ nested scope
    if "density" in dims and (title_is_web or path_is_web):
        return ("nested", {"nested_dir": Path("web")})

    # voice + cli/sysadmin/command → cli/ nested scope
    if "voice" in dims and (title_is_cli or path_is_cli):
        return ("nested", {"nested_dir": Path("cli")})

    # Strong web dim + web-ish title/path → web/ nested scope
    if has_web_dim and (title_is_web or path_is_web):
        return ("nested", {"nested_dir": Path("web")})

    # Strong cli dim + cli-ish title/path → cli/ nested scope
    if has_cli_dim and (title_is_cli or path_is_cli):
        return ("nested", {"nested_dir": Path("cli")})

    # Fall through: project scope. No magic.
    return ("project", {})
