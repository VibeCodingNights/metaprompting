# metaprompting

**Configuration is solved. Taste isn't.**

Your `AGENTS.md` can say "always use pnpm." It can't say "make it feel like rain on a window and the hum of a neon sign."

One of those is configuration. The other is taste.

Every metaprompting tool optimizes configuration. Cursor's `/Generate Cursor Rules`, the self-amending `CLAUDE.md` loop, OpenCode's `/init` — they tune build commands, lint rules, test runners. The structural layer.

Nobody is metaprompting taste. The register. The mood. The difference between "dark theme with purple" and "obsidian backgrounds, electric violet accents, liquid-ghostly animations." That's the layer where vibe coding actually lives and no tool touches it.

Gemma 4 shipped this month. Runs on your laptop via Ollama. Apache 2.0. Native thinking mode. It knows what vibe coding is — not the term, the aesthetic. It distinguishes between commanding a model and curating one. It has opinions.

Build the loop nobody has built. A local model that watches your session, notices which aesthetic framings you keep and which you throw away, reflects on why, and writes the taste directive that makes the next session better. Not a rules snapshot that rots. A rules file that learns your visual language.

**The model that writes your prompts should be the model you own.**

---

## Start here

Two paths to Gemma 4. Both converge at `setup/verify.sh` and the same challenge code.

```bash
# ☁️  Cloud — fast lane (2 min). Free API key, no GPU.
./setup/cloud.sh

# 💻 Local — own the model (15–30 min). Needs 16GB+ RAM.
./setup/local.sh
```

If `verify.sh` passes, you're ready. Pick a challenge.

## The three challenges

They compose into one pipeline.

1. **[Surface](challenges/01-surface/)** — Feed Gemma 4 a vibe coding session. It extracts the taste you didn't know you had.
2. **[Loop](challenges/02-loop/)** — The self-amending taste loop. The model watches your aesthetic choices and writes directives into your rules file.
3. **[Vibe Check](challenges/03-vibecheck/)** — Generate with the directive and without. Did the taste actually land?

## The fourth path, for the ambitious

**[The Sentinel](challenges/02-loop/sentinel_README.md)** — Gemma 4 tails your live Claude Code session (`~/.claude/projects/<encoded-cwd>/<uuid>.jsonl`), holds its own taste agenda, and `claude -p --resume`'s course corrections on its own authority. Silence is valid; intervention is earned. *No one has built this.*

## Brought your own rules files?

Drop your `.cursorrules`, `CLAUDE.md`, or `AGENTS.md` in [`bring-your-own/`](bring-your-own/). Then run:

```bash
python challenges/01-surface/audit.py bring-your-own/your-file.md
```

The audit reports what taste is *implied* by your phrasing but never stated. Use that as your onramp into any challenge.

## The two formats

- **[SESSION_FORMAT.md](SESSION_FORMAT.md)** — How vibe coding sessions are logged. Prompt → output → decision → *why*. Also documents the live Claude Code JSONL parser — point Surface or Loop at your real history.
- **[TASTE_FORMAT.md](TASTE_FORMAT.md)** — The taste directive schema. `dimension`, `keep`, `avoid`, `reference`.

## How the prompts talk to Gemma 4

The system prompts in `surface.py` and `loop.py` are themselves in-register — invitation, not instruction. That's the craft: **the prompt's own register is the induction signal.**

> "You are a taste extractor" → corporate output → `reference` fields that read "make it clean and modern." 
> "Read it like someone who's thrown work away for feeling wrong" → `reference` fields that read "a page that breathes — invitation, not persuasion."

Three other craft moves baked into the prompts, per the induction research:
- **Divergent exemplars beat curated ones.** 2–3 reference fields spanning web/CLI/data surfaces, not 5 examples on the same dimension.
- **Name the failure mode explicitly.** `"make it clean and modern" is what failure sounds like` lets the model self-recognize collapse.
- **Validate refusal.** `two real directives beats five generic ones` — padding for schema's sake is a failure, not a win.

Read the prompts. They're short. Edit them as you need — if they don't fit your register, you own the words.

## Entry paths

| You are… | Start here |
|---|---|
| New to rules files or local LLMs | Cloud setup → Challenge 1 |
| Claude Code user with some Python | Challenge 2: fill the loop stubs |
| Builds with LLMs, knows eval | Challenge 3: build the judge |
| Brought your messy rules files | `audit.py` on your files → any challenge |
| Want to loop on your own history | `discover_current_session()` + `parse_jsonl_session()` → Challenge 1 or 2 against your real Claude Code JSONL |
| Architecturally ambitious | [The Sentinel](challenges/02-loop/sentinel_README.md) — tail your live session, intervene on taste |

## Resources

- Repo layout is flat — `challenges/`, `setup/`, `shared/`, `bring-your-own/`
- `shared/` has the Gemma client, session parser, Pydantic schemas, rules I/O. Import, don't modify
- `setup/requirements.txt` installs: `ollama`, `openai`, `dspy-ai`, `pydantic`, `rich`

---

vibecodingnights.com
