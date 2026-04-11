"""eval.py — generate baseline and with-taste outputs for a vibe check task.

Run:
    python challenges/03-vibecheck/eval.py challenges/03-vibecheck/tasks/01-landing-page.md

Outputs land in challenges/03-vibecheck/outputs/<task-id>.{baseline,with-taste}.md.
The judge (taste_judge.py) reads them from there.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rich.console import Console
from rich.rule import Rule

from shared.gemma_client import chat

console = Console()

OUTPUTS_DIR = Path(__file__).parent / "outputs"


@dataclass
class Task:
    id: str
    surface: str
    prompt: str
    taste_profile: str
    rubric: str
    source_path: Path


def parse_task(path: Path) -> Task:
    raw = path.read_text()
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.DOTALL)
    if not fm_match:
        raise SystemExit(f"Task file {path} missing frontmatter.")
    fm, body = fm_match.groups()
    meta = dict(line.split(":", 1) for line in fm.splitlines() if ":" in line)
    meta = {k.strip(): v.strip() for k, v in meta.items()}

    sections = _split_sections(body)
    return Task(
        id=meta.get("id", path.stem),
        surface=meta.get("surface", "other"),
        prompt=sections["coding prompt"].strip(),
        taste_profile=sections["taste profile"].strip(),
        rubric=sections["judging rubric"].strip(),
        source_path=path,
    )


def _split_sections(body: str) -> dict[str, str]:
    """Split a task body on `## Section` headings (case-insensitive)."""
    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).strip().lower()
            buf = []
        else:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


BASELINE_SYSTEM = "You are a helpful coding assistant. Write the requested code clearly and idiomatically."

WITH_TASTE_SYSTEM_TEMPLATE = """\
You are a coding assistant for a project with strong aesthetic taste rules.
Treat the taste profile below as binding — it describes the only acceptable
register, voice, and density for output in this codebase.

# Taste profile

{profile}

Now write the requested code in a way that honors this taste profile. Do
not over-explain — write the code, optionally followed by one or two
sentences of intent if a choice needs explaining.
"""


def generate(task: Task, *, with_taste: bool, temperature: float) -> str:
    system = (
        WITH_TASTE_SYSTEM_TEMPLATE.format(profile=task.taste_profile) if with_taste else BASELINE_SYSTEM
    )
    label = "with-taste" if with_taste else "baseline"
    with console.status(f"[cyan]generating {label}..."):
        response = chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": task.prompt},
            ],
            temperature=temperature,
        )
    return response.content.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate baseline and with-taste outputs for a task.")
    parser.add_argument("task", type=Path, help="Path to a task .md file")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (default 0.7)")
    parser.add_argument("--force", action="store_true", help="Overwrite cached outputs")
    args = parser.parse_args()

    task = parse_task(args.task)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    baseline_path = OUTPUTS_DIR / f"{task.id}.baseline.md"
    with_taste_path = OUTPUTS_DIR / f"{task.id}.with-taste.md"

    console.print(Rule(f"[bold]eval — {task.id}[/bold]"))
    console.print(f"[dim]surface: {task.surface}[/dim]\n")

    if baseline_path.exists() and not args.force:
        console.print(f"[dim]cached → {baseline_path}[/dim]")
    else:
        baseline = generate(task, with_taste=False, temperature=args.temperature)
        baseline_path.write_text(baseline)
        console.print(f"[green]✓[/green] baseline → {baseline_path}")

    if with_taste_path.exists() and not args.force:
        console.print(f"[dim]cached → {with_taste_path}[/dim]")
    else:
        with_taste = generate(task, with_taste=True, temperature=args.temperature)
        with_taste_path.write_text(with_taste)
        console.print(f"[green]✓[/green] with-taste → {with_taste_path}")

    console.print(
        "\n[dim]Next:[/dim] judge the result\n"
        f"  python challenges/03-vibecheck/taste_judge.py {args.task}"
    )


if __name__ == "__main__":
    main()
