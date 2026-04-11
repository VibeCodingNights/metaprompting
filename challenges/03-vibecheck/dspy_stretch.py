"""dspy_stretch.py — GEPA evolutionary optimization of taste directive phrasings.

The stretch challenge. Slow on local Ollama (~30–60s per inference, dozens
of evaluations per generation). Cloud endpoints are faster but watch your
free-tier rate limits during a long run.

Run:
    python challenges/03-vibecheck/dspy_stretch.py challenges/03-vibecheck/tasks/01-landing-page.md --auto light

What this does:
    1. Define a DSPy module that takes (task, taste_profile) → output
    2. Define a metric that calls the LLM judge on (output, taste_profile)
       and returns the judge's confidence as a score (0..1)
    3. Run GEPA to mutate the prompt phrasings — including the `reference`
       field — looking for variants that consistently produce outputs the
       judge prefers
    4. Print the best phrasings discovered

This is fully wired. Run it and watch DSPy explore the prompt space.
If you prefer to read code over running it, the most interesting part is
the metric — that's where the taste judge becomes a fitness function.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.rule import Rule

from eval import Task, parse_task  # noqa: E402
from shared.gemma_client import _using_cloud  # noqa: E402

console = Console()


def configure_dspy() -> None:
    """Wire dspy.LM to the same backend the rest of the repo uses."""
    import dspy

    if _using_cloud():
        api_base = os.environ["GEMMA_API_BASE"]
        api_key = os.environ["GEMMA_API_KEY"]
        model = os.environ.get("GEMMA_MODEL", "gemma-4-27b-it")
        # DSPy understands the OpenAI-compatible URL via the openai/ prefix.
        lm = dspy.LM(
            model=f"openai/{model}",
            api_base=api_base,
            api_key=api_key,
            temperature=0.7,
            max_tokens=2048,
        )
    else:
        model = os.environ.get("GEMMA_MODEL", "gemma4")
        lm = dspy.LM(
            model=f"ollama_chat/{model}",
            api_base="http://localhost:11434",
            temperature=0.7,
            max_tokens=2048,
        )
    dspy.configure(lm=lm)


def build_program():
    """One module: take a task and a taste profile, return the code."""
    import dspy

    class TasteAwareCoder(dspy.Signature):
        """Write code for the task in a way that honors the taste profile."""

        task: str = dspy.InputField(desc="The coding task")
        taste_profile: str = dspy.InputField(desc="The taste rules to honor")
        output: str = dspy.OutputField(desc="The code")

    return dspy.ChainOfThought(TasteAwareCoder)


def build_metric(task: Task):
    """A metric that calls the taste judge on (output, taste_profile) and returns 0..1."""
    from shared.gemma_client import chat
    from shared.taste_schema import JudgeVerdict
    from taste_judge import JUDGE_SYSTEM  # reuse the judge prompt

    def metric(example, prediction, trace=None) -> float:
        # In GEPA, "example" is a dummy holder; the real comparison is between
        # the prediction's output and the (fixed) baseline output we cached.
        candidate = prediction.output if hasattr(prediction, "output") else str(prediction)

        baseline_path = Path(__file__).parent / "outputs" / f"{task.id}.baseline.md"
        baseline = baseline_path.read_text() if baseline_path.exists() else ""

        # Random A/B not needed here — we're scoring candidate vs. fixed baseline,
        # and we always put candidate as B so the fitness signal is consistent.
        user_prompt = (
            "# Taste profile\n\n"
            f"{task.taste_profile}\n\n"
            "# Judging rubric\n\n"
            f"{task.rubric}\n\n"
            "# OUTPUT A\n\n"
            f"```\n{baseline}\n```\n\n"
            "# OUTPUT B\n\n"
            f"```\n{candidate}\n```\n"
        )
        try:
            r = chat(
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM},
                    {"role": "user", "content": user_prompt},
                ],
                format=JudgeVerdict.model_json_schema(),
                think="medium",
                temperature=0.3,
            )
            v = r.parsed(JudgeVerdict)
        except Exception as e:
            console.print(f"[yellow]judge failed: {e}[/yellow]")
            return 0.0

        # If the judge picks B (our candidate), score = confidence. Otherwise (1 - confidence) * 0.5.
        if v.preferred.upper() == "B":
            return float(v.confidence)
        return float(1.0 - v.confidence) * 0.5

    return metric


def make_trainset(task: Task, n: int = 5):
    """Create N copies of the same task — GEPA needs a small set to evaluate phrasings."""
    import dspy

    return [
        dspy.Example(task=task.prompt, taste_profile=task.taste_profile).with_inputs("task", "taste_profile")
        for _ in range(n)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="GEPA over taste directive phrasings.")
    parser.add_argument("task", type=Path, help="Path to a task .md file")
    parser.add_argument(
        "--auto",
        choices=["light", "medium", "heavy"],
        default="light",
        help="GEPA budget. light is the only option that's reasonable on local Ollama.",
    )
    parser.add_argument("--trainset-size", type=int, default=4)
    args = parser.parse_args()

    task = parse_task(args.task)

    console.print(Rule(f"[bold]GEPA stretch — {task.id}[/bold]"))
    console.print(
        "[yellow]This will take a while. Local Ollama: ~30–60s per inference, "
        "dozens of evaluations. Cloud: faster but watch rate limits.[/yellow]\n"
    )

    try:
        import dspy
        from dspy.teleprompt import GEPA
    except ImportError:
        raise SystemExit("dspy-ai not installed. Run: pip install -r setup/requirements.txt")

    configure_dspy()

    program = build_program()
    metric = build_metric(task)
    trainset = make_trainset(task, n=args.trainset_size)

    console.print(f"[dim]GEPA budget: {args.auto}  ·  trainset size: {len(trainset)}[/dim]\n")

    optimizer = GEPA(metric=metric, auto=args.auto)
    compiled = optimizer.compile(program, trainset=trainset)

    console.print(Rule("[bold]optimized program[/bold]"))
    console.print(
        "[dim]The optimized prompts are inside the compiled program. "
        "Inspect them via:[/dim]\n  compiled.predictors()[0].signature\n"
    )
    for i, predictor in enumerate(compiled.predictors()):
        console.print(f"[bold]predictor {i}[/bold]")
        console.print(repr(predictor.signature))
        console.print()


if __name__ == "__main__":
    main()
