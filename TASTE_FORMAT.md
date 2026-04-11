# Taste Format

A **taste directive** is what comes out of Challenge 1 and gets written into your rules file in Challenge 2. It has four fields, enforced by a Pydantic schema (`shared/taste_schema.py`).

## The schema

```python
class TasteDirective(BaseModel):
    dimension: str   # register, palette, motion, typography, voice, density, rhythm, ...
    keep: list[str]  # 2–5 patterns to maintain
    avoid: list[str] # 2–5 patterns to reject
    reference: str   # ONE evocative sentence. not advice. a feeling.
```

## The four fields

### `dimension` — the axis you're legislating
One word or a short phrase. Not a scope, an axis. Examples:

- `register` — the emotional volume. Whisper vs. shout.
- `palette` — the color universe.
- `motion` — how things enter, leave, hover.
- `typography` — weight, tracking, hierarchy.
- `voice` — how copy sounds. Microcopy, error text, empty states.
- `density` — how much air between elements.
- `rhythm` — how content paces itself down the page.

Naming the dimension forces the model to pick a lane instead of writing one blobby directive that smears across everything.

### `keep` — patterns to maintain
2–5 items. Short imperatives or observed patterns. Things that were in the outputs you kept.

Good:
- `"lowercase CTAs that invite rather than demand"`
- `"warm neutrals (stone-*) over cool neutrals (slate-*)"`
- `"negative space as emphasis — margins do the work headers can't"`

Bad (too vague):
- `"good spacing"`
- `"clean look"`
- `"minimal"`

### `avoid` — patterns to reject
2–5 items. Things that were in the outputs you discarded. The shape of the wrong answer.

Good:
- `"all-caps CTAs, conversion-optimized button copy"`
- `"gradient purples, the self-improvement SaaS palette"`
- `"feature grids with checkmark icons"`

Bad (not grounded in any rejection):
- `"bad design"`
- `"generic UI"`
- `"ugly colors"`

### `reference` — ONE evocative sentence
**This is the test.** If this field collapses to generic advice, the extractor failed.

Good:
- `"a page that breathes — ten minutes of your day and it knows that's what it's asking for"`
- `"rain on a window: calm, structural, the noise is the point"`
- `"error messages that apologize like a friend, not a compliance document"`
- `"the hum of a neon sign — quiet but always there"`

Bad:
- `"make it clean and modern"`
- `"use muted colors"`
- `"minimal and professional"`

The `reference` field is the one field in the schema that explicitly *isn't* advice. It's a feeling. If Gemma 4 can write it, Gemma 4 understood the session. If it can't, the session notes weren't specific enough and you need to sharpen them.

## A worked example

From the meditation app session in `SESSION_FORMAT.md`:

```json
{
  "dimension": "register",
  "keep": [
    "lowercase headers that read as sighs not shouts",
    "CTAs as text links with language like 'begin when ready'",
    "copy that states the value prop without selling it",
    "explicit refusals: 'no streaks, no stats', 'no notifications, ever'"
  ],
  "avoid": [
    "all-caps brand names, periods that bark",
    "hustle-productivity copy: 'transform', 'unlock', 'now'",
    "purple conversion CTAs with 'GET STARTED' energy",
    "gamification language (streaks, stats, achievements)"
  ],
  "reference": "the first breath after you've been holding it — invitation, not persuasion"
}
```

Notice how every `keep` and `avoid` item traces back to a specific decision in the session. Nothing is invented. The `reference` field is a compression of the three turns into one phrase — it's what the session *was about* once you strip away the individual choices.

## How directives land in rules files

Challenge 2 appends these to your existing `CLAUDE.md` / `AGENTS.md` / `.cursorrules` under a `## Taste` section. The rest of the file — config, lint rules, build commands — stays untouched.

```markdown
# my rules file

## Build
- pnpm, not npm
- strict mode on
- pytest for python

## Taste

### register
A page that breathes — invitation, not persuasion.

**Keep:** lowercase headers that read as sighs, CTAs as text links ("begin when ready"), copy that states value without selling, explicit refusals ("no streaks, no stats").

**Avoid:** all-caps brand names, hustle-productivity copy ("transform", "unlock", "now"), purple conversion CTAs, gamification language.
```

## The taste collapse test

When you run Challenge 1, read the `reference` field first. If it's generic, everything else is generic too and the session needs sharper notes. This is the single fastest way to tell whether the extraction worked.
