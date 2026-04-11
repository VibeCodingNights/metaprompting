"""loop.py — the self-amending taste loop.

Four named stages. Two are wired (observe, amend). Two are stubs (reflect,
generalize) — that's the work.

Run:
    python challenges/02-loop/loop.py \
        --session challenges/02-loop/sample_session/session.md \
        --rules   challenges/02-loop/sample_session/starting_rules.md

The rules file will gain a `## Taste` section. Configuration above it is
left untouched.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from shared.gemma_client import chat
from shared.rules_io import append_taste, read_rules
from shared.session_parser import Session, parse_session
from shared.taste_schema import TasteDirective

console = Console()


# --------------------------------------------------------------------------- #
# 1. OBSERVE — wired. Just parse the session.
# --------------------------------------------------------------------------- #

def observe(session_path: Path) -> Session:
    """Load the session log from disk and structure it."""
    session = parse_session(session_path)
    console.print(Rule(f"[bold]observe[/bold] — {session.title}"))
    console.print(f"[dim]{len(session.turns)} turns · surface: {session.surface}[/dim]\n")
    return session


# --------------------------------------------------------------------------- #
# 2. REFLECT — stub. Use thinking mode to reason ACROSS turns.
# --------------------------------------------------------------------------- #

REFLECT_SYSTEM = """\
You are reflecting on a vibe coding session to find the *patterns* the user
is enforcing across multiple turns.

Read all the turns. Pay particular attention to:
- The contrast between turns marked `kept` and turns marked `discarded`. The
  kept ones describe the universe the user lives in. The discarded ones
  describe the universe they reject.
- Patterns that hold across more than one turn. A taste rule that only
  shows up once is a preference. A pattern that holds across turns is a
  *register*.
- Specificity in the notes. The user's `Notes:` field is the signal — the
  more concrete the why, the more specific the pattern.

Do NOT extract directives yet. Reflect in prose. Find 3–5 distinct patterns.
For each one, state what the pattern is and cite the specific turns that
support it. Be willing to say "this pattern only shows up once, weak signal".
"""


def reflect(session: Session) -> str:
    """Use thinking mode to reason about cross-turn patterns. Return the prose reflection."""
    # ─────────────────────────────────────────────────────────────────────
    # TODO (you): build the user message and call chat() with think='high'.
    # Return both the thinking trace AND the content as one string so the
    # next stage can read both.
    #
    # Hints:
    #   - The session has a .to_prompt_block() method that gives you a
    #     compact string of all the turns.
    #   - Pass think='high' for deep reasoning. Lower think levels collapse
    #     the patterns into a list of observations instead of a synthesis.
    #   - response.thinking is the trace; response.content is the prose.
    # ─────────────────────────────────────────────────────────────────────
    raise NotImplementedError("fill in reflect()")


# --------------------------------------------------------------------------- #
# 3. GENERALIZE — stub. Use tool-calling to materialize directives.
# --------------------------------------------------------------------------- #

GENERALIZE_SYSTEM = """\
You generalize a reflection on a vibe coding session into structured taste
directives.

You will be given:
1. The original session
2. A reflection on patterns across turns

Your job: call the `write_taste_directive` tool 3–5 times. Each call captures
ONE dimension of taste (register, palette, motion, voice, density, ...).

Rules for each directive:
- `dimension` is one word or short phrase.
- `keep` is 2–5 patterns that the user maintained, traceable to specific turns.
- `avoid` is 2–5 patterns that the user rejected, traceable to specific turns.
- `reference` is ONE evocative sentence. NOT advice. NOT "make it clean".
  Something like "a page that breathes — invitation, not persuasion".

If the reflection is thin, write fewer directives. Do not pad.
"""


def generalize(session: Session, reflection: str) -> list[TasteDirective]:
    """Materialize directives via tool-calling. Each tool call becomes one directive."""

    collected: list[TasteDirective] = []

    def write_taste_directive(
        dimension: str,
        keep: list[str],
        avoid: list[str],
        reference: str,
    ) -> str:
        """Persist a single taste directive. Call once per dimension you want to legislate.

        Args:
            dimension: One word or short phrase. e.g. 'register', 'voice', 'density'.
            keep: 2–5 patterns to maintain, traceable to specific turns.
            avoid: 2–5 patterns to reject, traceable to specific turns.
            reference: One evocative sentence capturing the feeling. Not advice.
        """
        try:
            d = TasteDirective(dimension=dimension, keep=keep, avoid=avoid, reference=reference)
            collected.append(d)
            return f"recorded: {dimension}"
        except Exception as e:
            return f"rejected: {e}"

    # ─────────────────────────────────────────────────────────────────────
    # TODO (you): call chat() with the system prompt above, the session +
    # reflection in the user message, and tools=[write_taste_directive].
    #
    # Hints:
    #   - The model may call write_taste_directive multiple times in one
    #     response. Each call appends to `collected` via the closure.
    #   - Some local backends (Ollama) call tools differently than cloud
    #     ones — but our shared client normalizes to a common shape, so
    #     you only need to handle the case where response.tool_calls is a
    #     list of {name, arguments} dicts. Iterate it and CALL THE LOCAL
    #     write_taste_directive function with the arguments. The model
    #     proposing a tool call doesn't actually run the tool — you do.
    #   - If a single response yields zero tool_calls, the model probably
    #     wrote the directives in content as JSON. Be lenient: if collected
    #     is still empty after processing, you may want to retry once with
    #     a sharper instruction.
    # ─────────────────────────────────────────────────────────────────────
    raise NotImplementedError("fill in generalize()")


# --------------------------------------------------------------------------- #
# 4. AMEND — wired. Append to the rules file's ## Taste section.
# --------------------------------------------------------------------------- #

def amend(rules_path: Path, directives: list[TasteDirective]) -> None:
    """Append directives to the rules file's `## Taste` section. Configuration is preserved."""
    if not directives:
        console.print("[yellow]No directives to amend.[/yellow]")
        return

    before = read_rules(rules_path)
    append_taste(rules_path, directives, dedupe=True)
    after = read_rules(rules_path)

    console.print(Rule("[bold]amend[/bold]"))
    console.print(
        f"[dim]config rules:[/dim]    {before.count_config_rules()} → {after.count_config_rules()} "
        f"[dim](should be unchanged)[/dim]"
    )
    console.print(
        f"[dim]taste directives:[/dim] {before.count_taste_directives()} → {after.count_taste_directives()}\n"
    )
    console.print(f"[green]✓[/green] amended {rules_path}")


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(description="The self-amending taste loop.")
    parser.add_argument("--session", type=Path, required=True, help="Path to the session .md")
    parser.add_argument("--rules", type=Path, required=True, help="Path to the rules file to amend")
    parser.add_argument(
        "--copy-rules",
        action="store_true",
        help="Copy the rules file to .amended.md before mutating, so the original stays clean.",
    )
    args = parser.parse_args()

    rules_path = args.rules
    if args.copy_rules:
        copy = rules_path.with_suffix(".amended.md")
        shutil.copy(rules_path, copy)
        rules_path = copy
        console.print(f"[dim]copy →[/dim] {copy}\n")

    session = observe(args.session)

    reflection = reflect(session)
    console.print(Panel(reflection.strip(), title="reflection", border_style="cyan"))

    directives = generalize(session, reflection)
    console.print(Rule("[bold]generalize[/bold]"))
    console.print(f"[dim]extracted {len(directives)} directives[/dim]\n")
    for d in directives:
        console.print(f"  · [cyan]{d.dimension}[/cyan] — [italic]{d.reference}[/italic]")
    console.print()

    amend(rules_path, directives)


if __name__ == "__main__":
    main()
