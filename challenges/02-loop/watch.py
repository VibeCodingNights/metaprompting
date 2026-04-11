"""watch.py — log a vibe coding session in real time.

While you work, run:
    python challenges/02-loop/watch.py --out my-session.md

You'll be prompted for each turn:
    1. paste the prompt you sent the model
    2. paste the output you got back (or a trimmed version)
    3. mark it: kept / revised / discarded
    4. write the WHY in plain English

Quit with `q` at the prompt step. The output is a session log in the
exact format `loop.py` and `surface.py` expect — feed it straight in.

This script does not call Gemma 4. It is a logger, not a model.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rich.console import Console
from rich.prompt import Prompt

console = Console()


def multiline(label: str) -> str:
    """Read a multi-line block from stdin until a line with `.` only."""
    console.print(f"[bold cyan]{label}[/bold cyan] [dim](end with a single `.` on its own line)[/dim]")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == ".":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Log a vibe coding session as you go.")
    parser.add_argument("--out", type=Path, required=True, help="Where to write the session .md")
    parser.add_argument("--title", default=None, help="Session title (you'll be prompted if omitted)")
    parser.add_argument("--surface", default=None, choices=["web", "cli", "data", "prose", "other"])
    args = parser.parse_args()

    title = args.title or Prompt.ask("session title", default=f"session {datetime.now():%Y-%m-%d %H:%M}")
    context = Prompt.ask("one-sentence context")
    surface = args.surface or Prompt.ask("surface", choices=["web", "cli", "data", "prose", "other"], default="web")

    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        f.write(f"---\ntitle: {title}\ncontext: {context}\nsurface: {surface}\n---\n")

    console.print(f"\n[green]Logging to {out}[/green]")
    console.print("[dim]Type `q` at the prompt step to finish.[/dim]\n")

    turn = 1
    while True:
        console.rule(f"[bold]Turn {turn}[/bold]")
        prompt_text = multiline(f"prompt for turn {turn}")
        if prompt_text.strip().lower() == "q":
            break

        output_text = multiline("output")

        decision = Prompt.ask("decision", choices=["kept", "revised", "discarded"], default="kept")
        notes = multiline("WHY (this is the taste signal — be specific)")

        with out.open("a") as f:
            f.write(f"\n## Turn {turn}\n\n")
            f.write(f"**Prompt:**\n> {prompt_text.replace(chr(10), chr(10) + '> ')}\n\n")
            f.write(f"**Output:**\n```\n{output_text}\n```\n\n")
            f.write(f"**Decision:** {decision}\n\n")
            f.write(f"**Notes:**\n{notes}\n\n---\n")

        turn += 1
        console.print(f"[dim]turn {turn - 1} saved.[/dim]\n")

    console.print(f"\n[green]✓[/green] {turn - 1} turns logged to {out}")
    console.print(
        "[dim]Next:[/dim] feed it into the loop:\n"
        f"  python challenges/02-loop/loop.py --session {out} --rules <your-rules-file>"
    )


if __name__ == "__main__":
    main()
