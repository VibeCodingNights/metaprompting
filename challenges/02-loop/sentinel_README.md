# The Taste Sentinel

> A second process with its own agenda. It watches Claude Code the way you'd watch a drummer who's about to rush the tempo — most of the time, not at all. Once in a while: a look.

## Why this exists

The loop in `loop.py` is reflective. It reads a session *after the fact*, generalizes what it sees, and writes taste directives into your rules file. That's valuable, but it's post-hoc — the session already happened, and Claude already drifted wherever it drifted.

The sentinel is the real-time counterpart. An external daemon tails the live JSONL that Claude Code writes to `~/.claude/projects/...`, loads the `## Taste` directives you've curated in your CLAUDE.md hierarchy, and — on each new assistant turn — asks Gemma 4 a single question: *is Claude actively violating the register right now?*

The schema's `intervene: bool` is Gemma's self-veto. **Silence is valid.** Performative interventions — the sentinel piping up on every turn to prove it's listening — are the failure mode. We want a model that has taste about *when* to speak, not just what to say. A sentinel that fires once an hour is working. A sentinel that fires every turn is broken.

## How to run

One command, in a second terminal while Claude Code is running in the first:

```bash
python challenges/02-loop/sentinel.py --cwd . --dry-run
```

Drop `--dry-run` once you've watched the verdicts and you trust it. Optional flags:

```
--window-turns 5       # turns of session context fed to Gemma
--cooldown 90          # seconds between interventions
--threshold 0.7        # confidence floor for firing
--poll-interval 2      # seconds between stat checks on the JSONL
```

## How cooldown works

Three gates stack. An intervention fires only when **all three** pass:

1. **Gemma's verdict.** `intervene: true` — the model thinks the output is actively violating a directive.
2. **Confidence floor.** `confidence >= threshold` (default 0.7).
3. **Cooldown + dimension dedup.** Within the last `cooldown` seconds, we already fired on this dimension → skip. Within the last `cooldown` seconds, fired on a different dimension → skip anyway (one nudge at a time). After the cooldown expires, the gate reopens.

State lives at `~/.claude/sentinel_log.json` so cooldowns survive restarts.

## What an intervention looks like

The sentinel shells out:

```
claude -p "the CTA just went from 'begin when ready' to 'GET STARTED NOW.' Back off." \
       --resume <session-id> --output-format json
```

In Claude Code, that shows up as a new user turn — as if you had typed the note yourself. Claude's next response should read like a correction. The next tick of the sentinel sees both the injection and Claude's reply, which lets it judge whether the correction landed.

## The gotcha

This requires Claude Code to be **running interactively** — the sentinel tails what Claude writes in real time. You can't point it at an old session and have it retroactively fix the transcript. If Claude isn't running, the JSONL doesn't grow, and the sentinel just stares at a file that isn't changing.

## Known limits

- **It's louder than you might want by default.** `-p --resume` adds a visible user turn — there's no silent correction mechanism in Claude Code. Tune the threshold up (try 0.85) if you want fewer, higher-confidence fires.
- **It requires real taste directives.** With no `## Taste` section anywhere in your CLAUDE.md hierarchy, the sentinel has no ground truth and will stay silent (by design — see the placeholder in `load_active_taste`).
- **Polling, not inotify.** We stat the JSONL every couple of seconds. This is fine — Claude Code flushes per event — but it's not instantaneous.
- **Gemma can be wrong.** The verdict schema lets Gemma veto itself (`intervene: false`), but it can also false-positive. The cooldown softens that; the `reasoning` field in the log is where you audit which fires were earned.

## Design notes for the curious

- The sentinel only reacts to `assistant` events, not `user` events. We're judging what Claude *produced*, not what you *asked for* — your prompts are signal for Claude, not grading rubric for Gemma.
- The CLAUDE.md walker resolves `@path` imports and concatenates outer-to-inner, so a project-level `## Taste` section overrides the global one visually in the prompt.
- The system prompt is written in-register on purpose. A flat "judge whether X violates Y" prompt produces flat verdicts. The sentinel's own voice has to match what it's guarding.
