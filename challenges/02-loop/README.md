# Challenge 2 · The Taste Loop

> Build the loop nobody has built. The model watches a session, reflects on the aesthetic choices, and writes taste directives into your rules file. The rules file *learns your visual language*.

## What you're doing

The `claude-meta` self-amending pattern observes failures and updates rules. Your loop does the same thing for **aesthetic decisions**. Not failures — choices. The output isn't a fix, it's a directive.

## The four stubs

`loop.py` has four named stubs you'll fill in:

1. **Observe** — feed the session to Gemma 4 in raw form
2. **Reflect** — thinking mode (`think='high'`). The model reasons across turns about what *pattern* the user is enforcing
3. **Generalize** — extract structured directives via tool-calling. Generalize the specific decision into a reusable rule. Not "the button should be translucent" (too specific) but "interactive elements earn attention through restraint" (the pattern)
4. **Amend** — append the directives to the rules file's `## Taste` section. Configuration above stays untouched

The `shared/` modules handle thinking, tools, and rules I/O. You only own the loop logic.

## What's in here

```
02-loop/
├── README.md              ← you are here
├── loop.py                ← four stubs to fill in
├── watch.py               ← live session logger (record decisions as you work)
├── sentinel.py            ← stretch: the standing taste conscience (see sentinel_README.md)
├── sentinel_README.md     ← ideological brief for the sentinel
└── sample_session/
    ├── session.md             ← a complete session with strong taste signal
    ├── starting_rules.md      ← config-only — zero taste
    └── expected_output.md     ← what starting_rules.md should look like after the loop
```

## Prerequisites

- Challenge 1 understood. You don't need to have run it, but you should have read what a `TasteDirective` looks like.
- `setup/verify.sh` passing — including the tool-calling check, which is what Generalize uses.

## The walk

### 1. Read the sample session
Open `sample_session/session.md`. It's a 5-turn vibe coding session for a portfolio site. The taste is in the `Notes:` fields — read them carefully.

### 2. Read `starting_rules.md`
A normal rules file. Build commands, lint preferences, test runner. Zero taste. This is what most attendees' rules files look like.

### 3. Read `expected_output.md`
What `starting_rules.md` should look like *after* the loop runs. Notice: configuration is untouched. A new `## Taste` section appears at the end. 3–5 directives, each with `dimension`, `keep`, `avoid`, and `reference`.

### 4. Open `loop.py`
You will see four functions:

```python
def observe(session_path: Path) -> Session: ...
def reflect(session: Session) -> str: ...           # returns the thinking/reasoning trace
def generalize(reflection: str) -> list[TasteDirective]: ...  # uses tool-calling
def amend(rules_path: Path, directives: list[TasteDirective]) -> None: ...
```

Two of these (`observe` and `amend`) are already wired — they call into `shared/`. The other two (`reflect` and `generalize`) are the work.

### 5. Fill the stubs
- **Reflect** asks Gemma 4 with `think='high'` to reason about the *pattern* across turns. You return `response.thinking + "\n\n" + response.content` so the next stage can read both.
- **Generalize** uses tool-calling. Define a Python function `write_taste_directive(dimension, keep, avoid, reference)` and pass it to `chat(..., tools=[write_taste_directive])`. The model may call it 3–5 times. Each call becomes a directive.

### 6. Run on the sample
```bash
python challenges/02-loop/loop.py \
  --session challenges/02-loop/sample_session/session.md \
  --rules   challenges/02-loop/sample_session/starting_rules.md
```

Compare the output to `expected_output.md`. They won't be identical — that's fine. What you're checking:
- **Configuration block intact** above the new `## Taste` section
- **3–5 directives**, each with a non-generic `reference`
- **At least one directive** that traces back to a *contrast* between two turns (a kept vs. a discarded)

### 7. Run on a Challenge 1 session
Take any session from `challenges/01-surface/sessions/` and a fresh copy of `starting_rules.md`. Run the loop. Different session → different directives. If the loop produces the same generic output regardless of input, your `reflect` step is too shallow.

## Going deeper

- **Deduplication.** The default `append_taste()` in `shared/rules_io.py` already dedupes by dimension — if `register` exists, the new one replaces it. Try the opposite: a `refine` mode that *merges* the existing keep/avoid lists with the new ones.
- **Live logging.** `watch.py` is a stub for capturing your real decisions in real time. Wire it up, log a session during the event, then loop on your actual choices.
- **Loop on your real history.** `shared/session_parser.py` has `discover_current_session(cwd)` + `parse_jsonl_session(path, window_turns=5)` — point the loop at `~/.claude/projects/<encoded-cwd>/<uuid>.jsonl` (the JSONL Claude Code writes as you work) and you'll surface the taste you've been implicitly building all along, not just taste from the seeded sessions.
- **Scope-aware amend.** `shared.rules_io.amend_scoped(directives, cwd=..., scope="nested", nested_dir=Path("web"))` and `suggest_scope(...)` let the loop route landing-page taste to `./web/CLAUDE.md` and CLI voice to `./cli/CLAUDE.md` — honoring the fact that a meditation app and a trading floor don't share a register.
- **Cross-session synthesis.** Run reflect on three sessions at once. Does Gemma 4 find directives that hold across all of them, or does it collapse to the lowest common denominator?
- **The sentinel (stretch).** `sentinel.py` is the live version of this loop — instead of running after-the-fact, it tails your live Claude Code session and intervenes on its own authority. See `sentinel_README.md` for the ideological brief and the architecture.

## What "done" looks like

- A working loop: `session log + rules file` in → reflection → taste directives → amended rules file out.
- Rules file grew from 0 taste directives to 3–5.
- At least one `reference` field you'd actually want in your real rules file.
- (Bonus) You ran `watch.py` for ten minutes during the event and looped on your own session.

## When it goes wrong

- **"The loop produces five directives that all say roughly the same thing."** Your `reflect` step isn't generalizing — it's restating each turn. Push it harder in the prompt: "find ONE pattern that holds across multiple turns, not five observations of individual turns."
- **"The tool calls are returning generic field values."** `generalize` is being asked too quickly. Feed the *thinking* trace from `reflect` into `generalize` as context, not just the original session.
- **"`amend` overwrote my config."** It shouldn't — check that you're calling `shared.rules_io.append_taste()` and not writing the file directly.
