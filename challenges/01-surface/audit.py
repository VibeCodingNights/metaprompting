"""audit.py — audit a rules file for stated config vs implied taste.

The bring-your-own onramp. Drop your `.cursorrules`, `CLAUDE.md`, or
`AGENTS.md` into bring-your-own/, then:

    python challenges/01-surface/audit.py bring-your-own/your-file.md

You will get back:
    · how many config rules you have
    · how many taste directives you have (almost always: 0)
    · the taste DEMOCRATICALLY IMPLIED by your phrasing but never stated
    · a one-paragraph summary of the gap

The implied taste is the interesting output. A rules file full of "no
comments unless necessary" and "prefer composition over inheritance" has
a voice — terse, opinionated, low ceremony. The model can name that voice.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from shared.gemma_client import chat
from shared.rules_io import read_rules
from shared.taste_schema import AuditFinding

console = Console()


SYSTEM_PROMPT = """\
You audit rules files (CLAUDE.md, .cursorrules, AGENTS.md) for unstated taste.

A rules file usually contains configuration: build commands, lint rules,
test runners, "use pnpm", "no any types", etc. That's the structural layer
and it is solved.

What is NOT in the file but is implied by it: taste. The voice in which
the rules are written, the things they pointedly leave out, the patterns
they nudge toward without legislating. A file full of "do not add comments
unless they explain a non-obvious why" implies a voice that values terse,
intentional code. A file full of "always include error handling for X, Y,
Z" implies a defensive register.

Your job:
- Read the rules file content provided.
- Count how many CONFIGURATION rules exist (lines that legislate
  structure: tooling, lint, build, test, syntax, types).
- Count how many TASTE DIRECTIVES exist (lines that legislate aesthetics:
  voice, register, density, palette, mood). Be strict — if it doesn't
  read as taste, it isn't.
- Then surface 2–4 taste directives that are IMPLIED by the file but
  never stated. These are inferences, not instructions — the user did
  not write them, the user's phrasing implies them.
- Each implied directive must follow the TasteDirective schema:
  dimension, keep (2–5), avoid (2–5), and a `reference` that is ONE
  evocative sentence, NOT generic advice.
- Write a one-paragraph `summary` of the gap. Lead with the numbers.
  Then describe the unspoken voice. End with the consequence — what
  kind of output the user is currently getting that they don't realize
  is shaped by their unstated taste.

Return ONLY valid JSON conforming to the AuditFinding schema.
"""


def audit(rules_path: Path, think: str | bool, temperature: float) -> AuditFinding:
    rf = read_rules(rules_path)
    if not rf.raw.strip():
        raise SystemExit(f"{rules_path} is empty or doesn't exist.")

    console.print(Rule(f"[bold]auditing — {rules_path.name}[/bold]"))
    console.print(
        f"[dim]raw size: {len(rf.raw)} chars  ·  "
        f"local config rule estimate: {rf.count_config_rules()}  ·  "
        f"local taste directive estimate: {rf.count_taste_directives()}[/dim]\n"
    )

    user_prompt = (
        "Audit this rules file. Return the AuditFinding JSON.\n\n"
        f"```markdown\n{rf.raw}\n```\n"
    )

    with console.status("[bold cyan]Gemma 4 is reading your rules..."):
        response = chat(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            think=think,
            format=AuditFinding.model_json_schema(),
            temperature=temperature,
        )

    if response.thinking:
        console.print(Panel(response.thinking.strip(), title="thinking", border_style="dim"))

    try:
        finding = response.parsed(AuditFinding)
    except Exception as exc:
        console.print("[red]Failed to parse structured output:[/red]", exc)
        console.print("\nRaw content:")
        console.print(response.content)
        raise SystemExit(1)

    return finding


def render(finding: AuditFinding) -> None:
    console.print(Rule("[bold]audit[/bold]"))
    console.print(f"  config rules:      [bold]{finding.config_rule_count}[/bold]")
    console.print(f"  taste directives:  [bold]{finding.taste_directive_count}[/bold]")
    console.print()

    if finding.implied_taste:
        console.print("[bold]implied taste — never stated, but in your phrasing:[/bold]\n")
        for i, d in enumerate(finding.implied_taste, start=1):
            console.print(f"[cyan]{i}. {d.dimension}[/cyan]")
            console.print(f"   [italic]{d.reference}[/italic]")
            console.print(f"   [green]keep:[/green]  {'; '.join(d.keep)}")
            console.print(f"   [red]avoid:[/red] {'; '.join(d.avoid)}")
            console.print()

    console.print(Panel(finding.summary, title="the gap", border_style="cyan"))
    console.print(
        "\n[dim]Next:[/dim] feed one of these implied directives into "
        "Challenge 2's loop, or use the gap as input to Challenge 3."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("rules_file", type=Path, help="Path to a rules file (CLAUDE.md, .cursorrules, AGENTS.md...)")
    parser.add_argument("--think", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--no-thinking", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.4)
    args = parser.parse_args()

    think: str | bool = False if args.no_thinking else args.think

    finding = audit(args.rules_file, think=think, temperature=args.temperature)
    render(finding)


if __name__ == "__main__":
    main()
