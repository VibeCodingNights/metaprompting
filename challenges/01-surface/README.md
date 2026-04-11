# Challenge 1 · Surface the Taste

> Configuration is in your rules file. Taste is in the *decisions* you make and never write down. Surface it.

## What you're doing

Feed Gemma 4 a vibe coding session log. Watch it read your decisions and your reasoning, then return a structured taste profile — `dimension`, `keep`, `avoid`, `reference`. Patterns that were always there but never made it into the rules file.

## What's in here

```
01-surface/
├── README.md          ← you are here
├── surface.py         ← extract a taste profile from a session
├── audit.py           ← audit an existing rules file for missing taste
└── sessions/
    ├── 01-meditation-app.md   web · finding the register
    ├── 02-cli-restic.md       cli  · taste in non-visual context
    └── 03-trading-dash.md     data · density vs clarity tension
```

## Prerequisites

`./setup/verify.sh` is passing. If it isn't, fix that first — none of this works without a live Gemma 4.

## Beginner path — 30 minutes

1. **Read one seeded session.** Open `sessions/01-meditation-app.md`. Read the four turns. Notice that the `Notes:` field is doing the real work — it's where the *why* lives.

2. **Run `surface.py` against it.**
   ```bash
   python challenges/01-surface/surface.py sessions/01-meditation-app.md
   ```
   You should see Gemma 4's thinking trace, then a structured `TasteProfile` with 3–5 directives.

3. **Read the output. Specifically: read the `reference` field first.**
   - If it says something like "a page that breathes — invitation, not persuasion" → the model captured taste.
   - If it says "use muted colors and minimal design" → **taste collapse**. The session notes were too vague, or the model wasn't given enough thinking budget. Re-run with `--think high`.

4. **Run on the CLI session.** This is the harder one. Taste in CLI tools is real (verbosity, voice, error tone) but easier for the model to fake. If the directive for `02-cli-restic.md` is just "be concise," that's collapse — the session has more signal than that.

5. **Run on the data dashboard session.** Density vs. clarity. The interesting tension here is *which* signal the model picks up.

## Going deeper

- **Run all three sessions.** Do the profiles diverge or collapse to the same generic advice? If they collapse, the bottleneck is your sessions, not the model.
- **Write your own session.** Open a real Cursor or Claude Code conversation, copy 4–6 turns into the format described in `SESSION_FORMAT.md`, and run `surface.py` on it.
- **Build a taste-diff tool.** Two profiles, output the dimensions where they disagree.

## The bring-your-own hook

If you brought a `.cursorrules`, `CLAUDE.md`, or `AGENTS.md`:

```bash
python challenges/01-surface/audit.py bring-your-own/your-rules-file.md
```

The audit reports:
- **Config rule count** — how many "use pnpm"-style rules you have today
- **Taste directive count** — almost certainly zero
- **Implied taste** — directives the model could *infer* from how you phrase your config rules (e.g., a file full of "no comments unless necessary" implies a specific voice)
- **Summary** — one paragraph describing the gap

That gap is your onramp into Challenge 2 or Challenge 3.

## What "done" looks like

- A taste profile with 3–5 structured directives extracted from at least two sessions.
- At least one directive from the CLI session — **proof that taste isn't just color palettes.**
- The `thinking` trace visible, showing Gemma 4 reasoning about aesthetics rather than syntax.
- (Bonus) An audit of someone's real rules file with the gap surfaced.

## When it goes wrong

- **"Every directive collapses to 'make it clean and modern'"** — Your session notes are too vague. Read `SESSION_FORMAT.md` again. Vague notes → vague directives, every time.
- **"The model returns invalid JSON"** — Try a lower temperature. The default is 0.4 here; drop to 0.2 if it keeps misbehaving.
- **"It's slow on local Ollama"** — Switch to cloud (`./setup/cloud.sh`). Local with `think='high'` can be 30+ seconds per call.
