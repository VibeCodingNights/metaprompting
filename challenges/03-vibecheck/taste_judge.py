"""taste_judge.py — LLM-as-judge for aesthetic adherence.

Reads two outputs from challenges/03-vibecheck/outputs/, randomizes order,
sends them to Gemma 4 with thinking mode and the task's taste profile, and
returns a structured verdict.

Run:
    python challenges/03-vibecheck/taste_judge.py challenges/03-vibecheck/tasks/01-landing-page.md

If the output files don't exist, runs eval.py first.
"""

from __future__ import annotations

import argparse
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from shared.gemma_client import chat
from shared.taste_schema import JudgeVerdict

# Re-use the parser from eval.py.
sys.path.insert(0, str(Path(__file__).parent))
from eval import OUTPUTS_DIR, Task, parse_task  # noqa: E402

console = Console()


JUDGE_SYSTEM = """\
You are a taste judge for code outputs.

You will be given:
1. A taste profile — the aesthetic rules the output should honor
2. A judging rubric — what to reward and what to penalize
3. Two outputs labeled OUTPUT A and OUTPUT B (order randomized)

Your job:
- Reason out loud about which output better honors the taste profile.
- Cite SPECIFIC elements from the outputs. "Output A is cleaner" is not
  acceptable. "Output A uses `font-light text-2xl` and a text link, while
  Output B has `bg-purple-600 px-8 py-4 rounded-full font-bold` for the
  CTA" is acceptable.
- Identify any directives from the taste profile that you cannot find
  evidence of being honored in EITHER output. List them. Those directives
  are ineffective at shaping behavior.
- DO NOT reward length over fit. A shorter output that honors the profile
  beats a longer one that ignores it. The whole point of the rubric is
  to prevent length bias.
- Return a JudgeVerdict JSON: preferred (A or B), confidence (0–1),
  reasoning (your analysis), ineffective_directives (list of directive
  descriptions you couldn't find evidence for).
"""


def judge(task: Task, *, seed: int | None) -> JudgeVerdict:
    baseline_path = OUTPUTS_DIR / f"{task.id}.baseline.md"
    with_taste_path = OUTPUTS_DIR / f"{task.id}.with-taste.md"

    if not (baseline_path.exists() and with_taste_path.exists()):
        console.print("[yellow]Outputs not found, running eval.py first ...[/yellow]")
        subprocess.check_call(
            [sys.executable, str(Path(__file__).parent / "eval.py"), str(task.source_path)]
        )

    baseline = baseline_path.read_text()
    with_taste = with_taste_path.read_text()

    rng = random.Random(seed)
    if rng.random() < 0.5:
        a_label, a_text = "baseline", baseline
        b_label, b_text = "with-taste", with_taste
    else:
        a_label, a_text = "with-taste", with_taste
        b_label, b_text = "baseline", baseline

    console.print(Rule(f"[bold]judging — {task.id}[/bold]"))
    console.print(f"[dim]A is internally: {a_label}  ·  B is internally: {b_label}[/dim]\n")

    user_prompt = (
        "# Taste profile\n\n"
        f"{task.taste_profile}\n\n"
        "# Judging rubric\n\n"
        f"{task.rubric}\n\n"
        "# OUTPUT A\n\n"
        f"```\n{a_text}\n```\n\n"
        "# OUTPUT B\n\n"
        f"```\n{b_text}\n```\n\n"
        "Return the JudgeVerdict JSON. Cite specific lines from the outputs."
    )

    with console.status("[cyan]judge is reasoning..."):
        response = chat(
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            think="high",
            format=JudgeVerdict.model_json_schema(),
            temperature=0.3,
        )

    if response.thinking:
        console.print(Panel(response.thinking.strip(), title="thinking", border_style="dim"))

    try:
        verdict = response.parsed(JudgeVerdict)
    except Exception as exc:
        console.print("[red]Failed to parse verdict:[/red]", exc)
        console.print("\nRaw content:")
        console.print(response.content)
        raise SystemExit(1)

    # Translate the random A/B back to baseline/with-taste for the user.
    chosen_label = a_label if verdict.preferred.upper() == "A" else b_label
    return verdict, chosen_label


def render(verdict: JudgeVerdict, chosen_label: str) -> None:
    console.print(Rule("[bold]verdict[/bold]"))
    color = "green" if chosen_label == "with-taste" else "yellow"
    console.print(f"  preferred:   [bold]{verdict.preferred}[/bold]  →  [{color}]{chosen_label}[/{color}]")
    console.print(f"  confidence:  {verdict.confidence:.2f}")
    console.print()
    console.print(Panel(verdict.reasoning, title="reasoning", border_style="cyan"))

    if verdict.ineffective_directives:
        console.print()
        console.print(Panel(
            "\n".join(f"· {d}" for d in verdict.ineffective_directives),
            title="ineffective directives — no evidence in either output",
            border_style="yellow",
        ))
        console.print(
            "\n[dim]These directives didn't shape the output. Rewrite them, "
            "or feed them to the GEPA stretch in dspy_stretch.py.[/dim]"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Judge a vibe check task.")
    parser.add_argument("task", type=Path, help="Path to a task .md file")
    parser.add_argument("--seed", type=int, default=None, help="Seed the A/B randomization (default: random)")
    args = parser.parse_args()

    task = parse_task(args.task)
    verdict, chosen_label = judge(task, seed=args.seed)
    render(verdict, chosen_label)


if __name__ == "__main__":
    main()
