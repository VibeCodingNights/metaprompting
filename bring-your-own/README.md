# Bring Your Own Rules Files

Drop your `.cursorrules`, `CLAUDE.md`, `AGENTS.md`, `.windsurfrules`, or any other prompt-rules file you've been carrying around.

Then run the audit:

```bash
python challenges/01-surface/audit.py bring-your-own/your-file.md
```

You'll get back:

- **Config rule count** — how many "use pnpm"-style rules you have today
- **Taste directive count** — almost certainly zero
- **Implied taste** — the directives Gemma 4 can *infer* from your phrasing but you never wrote down
- **Summary** — one paragraph describing the gap

The implied taste is the interesting part. A file full of "no comments unless they explain a non-obvious why" has a *voice* — terse, opinionated, low ceremony. The model can name that voice. You almost never have.

## Where to go from there

- **Want to fill the gap?** Take an implied directive into Challenge 2 and run the loop on a real session, using your file as the starting rules. Watch the `## Taste` section appear at the end.
- **Want to test whether it works?** Take an implied directive into Challenge 3, hand-write a coding task, and run the judge. Find out whether the directive actually shapes output or just sounds good.

## Privacy

This directory is `.gitignored` (everything except this README and `.gitkeep`). Your real rules files won't get committed to the repo. Drop them in here without worrying.
