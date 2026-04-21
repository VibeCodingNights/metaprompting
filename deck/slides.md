---
theme: seriph
title: "metaprompting — configuration is solved. taste isn't."
info: |
  Vibe Coding Nights intro · 5 minutes · hard stop.
  Every rung of metaprompting today tunes configuration. Tonight
  we build the loop nobody has built — one that tunes taste.
colorSchema: dark
background: "#1c1917"
class: text-stone-200
fonts:
  serif: Iowan Old Style, Palatino, Source Serif Pro, Georgia, serif
  mono: JetBrains Mono, SF Mono, Menlo, monospace
drawings:
  persist: false
transition: fade
mdc: true
---

<div class="label">vibe coding nights · metaprompting</div>

# configuration is solved.

# taste isn't.

<div class="epigraph">

your AGENTS.md can say "always use pnpm."<br>
it can't say "make it feel like rain on a window<br>and the hum of a neon sign."

</div>

<!--
Open slow. Two beats of silence after reading the two lines.
The audience is already in the room — the deck's job is to lower the temperature,
not raise it.
-->

---
layout: default
---

<div class="label">slide 1 · same stack, different universe</div>

<div class="diptych">

<div class="col">

### AGENTS.md

```markdown
## Build
- pnpm, not npm
- Strict TypeScript
- ~/ path alias

## Style
- two-space indent
- no semicolons
- Tailwind only

## Testing
- Vitest + RTL
- co-locate tests
```

</div>

<div class="col">

### AGENTS.md

```markdown
## Build
- pnpm, not npm
- Strict TypeScript
- ~/ path alias

## Style
## Testing
(...same...)

## Taste

### register
A page that breathes —
invitation, not persuasion.
```

</div>

</div>

<div class="epigraph">same project. same stack. different universe.</div>

<!--
45 sec. The audience reads. Don't fill the silence.
The question: which rules file is yours?
Every one is the left.
-->

---
layout: default
---

<div class="label">slide 2 · the ladder everyone is climbing</div>

# every rung tunes correctness.

<ul class="ladder">
  <li><code>.cursorrules</code> <span class="desc">— static rules file (2023)</span></li>
  <li><code>/Generate Cursor Rules</code> <span class="desc">— inferred from examples</span></li>
  <li><code>CLAUDE.md + @AGENTS.md</code> <span class="desc">— Linux Foundation standard, 60K repos (Dec 2025)</span></li>
  <li><code>claude-meta</code> <span class="desc">— self-amends from failure</span></li>
  <li><code>claude-reflect</code> <span class="desc">— learns from corrections and positive feedback</span></li>
</ul>

<div class="epigraph">
pnpm. pytest. strict mode. conventional commits.<br>
nobody is tuning the voice of an error message.
</div>

<!--
45 sec. The ladder is real. Name claude-reflect — it exists, it almost does this.
But even claude-reflect learns from CORRECTNESS signals, not aesthetic ones.
-->

---
layout: center
class: shout-scope
---

<h1>transform<br>your<br>rules file!</h1>

<p>unlock your potential with AI-powered metaprompting. join thousands of developers who have already revolutionized their workflow.</p>

<div class="cta">🚀 get started now</div>

<!--
10 sec. Say nothing. Let the slide be the argument.
Then click forward on the beat.
-->

---
layout: default
class: text-stone-200
---

<div style="margin-left: 5rem; margin-top: 4rem;">

<h1 style="font-size: 4.5rem; margin: 0; line-height: 1; text-transform: lowercase; letter-spacing: -0.02em; color: #f5f5f4; font-family: 'Iowan Old Style', 'Palatino', serif; font-weight: 400;">still.</h1>

<p style="color: #a8a29e; margin-top: 2.4rem; font-size: 1.15rem; line-height: 1.8; max-width: 28rem;">
ten minutes. once a day. that's the whole thing.
</p>

<p style="color: #78716c; margin-top: 3rem; font-size: 0.9rem; font-style: italic;">
begin when ready
</p>

</div>

<div class="epigraph" style="margin: 4rem 5rem 0; max-width: 32rem;">
what changed isn't in any rules file. not pnpm.<br>
not strict mode. not commit conventions. register.
</div>

<!--
60 sec. The longest dwell in the deck.
The audience just felt the flip. Name what they felt:
"Turn 1 of every session is the same SaaS landing-page universe.
Turn 2 is someone who's thrown that universe away."
The thing that got thrown away isn't in any rules file on earth.
-->

---
layout: default
class: quote-slide
---

<div class="label">slide 4 · gemma 4, unprompted</div>

<blockquote>
<p>"obsidian syntax: precise, cold, and cutting."</p>
<p>"vapor syntax: flowing, ethereal, and liminal."</p>
<p>"kill the corporate ghost."</p>
<p>"cook the vibe until the pixels bleed."</p>
</blockquote>

<div class="epigraph" style="margin-top: 3rem;">
nothing in the prompt primed this. gemma 4 volunteered<br>
the vocabulary. it already speaks the dialect.
</div>

<!--
60 sec. The most important slide.
This is the proof point. Gemma 4 didn't follow instructions — it VOLUNTEERED
"obsidian" and "vapor" and "corporate ghost" without being asked.
It distinguishes "correct output" from "transcendent output" on its own.
Gemma 3 could style-match on request. Gemma 4 initiates register.
-->

---
layout: default
class: craft-slide
---

<div class="label">slide 5 · the craft move</div>

<div class="diptych">

<div class="col">

### what the repo ships with

```python
"""
You are a taste extractor
for vibe coding sessions.

Extract 3–5 taste directives.
Each must include: dimension,
keep, avoid, reference.

Return valid JSON.
"""
```

</div>

<div class="col">

### what to write instead

```python
"""
You've been handed a vibe coding
session. Read it like someone
who's thrown work away for feeling
wrong.

The decisions aren't about
correctness — they're about register.

  "a page that breathes —
   invitation, not persuasion"
  "command-line as whispered apology"

"make it clean and modern" is
what failure sounds like.
"""
```

</div>

</div>

<div class="epigraph">
the prompt's own register is the induction signal.<br>
write it in the voice you want back.
</div>

<!--
50 sec. The one practical takeaway.
You can't ask a model to be creative in a bureaucratic voice.
Gemma 4 mirrors what you hand it. So hand it the register you want.
Also: diverse exemplars across web/CLI/data — same-dimension examples over-constrain.
-->

---
layout: default
---

<div class="label">slide 6 · taste has shape</div>

# it resolves to where you work.

<div class="hierarchy">
<div><span class="path">~/.claude/CLAUDE.md</span></div>
<div class="note">global register — how all your sessions should feel</div>
<div><span class="path">./CLAUDE.md</span></div>
<div class="note">this project's register</div>
<div><span class="path">./web/CLAUDE.md</span></div>
<div class="note">landing pages — stone palette, serif body</div>
<div><span class="path">./cli/CLAUDE.md</span></div>
<div class="note">sysadmin voice — no emoji, no apologetic "we"</div>
<div><span class="path">.claude/agents/designer.md</span></div>
<div class="note">subagent-scoped taste</div>
<div><span class="path">.claude/skills/taste/SKILL.md</span></div>
<div class="note">auto-activates on matching file globs</div>
</div>

<div class="epigraph">
a meditation app and a trading floor don't share a register.<br>
the loop learns where to write.
</div>

<!--
40 sec. The map. Claude Code's own hierarchy picks up nested CLAUDE.md on-demand
when it reads files in that subtree — this is already live, not a hypothetical.
-->

---
layout: default
---

<div class="label">slide 7 · pick a path, go</div>

<div style="margin: 2rem 0 3rem;">

**surface** &mdash; <span class="cite">feed gemma a session. watch it surface the taste you didn't know you had.</span>

**loop** &mdash; <span class="cite">the self-amending taste loop. session → reflection → directive → amended CLAUDE.md.</span>

**vibe check** &mdash; <span class="cite">generate with and without. did the directive actually land?</span>

**the sentinel** &mdash; <span class="cite">for the ambitious. gemma tails your live claude code session, holds its own taste agenda, and <code>claude -p --resume</code>'s course corrections on its own authority. <strong>no one has built this.</strong></span>

</div>

<div style="margin-top: 2rem;">

```bash
# cloud fast lane (2 min)    # or local — own the model
./setup/cloud.sh              ./setup/local.sh
```

</div>

<div class="epigraph">
<strong>github.com/vibecodingnights/metaprompting</strong><br><br>
<em>"language is not just a carrier of information; it is a carrier of energy."</em><br>
<span class="cite">— Gemma 4</span>
</div>

<!--
30 sec. Land it. The repo URL is the handoff.
Don't explain the three paths — the audience will click into whichever matches their comfort.
The sentinel line is the pepper: "no one has built this" is the part that makes
the ambitious 10% lean in. The rest get the normal three challenges.
-->
