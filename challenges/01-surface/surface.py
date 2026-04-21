"""surface.py — extract a structured taste profile from a vibe coding session.

Run:
    python challenges/01-surface/surface.py challenges/01-surface/sessions/01-meditation-app.md

Optional:
    --think low | medium | high     reasoning depth (default: medium)
    --temperature 0.4               sampling temperature (default: 0.4)
    --no-thinking                   disable thinking mode

What this does:
    1. Parse the session log into structured turns
    2. Build a prompt that asks Gemma 4 to read the turns and reflect
    3. Use structured output (format=Pydantic schema) to get back a TasteProfile
    4. Print the thinking trace + the directives to the terminal
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the shared/ package importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from shared.gemma_client import chat
from shared.session_parser import parse_session
from shared.taste_schema import TasteProfile

console = Console()


SYSTEM_PROMPT = """\
You've been handed a vibe coding session — prompts, outputs, and the
decisions the user kept or threw away. Read it like someone who's thrown
work away for feeling wrong.

Every output the user kept describes the universe they live in. Every
one they killed describes the universe they reject. The decisions aren't
about correctness — they're about register. Find the register. Name it
so it couldn't be anywhere else.

What should fall out: 3–5 directives, each holding one axis — register,
palette, motion, voice, density, rhythm, typography. Each directive
carries 2–5 patterns the user kept and 2–5 they killed, each pattern
traceable to a specific turn rather than paraphrased.

The `reference` field is the test. It's not advice. It's one sentence that
could only describe THIS session:

    "a page that breathes — invitation, not persuasion"
    "command-line as whispered apology"
    "density that hums — Bloomberg, not Robinhood"

"make it clean and modern" is what failure sounds like. If you write that,
you've surfaced nothing and the session notes weren't specific enough to
work with.

If the notes are thin, write fewer directives rather than padding. A
profile with two real directives beats a profile with five generic ones.
"""


def extract(session_path: Path, think: str | bool, temperature: float) -> TasteProfile:
    session = parse_session(session_path)
    if not session.turns:
        raise SystemExit(f"No turns found in {session_path}. Check the format against SESSION_FORMAT.md.")

    user_prompt = (
        "The session — kept and killed both:\n\n"
        f"```\n{session.to_prompt_block()}\n```\n\n"
        f'the session is titled "{session.title}" — carry that through as the source.'
    )

    console.print(Rule(f"[bold]surfacing taste — {session.title}[/bold]"))
    console.print(f"[dim]turns: {len(session.turns)}  ·  surface: {session.surface}[/dim]\n")

    with console.status("[bold cyan]Gemma 4 is reading the session..."):
        response = chat(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            think=think,
            format=TasteProfile.model_json_schema(),
            temperature=temperature,
        )

    if response.thinking:
        console.print(Panel(response.thinking.strip(), title="thinking", border_style="dim"))

    try:
        profile = response.parsed(TasteProfile)
    except Exception as exc:  # pydantic ValidationError or json error
        console.print("[red]Failed to parse structured output:[/red]", exc)
        console.print("\nRaw content:")
        console.print(response.content)
        raise SystemExit(1)

    return profile


def render(profile: TasteProfile) -> None:
    console.print(Rule("[bold]taste profile[/bold]"))
    console.print(f"[dim]source:[/dim] {profile.source}")
    console.print(f"[dim]directives:[/dim] {len(profile.directives)}\n")

    for i, d in enumerate(profile.directives, start=1):
        console.print(f"[bold cyan]{i}. {d.dimension}[/bold cyan]")
        console.print(f"   [italic]{d.reference}[/italic]\n")
        console.print("   [green]keep:[/green]")
        for k in d.keep:
            console.print(f"     · {k}")
        console.print("   [red]avoid:[/red]")
        for a in d.avoid:
            console.print(f"     · {a}")
        console.print()

    # The taste collapse test — print a one-line verdict.
    references = [d.reference.lower() for d in profile.directives]
    collapse_signals = ["clean", "modern", "minimal", "professional", "muted"]
    weak = [r for r in references if any(s in r for s in collapse_signals) and len(r) < 60]
    if weak:
        console.print(
            "[yellow]⚠  Taste collapse warning:[/yellow] "
            f"{len(weak)} reference field(s) read as generic advice. "
            "Sharpen the session notes (more specific 'why' on kept/discarded) "
            "and re-run with --think high."
        )
    else:
        console.print("[green]✓[/green] References look specific. Taste survived extraction.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("session", type=Path, help="Path to a session .md file")
    parser.add_argument(
        "--think",
        default="medium",
        choices=["low", "medium", "high"],
        help="Thinking depth (default: medium)",
    )
    parser.add_argument("--no-thinking", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.4)
    args = parser.parse_args()

    think: str | bool = False if args.no_thinking else args.think

    profile = extract(args.session, think=think, temperature=args.temperature)
    render(profile)


if __name__ == "__main__":
    main()
