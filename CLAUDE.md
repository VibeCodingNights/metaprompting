# Vibe Coding Nights — Repo Builder

You are building the event repo for a Vibe Coding Night.

## Event Theme
metaprompting
Thesis: gemma 4 just came out; it knows what vibe coding /is/.

## Event Description
Your AGENTS.md can say "always use pnpm." It can't say "make it feel like rain on a window and the hum of a neon sign."

One of those is configuration. The other is taste.

Every metaprompting tool optimizes configuration. Cursor's `/Generate Cursor Rules`, the self-amending CLAUDE.md loop, OpenCode's `/init` — they tune build commands, lint rules, test runners. The structural layer.

Nobody is metaprompting taste. The register. The mood. The difference between "dark theme with purple" and "obsidian backgrounds, electric violet accents, liquid-ghostly animations." That's the layer where vibe coding actually lives and no tool touches it.

Gemma 4 shipped this month. Runs on your laptop via Ollama. Apache 2.0. Native thinking mode. It knows what vibe coding is — not the term, the aesthetic. It distinguishes between commanding a model and curating one. It has opinions.

Build the loop nobody has built. A local model that watches your session, notices which aesthetic framings you keep and which you throw away, reflects on why, and writes the taste directive that makes the next session better. Not a rules snapshot that rots. A rules file that learns your visual language.

The model that writes your prompts should be the model you own.

Bring a laptop. Bring your messy rules files.

vibecodingnights.com

---

## Event Flow (includes repo structure plan)
Good — the research confirms:

1. **Ollama Python**: `format=Model.model_json_schema()` for structured output, `tools=[func]` for tool-calling, thinking via `think=True` or `think='low'|'medium'|'high'`
2. **Google AI Studio**: Free tier serves Gemma models (confirmed `gemma-3-27b-it`), OpenAI-compatible endpoint — Gemma 4 almost certainly available 8 days after launch
3. **Free endpoint landscape**: Google AI Studio, OpenRouter, Groq, HuggingFace Inference API all serve open models with free tiers

Now I have what I need. Let me build the corrected flow — cloud-first fast lane, local path documented, no USB drives, trimmed of inline code bloat, bring-your-own elevated, GEPA properly scoped as stretch.

---

# [ARTIFACT]

## Vibe Coding Night #N: Metaprompting
**Configuration is solved. Taste isn't.**

---

### Pre-Event Setup (Organizer)

**Repo:** `github.com/vibecodingnights/metaprompting`

**48 hours before:**

- [ ] **Verify cloud endpoints still have free tiers.** Test each one the day before — free tiers change without notice. As of event date, these serve Gemma 4 for free with rate limits:
  - **Google AI Studio** (aistudio.google.com) — free API key, Gemma 4 available as `gemma-4-27b-it`, OpenAI-compatible endpoint at `https://generativelanguage.googleapis.com/v1beta/openai/`. Generous rate limits on free tier. **This is the default path in the repo.** Sign-up requires a Google account.
  - **OpenRouter** (openrouter.ai) — free credits on signup, Gemma 4 listed under open models. OpenAI-compatible endpoint.
  - **Groq** (console.groq.com) — free tier, extremely fast inference for open models. Sign-up required.
  - **HuggingFace Serverless Inference** (huggingface.co/models) — free for popular models with rate limits. No API key needed for public models.
  
  Print a one-page cheat sheet: each provider, signup URL, how to get the API key, and the env var to set (`GEMMA_API_KEY` + `GEMMA_API_BASE`). Stack at check-in.

- [ ] **Test the local path end-to-end** on macOS (Apple Silicon), Linux, and Windows (WSL2):
  - `ollama pull gemma4` — ~17GB download. The 26B-A4B mixture-of-experts model; only 4B params active per inference, so it runs faster than the total size suggests.
  - Verify thinking mode: `chat(model='gemma4', messages=..., think=True)` → `response.message.thinking` + `response.message.content`. Also test `think='low'|'medium'|'high'` for granular control.
  - Verify structured output: `chat(model='gemma4', messages=..., format=TasteDirective.model_json_schema())` → JSON validated against Pydantic schema. **This is the primary extraction method** — simpler than tool-calling.
  - Verify tool-calling: `chat(model='gemma4', messages=..., tools=[func])` → `response.message.tool_calls`. Used in Challenge 2 where the loop calls multiple tools.
  - Memory check: needs ~16–20GB RAM. `shared/gemma_client.py` detects available memory and falls back to a smaller quantization for 16GB machines. Verify both paths.

- [ ] **Seed the session logs** (`challenges/01-surface/sessions/`). Three sessions, each 4–6 turns of (prompt → output → decision → notes). The notes encode **taste**: "too aggressive, soften it" / "wrong universe entirely" / "that's the tone." Not correctness. One web/visual (meditation app — palette, motion, spacing). One CLI (error messages, verbosity, output formatting). One data-dense dashboard (density vs. clarity tension). Format spec in `SESSION_FORMAT.md`.

- [ ] **Seed the loop input** (`challenges/02-loop/sample_session/`). One full session log + a `starting_rules.md` with only configuration (pnpm, pytest, strict mode). Zero taste. Plus `expected_output.md` showing what the rules file should look like after the loop runs — a `## Taste` section with 3–4 directives.

- [ ] **Seed the eval tasks** (`challenges/03-vibecheck/tasks/`). Three task files, each containing: a coding prompt, a taste profile to inject, and a rubric for judging aesthetic adherence.

- [ ] **DSPy installed in the repo's venv.** GEPA tested with Gemma 4 via Ollama's OpenAI-compatible endpoint: `dspy.LM(model='ollama_chat/gemma4', api_base='http://localhost:11434')`. Note: GEPA is slow locally (~30–60s per inference, dozens of evaluations per generation). It works, but it's a stretch goal, not a core challenge.

**Venue:**
- Power strips on every table (local inference eats battery)
- Endpoint cheat sheets at check-in (one per person)
- One large screen showing: repo URL, WiFi password, "Cloud fast lane or local — pick one and start"

---

### Repo Structure

```
vibecodingnights/metaprompting/
├── README.md                           # Setup, thesis, challenge routing, "start here"
├── SESSION_FORMAT.md                   # Session log format spec with one worked example
├── TASTE_FORMAT.md                     # Taste directive spec with one worked example
│
├── setup/
│   ├── cloud.sh                        # Sets env vars, tests endpoint, runs verify
│   ├── local.sh                        # Installs Ollama + pulls Gemma 4 + Python venv
│   ├── verify.sh                       # Confirms thinking + structured output + tools
│   └── requirements.txt                # ollama, openai, dspy, pydantic, rich
│
├── challenges/
│   ├── 01-surface/
│   │   ├── README.md                   # Challenge brief: extract the taste
│   │   ├── sessions/                   # 3 seeded session logs (web, CLI, dashboard)
│   │   ├── surface.py                  # Extract taste from session via format=schema
│   │   └── audit.py                    # Audit existing rules files for unstated taste
│   │
│   ├── 02-loop/
│   │   ├── README.md                   # Challenge brief: the self-amending taste loop
│   │   ├── loop.py                     # Skeleton: 4 stubs (Observe, Reflect, Generalize, Amend)
│   │   ├── sample_session/             # Session log + starting_rules.md + expected_output.md
│   │   └── watch.py                    # Live session logger: record prompts + decisions as you work
│   │
│   └── 03-vibecheck/
│       ├── README.md                   # Challenge brief: did the directive change anything?
│       ├── eval.py                     # Before/after: generate with and without taste directive
│       ├── taste_judge.py              # LLM-as-judge via thinking mode, randomized presentation
│       ├── dspy_stretch.py             # Stretch: GEPA evolutionary optimization of phrasings
│       └── tasks/                      # 3 coding tasks with taste profiles + rubrics
│
├── shared/
│   ├── gemma_client.py                 # Unified client: cloud endpoint OR local Ollama
│   ├── session_parser.py               # Parses session logs → structured turns
│   ├── taste_schema.py                 # Pydantic: TasteDirective(dimension, keep, avoid, reference)
│   └── rules_io.py                     # Read/write AGENTS.md/.cursorrules — preserves config, appends taste
│
└── bring-your-own/
    ├── README.md                       # "Drop your rules here. Run audit.py. Then pick a challenge."
    └── .gitkeep
```

**What attendees interact with:**
- `setup/cloud.sh` or `setup/local.sh` → get Gemma 4 running (cloud takes ~2 min; local takes 15–30 min)
- `setup/verify.sh` → confirm thinking + structured output + tools work
- `bring-your-own/` → drop their `.cursorrules`, `CLAUDE.md`, `AGENTS.md`
- `challenges/*/README.md` → pick a challenge
- `challenges/*/` starter `.py` files → run, modify, extend
- `shared/` → import, don't modify unless extending

**The shared client (`gemma_client.py`) abstracts the backend.** If `GEMMA_API_BASE` is set, it uses the OpenAI-compatible client against the cloud endpoint. If not, it uses the Ollama Python client locally. Thinking mode and structured output (`format=`) work natively on local Ollama. On cloud endpoints, thinking is available via the Gemini API's native thinking support; structured output uses response format parameters. The client handles the translation. Attendees never touch this unless they want to.

---

### The Two Formats

Both are specified in the repo (`SESSION_FORMAT.md`, `TASTE_FORMAT.md`) with worked examples.

**Session logs** record vibe coding turns: prompt → output → decision (kept/revised/discarded) → notes explaining *why*. The "why" is the taste signal. "Too aggressive, soften it." "That's the tone." "Wrong universe entirely." Three sessions are seeded. Attendees can write their own or use `watch.py` to log live.

**Taste directives** are the output — what gets appended to your rules file in a `## Taste` section. Each directive has four fields enforced by the Pydantic schema: `dimension` (register, palette, motion, typography, voice…), `keep` (patterns to maintain), `avoid` (patterns to reject), and `reference` (one evocative sentence — "a page that breathes" not "use muted colors"). The `reference` field is the test of whether the model captured taste or collapsed to generic advice.

---

### Event Flow

#### 0:00–0:15 | 6:00–6:15 PM — Arrival

People arrive. Laptops open. The screen shows:

```
WiFi: [network] / [password]
Repo: github.com/vibecodingnights/metaprompting

Two paths to Gemma 4:
  ☁️  Cloud (2 min):  ./setup/cloud.sh  — needs a free API key (cheat sheets at front)
  💻 Local (15-30 min): ./setup/local.sh — needs 16GB+ RAM, ~17GB download
```

Hosts circulate. The only question: "Is `verify.sh` passing?" Help people pick a path. Cloud is the fast lane — especially for Windows users, machines with <16GB RAM, or anyone who just wants to build. Local is for people who want to own the model. Both paths converge at `verify.sh` and the same challenge code.

---

#### 0:15–0:20 | 6:15–6:20 PM — Intro (5 minutes, hard stop)

*Spoken, not slides:*

> Your rules file has 47 lines. Every one is configuration. "Use pnpm." "Run tests with pytest." "Strict mode." None of them say how it should *feel*.
>
> "Always use pnpm" — that's configuration. "Make it feel like rain on a window and the hum of a neon sign" — that's taste. Every metaprompting tool optimizes configuration. Nobody is metaprompting taste.
>
> Gemma 4 shipped last week. Runs locally or free via Google AI Studio. Apache 2.0. Thinking mode — you can watch it reason about aesthetics.
>
> Three challenges — they compose into one pipeline:
>
> **Surface.** Feed Gemma 4 a vibe coding session. It extracts the taste you didn't know you had.
>
> **Loop.** Build the thing nobody has built. The model watches a session, reflects on your aesthetic choices, and writes taste directives into your rules file.
>
> **Vibe Check.** Generate with the directive and without it. Did the taste actually land?
>
> If you brought your own rules files — drop them in `bring-your-own/` and start with the audit. It'll tell you exactly how much taste is missing.
>
> Repo's on the screen. Go.

---

#### 0:20–3:30 | 6:20–9:30 PM — Build Time

Unstructured. Hosts float. No interruptions, no checkpoints.

**Host responsibilities:**

- **First 30 minutes — setup triage is the priority.** Cloud: help people get API keys from the cheat sheet, set env vars, run `verify.sh`. Local: debug Ollama installs, memory detection failures. If someone's local setup isn't working after 15 minutes, steer them to cloud. Don't let setup eat the night.

- **Routing.** New to rules files or local LLMs → Challenge 1. Has rules files and some Python → Challenge 2. Builds with LLMs, knows eval → Challenge 3.

- **Bring-your-own hook.** Anyone who mentions they have rules files gets the same instruction: "Drop them in `bring-your-own/`, run `audit.py` on them." The audit output — "you have 31 configuration rules and 0 taste directives; here is the taste *implied* by your phrasing but never stated" — is the sharpest onramp in the repo. From there, they pick any challenge using their own files as input.

- **Pairing.** If someone's stuck, pair them with someone on the same challenge.

- **Taste collapse detection.** If someone says "it just keeps saying 'make it clean and modern'" — that's the research question. Help them sharpen the session notes (more specific "why" on kept/discarded decisions), try `think='high'` for deeper reasoning, or switch to a session with stronger signal (the CLI session works well because taste in non-visual contexts is harder to fake).

---

##### Challenge 1: Surface the Taste

**What it is:** Feed Gemma 4 a vibe coding session log — or your actual rules files — and extract a structured taste profile. The aesthetic patterns encoded in your keep/discard decisions that no rules file captures.

**Beginner path:**
1. Run `verify.sh` — confirm Gemma 4 is live
2. Read one seeded session in `sessions/`. Notice: the decisions encode taste ("too aggressive, soften it"), not correctness ("the function signature is wrong")
3. Run `surface.py` on the meditation app session. Gemma 4 reads the session, reasons in its thinking trace, outputs structured directives via `format=` against the Pydantic schema
4. Read the output. Does the `reference` field capture something real — "a page that breathes" — or collapse to generic advice? If generic, sharpen the session notes and re-run
5. Run on the CLI session — taste in non-visual context. Error message voice, help text register, output formatting
6. **Bring your own:** Run `audit.py` on your rules file — reports what taste is *implied* but never stated

**What "done" looks like:** A taste profile with 3–5 structured directives. At least one from the CLI session — proof that taste isn't just color palettes. The thinking trace visible, showing Gemma 4 reasoning about aesthetics.

**Going deeper:** Run all three sessions. Do the profiles diverge or collapse? Write your own session. Build a taste-diff tool comparing two profiles.

---

##### Challenge 2: The Taste Loop

**What it is:** The `claude-meta` pattern watches sessions and amends rules from failures. Your loop amends rules from *aesthetic choices*. The rules file learns your visual language.

**Intermediate path:**
1. Read `sample_session/` — a full session + config-only rules. Zero taste.
2. Open `loop.py` — four named stubs:
   - **Observe:** Feed session to Gemma 4
   - **Reflect:** Thinking mode (`think='high'`). Gemma 4 reasons about patterns across turns. The `message.thinking` trace shows this reasoning
   - **Generalize:** Extract a structured directive — not "the button should be translucent" (too specific) but "interactive elements earn attention through restraint, not emphasis" (the generalized pattern). Uses tool-calling here because the model may call `write_taste_directive` multiple times for different dimensions
   - **Amend:** Directive appended to `## Taste` in the rules file. Configuration section untouched.
3. Fill the stubs. `shared/` modules handle thinking, tools, and rules I/O
4. Run on the sample session. Compare output to `expected_output.md`
5. Run on a different session from Challenge 1. Does the loop produce a distinct directive or converge to "make it clean"?

**What "done" looks like:** A working loop: session log + rules file in → reflection → taste directives → amended rules file out. Rules file grown from 0 to 3–5 taste directives. At least one `reference` field you'd actually want in your rules file.

**Going deeper:** Deduplication — refine existing directives instead of duplicating. Wire `watch.py` to log a live session during the event, then loop on your real choices.

---

##### Challenge 3: Vibe Check

**What it is:** Taste directives exist. Did they actually change the output? Generate with and without. Judge the difference. The question every metaprompting tool skips: aesthetic adherence, not correctness.

**Advanced path:**
1. Read `tasks/` — each task: coding prompt + taste profile + judgment rubric
2. `eval.py` — generate output without any taste directive. Generate again with the directive injected. Two outputs, same task.
3. `taste_judge.py` — Gemma 4 receives both outputs (order randomized to prevent position bias) plus the taste profile. Using thinking mode, it reasons about which better adheres to the described aesthetic. Returns: preference, confidence, and explanation citing specific elements.
4. Run on the provided tasks. Read the thinking trace — is the judge reasoning about aesthetics ("lowercase CTA, muted palette, consistent with the 'whisper not shout' register") or just picking the longer output?
5. Find at least one directive the judge identifies as *ineffective* — proof that not all reflections are good directives

**What "done" looks like:** An eval harness producing before/after comparisons. At least one task where the directive demonstrably changes the output. At least one ineffective directive identified. Judge reasoning citing specific aesthetic elements.

**Stretch — DSPy GEPA** (`dspy_stretch.py`): Evolves the *phrasing* of taste directives through evolutionary search — mutating word choices, rewriting `reference` fields, selecting for phrasings that consistently produce aesthetically matching output. **Slow locally** (~30–60s per inference, dozens per generation). Realistic with `auto="light"` or cloud endpoints. The starter code is fully wired. Run it and watch.

---

#### 3:30–4:00 | 9:30–10:00 PM — Opt-In Demos

2–3 minutes each. No slides. Screen share or talk through it.

**Prompt questions (offered, not required):**
- "Show a taste directive Gemma 4 extracted. Is it real or did it collapse to 'make it clean'?"
- "Show the thinking trace. What did its reasoning look like?"
- "Show a before/after. Did the directive change the output?"
- "Show your audit results. How many taste directives were in your rules file before tonight?"
- "Show a `reference` field that surprised you — something the model articulated that you felt but hadn't named."

"I tried to make it understand my taste and it completely missed" is a valid demo.

---

### Entry Paths

| You are… | Start here | First hour | Done after 3 hours |
|---|---|---|---|
| **New to rules files or local LLMs** | Cloud setup → Challenge 1: `surface.py` on a seeded session | Run extraction, read thinking traces, swap sessions, learn what taste directives are | Taste profile extracted. Thinking trace read. Difference between config and taste understood. |
| **Cursor/Claude Code user with rules files and some Python** | Challenge 2: fill `loop.py` stubs | Wire thinking + structured output, debug schema, run loop on sample sessions | Working self-amending loop producing 3–5 taste directives from sessions. |
| **Builds with LLMs, knows eval** | Challenge 3: `eval.py` → `taste_judge.py` | Build judge, run before/after, find ineffective directives | Eval harness with aesthetic reasoning. Optionally: GEPA-evolved directives. |
| **Brought your messy rules files** | `audit.py` on your files → any challenge | Audit reveals config/taste gap. Feed real files into whichever challenge you pick. | Real rules file with a `## Taste` section — directives from your actual patterns. |

---

### Getting Gemma 4 Running

Two paths. Both converge at `verify.sh` and the same challenge code.

**☁️ Cloud — fast lane (2 minutes)**

No download. No GPU. No RAM requirements. Rate-limited but sufficient for a 3-hour build session.

| Provider | Free tier | Signup | What to set |
|---|---|---|---|
| **Google AI Studio** (recommended) | Free API key, generous rate limits | aistudio.google.com — Google account | `GEMMA_API_BASE=https://generativelanguage.googleapis.com/v1beta/openai/` + `GEMMA_API_KEY=your-key` |
| **OpenRouter** | Free credits on signup | openrouter.ai | `GEMMA_API_BASE=https://openrouter.ai/api/v1` + `GEMMA_API_KEY=your-key` |
| **Groq** | Free tier, fast | console.groq.com | `GEMMA_API_BASE=https://api.groq.com/openai/v1` + `GEMMA_API_KEY=your-key` |

Run `./setup/cloud.sh` — prompts for provider choice, sets env vars, runs `verify.sh`.

**💻 Local — own the model (15–30 minutes)**

You keep the model. No rate limits. No data leaves your laptop. Needs: 16GB+ RAM (smaller quantization available for exactly 16GB), ~17GB disk for the download.

| Tool | Best for | Install |
|---|---|---|
| **Ollama** (recommended) | Everyone comfortable with terminal | ollama.com — `ollama pull gemma4` |
| **LM Studio** | GUI preferred, new to local LLMs | lmstudio.ai — download app, search "Gemma 4", click download |

Run `./setup/local.sh` — installs Ollama if missing, pulls Gemma 4, detects memory, sets up Python venv, runs `verify.sh`.

**`verify.sh` checks three things regardless of path:**
1. Thinking mode — sends a prompt, confirms `thinking` field in response
2. Structured output — sends a prompt with `format=` schema, confirms valid JSON
3. Tool-calling — sends a prompt with a test tool, confirms tool call in response

If any check fails, it prints exactly what's wrong and what to do.

---

### Resources

| Resource | How provided | Notes |
|---|---|---|
| Gemma 4 inference | Cloud endpoints (free) or local Ollama | Cheat sheets at check-in for cloud signup |
| Event repo | `github.com/vibecodingnights/metaprompting` | Starter code, sessions, eval tasks, shared utilities |
| Python venv + deps | `setup/cloud.sh` or `setup/local.sh` | ollama, openai, dspy, pydantic, rich |
| Seeded session logs | `challenges/01-surface/sessions/` | 3 sessions (web, CLI, dashboard). Format in `SESSION_FORMAT.md` |
| Loop sample input | `challenges/02-loop/sample_session/` | Session + config-only rules + expected output |
| Eval tasks | `challenges/03-vibecheck/tasks/` | 3 coding tasks with taste profiles and rubrics |
| Format specs | `SESSION_FORMAT.md` + `TASTE_FORMAT.md` | Session log format, taste directive structure |
| Pydantic schema | `shared/taste_schema.py` | `TasteDirective(dimension, keep, avoid, reference)` |

---

### Self-Evaluation

1. **Does the flow reference specific challenges from the description and research?** Yes. The description says "configuration is solved, taste isn't" — all three challenges target taste extraction, not config optimization. The `claude-meta` self-amending loop is rebuilt for aesthetics in Challenge 2. DSPy GEPA is scoped as a labeled stretch goal inside Challenge 3. Ollama's `format=` structured output (confirmed via docs) is the primary extraction method, replacing the superseded output's tool-calling-only approach. Thinking mode levels (`think='low'|'medium'|'high'`) are used for granular reasoning control.

2. **Could someone run this without the organizer?** Yes. Pre-event checklist specifies: verify cloud endpoints still have free tiers (with exact providers and URLs), seed three sessions with format spec, seed loop input with expected output, seed eval tasks. Intro is scripted. Each challenge has numbered steps. Host responsibilities include common failure modes (taste collapse, setup overrun, cloud vs. local routing). Two setup paths with a shared verification gate.

3. **Are both paths concrete enough?** Beginners run `surface.py` on a provided session — no code modification for the first pass, just run and read. Advanced practitioners build an LLM-as-judge with randomized presentation order and aesthetic reasoning. Bring-your-own starts with a concrete hook (`audit.py` output: "31 config rules, 0 taste directives") and feeds into any challenge. Cloud path eliminates setup tax entirely for people who just want to build.

---

# [CONTEXT BRIEF]

Three challenges composing one pipeline, all running Gemma 4 (free via Google AI Studio or locally via Ollama): (1) extract aesthetic patterns from vibe coding sessions into structured taste directives — register, palette, motion, voice — not configuration, (2) build the self-amending loop nobody has built — model watches your aesthetic choices, reflects using thinking mode, writes taste directives into your rules file, (3) evaluate whether taste directives actually change output using LLM-as-judge with visible reasoning. Cloud fast lane means no hardware requirements; local path needs 16GB+ RAM. Bring your existing rules files — an audit script shows exactly how much taste is missing.

## Existing Repos in github.com/vibecodingnights
- **reverse-engineering** — Your LLM can decompile a function. It cannot understand a binary.
- **metaprompting** — Configuration is solved. Taste isn't. Build the metaprompting loop nobody has built — Gemma 4 watches your aesthetic choices and writes the taste directives that shape the next session.
- **auto-vcn** — 
- **bob** — Finds hackathons. Enters them. Wins.
- **agent-teams** — Think in teams, not prompts.
- **agent-orchestration** — The coordination problems are fifty years old. The frameworks are new.
- **agent-harnesses** — The pattern isn't about code — it's about closing loops
- **information-primitives** — Exercises, primitives, and provocations for exploring how we structure and interact with information
- **design-interaction** — Design & Interaction
- **offensive-security** — AI Security Workshop: Prompt injection, memory poisoning, and MCP tool attacks

## Instructions
- **Name the repo** to match the org convention above (simple kebab-case topic
  names like `agent-harnesses`, `offensive-security`, `design-interaction`).
- Create the directory structure from the flow plan.
- Write the README in the event voice (short, direct, provocative).
- Challenge files should have clear instructions. Starter templates should be minimal and runnable.
- When ready, create the repo on GitHub: `gh repo create vibecodingnights/{name} --public`
- Stage everything and commit: `git add -A && git commit -m "scaffold: metaprompting"`
- Push: `git push -u origin main`
