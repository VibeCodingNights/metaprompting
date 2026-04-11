# Challenge 3 · Vibe Check

> Taste directives exist. Did they actually change the output? Generate with and without. Judge the difference. The question every metaprompting tool skips: aesthetic adherence, not correctness.

## What you're doing

You have a taste directive (from Challenge 1 or 2, or hand-written). You have a coding task. You generate output **twice** — once without the directive, once with — and ask Gemma 4 to judge which one better honors the directive. Thinking mode is on, so you can read the judge's actual reasoning.

The goal isn't to pick a winner. It's to find out:
- **Does the directive change anything at all?** Sometimes the answer is no — and that means the directive is *ineffective* and needs to be rewritten.
- **Can the judge cite specific aesthetic elements?** Or does it cheat by picking the longer output?
- **(Stretch)** Can DSPy's GEPA evolve the *phrasing* of a directive into one that consistently produces aesthetically matching output?

## What's in here

```
03-vibecheck/
├── README.md          ← you are here
├── eval.py            ← generate with-directive and without-directive outputs
├── taste_judge.py     ← LLM-as-judge with thinking mode + position randomization
├── dspy_stretch.py    ← optional GEPA evolutionary search over phrasings
└── tasks/
    ├── 01-landing-page.md   ← task + injected taste profile + judging rubric
    ├── 02-error-handler.md  ← CLI/non-visual taste task
    └── 03-data-table.md     ← density/clarity tension task
```

## Prerequisites

- `setup/verify.sh` is passing.
- Ideally, you've at least *seen* a taste profile from Challenge 1 — Challenge 3 will be more interesting if you have a real one to evaluate, not just the hand-written ones in `tasks/`.

## The walk

### 1. Read one task

Open `tasks/01-landing-page.md`. You'll see:
- A **coding prompt** (the kind of thing you'd ask in Cursor)
- A **taste profile** (3–4 directives, hand-written for this task)
- A **rubric** (what the judge should look for)

### 2. Generate two outputs
```bash
python challenges/03-vibecheck/eval.py tasks/01-landing-page.md
```

This calls Gemma 4 twice with the same task — once with no taste directive in the system prompt, once with the taste profile injected. The two outputs are saved to `outputs/01-landing-page.{baseline,with-taste}.md` for inspection.

### 3. Judge the result
```bash
python challenges/03-vibecheck/taste_judge.py tasks/01-landing-page.md
```

This runs `eval.py` if outputs aren't on disk yet, then sends both outputs (in random order — A and B might be either) to Gemma 4 with thinking mode on. The judge returns:
- **Preference** — A or B
- **Confidence** — 0.0 to 1.0
- **Reasoning** — what specific elements it cited
- **Ineffective directives** — anything from the profile it could *not* find honored in either output

Read the reasoning. The interesting question isn't "did it pick right" — it's "is the reasoning grounded in the actual output, or is it post-hoc justification."

### 4. Run on all three tasks
The tasks span surfaces (web / CLI / data) so the same judge has to evaluate visual taste, voice taste, and density taste. If the judge reasoning *only* makes sense for the web task, you've found a limitation.

### 5. Find an ineffective directive
This is the most useful output of the whole challenge. A directive the judge couldn't find evidence for in *either* output is a directive that didn't change the model's behavior. That directive is broken and needs different phrasing — which is the entry point for the GEPA stretch.

## Stretch — DSPy GEPA

`dspy_stretch.py` is fully wired. It defines a DSPy module that takes a taste profile + a coding task and produces an output. GEPA (the evolutionary optimizer) then mutates the *prompt phrasings* — including the `reference` field — looking for variants that consistently produce outputs the judge prefers.

```bash
python challenges/03-vibecheck/dspy_stretch.py tasks/01-landing-page.md --auto light
```

**Warnings:**
- Locally on Ollama, GEPA is slow (~30–60s per inference, dozens of evaluations per generation). `--auto light` keeps it manageable; `medium`/`heavy` will take an hour+ on a laptop.
- Cloud endpoints are much faster but you may hit free-tier rate limits during a long GEPA run. Watch your console for 429s.
- This is a stretch goal. Don't spend the night on it unless the rest is locked in.

## What "done" looks like

- `eval.py` produces a baseline + with-taste output for at least one task.
- `taste_judge.py` returns reasoning that cites specific aesthetic elements ("the lowercase CTA in B", "the gradient background in A").
- At least one task where the directive demonstrably changes the output (the judge picks the with-taste version with confidence > 0.7).
- At least one **ineffective directive** identified — proof that not every reflection is a useful directive.
- (Bonus) GEPA produces a directive variant that beats the original by a measurable margin.

## When it goes wrong

- **"The judge always picks B."** Position bias. `taste_judge.py` randomizes order — confirm the seed flag isn't pinning it. Run multiple trials.
- **"The judge picks the longer output every time."** Your rubric is too generic. Add explicit "do not reward length over taste fit" language to the judge prompt.
- **"Both outputs look identical."** Either the directive is too vague (rewrite it) or the temperature is too low (try 0.7 in eval.py). If it's a `reference` field that says "make it clean and modern" — that's why nothing is changing. Sharpen it.
