# Session Format

A **session log** records the turns of a vibe coding session. Each turn has four fields. The fourth field — `notes` — is where taste lives.

## The schema

```markdown
---
title: <one-line title of the session>
context: <what you were building, in one sentence>
surface: <web | cli | data | prose | other>
---

## Turn 1

**Prompt:**
> <what you asked the model for, verbatim>

**Output:**
```<language>
<the code, copy, or description the model returned — trimmed if long>
```

**Decision:** <kept | revised | discarded>

**Notes:**
<why. this is the taste signal. what made you keep it, soften it, or throw it out.>

---

## Turn 2
...
```

## The rules

- **4–6 turns per session.** Fewer and there's no signal. More and the pattern dissolves.
- **Decisions are one of three words.** `kept`, `revised`, or `discarded`. No half-states.
- **Notes explain taste, not correctness.** "The function signature was wrong" is useless. "Too aggressive, soften it" is gold. "Wrong universe entirely" is a directive in disguise.
- **Be specific about the reference.** Not "make it cleaner." Say "like a page that breathes," "the way Craft handles margins," "more whisper less shout."
- **Revised turns can chain.** Turn 3 revises Turn 2's output → record the *new* prompt and the *new* output, and in notes say what you softened.

## A worked example

```markdown
---
title: Meditation app landing — finding the register
context: building a single-page site for a 10-minute daily breathing practice
surface: web
---

## Turn 1

**Prompt:**
> Design a hero section for a meditation app called Still. Dark theme.

**Output:**
```html
<section class="bg-black text-white py-24">
  <h1 class="text-6xl font-bold">STILL.</h1>
  <p class="text-xl">Transform your mind. Unlock your potential. Start today.</p>
  <button class="bg-purple-600 hover:bg-purple-700 px-8 py-4 rounded-lg font-bold">
    GET STARTED NOW
  </button>
</section>
```

**Decision:** discarded

**Notes:**
Everything is shouting. `STILL.` in 6xl bold with a period is a brand yelling its own name. "Transform your mind" is the copy on every hustle-productivity SaaS since 2019. Purple CTA screams conversion-optimized. This is the universe of self-improvement-as-aggression. Wrong universe entirely. I want something that doesn't sell me on stillness — it *is* still.

---

## Turn 2

**Prompt:**
> Same app. Now the hero should feel like the first breath after you've been holding it. Lowercase. Generous negative space. No CTA that sounds like a CTA.

**Output:**
```html
<section class="bg-stone-950 text-stone-200 min-h-screen flex items-center">
  <div class="max-w-xl px-16">
    <h1 class="text-4xl font-light tracking-wide">still.</h1>
    <p class="mt-8 text-lg text-stone-400 leading-relaxed">
      ten minutes. once a day. that's the whole thing.
    </p>
    <a href="#begin" class="mt-12 inline-block text-stone-300 underline underline-offset-8">
      begin when ready
    </a>
  </div>
</section>
```

**Decision:** kept

**Notes:**
Yes. The lowercase `still.` reads as a sigh, not a shout. `stone-950` not `black` — warmer, less clinical. The CTA is a text link that says "begin when ready" — it *invites* rather than *demands*. "ten minutes. once a day. that's the whole thing." is the whole value prop with zero conversion-speak. This is the tone. Everything downstream should honor it.

---

## Turn 3

**Prompt:**
> Keep going with a features section. Three features. Same register.

**Output:**
```html
<section class="py-32 bg-stone-950">
  <div class="max-w-2xl mx-auto px-16 space-y-16">
    <div>
      <h2 class="text-stone-400 text-sm uppercase tracking-widest">one</h2>
      <p class="mt-4 text-stone-200 text-lg">a single ten-minute practice. no streaks, no stats.</p>
    </div>
    <div>
      <h2 class="text-stone-400 text-sm uppercase tracking-widest">two</h2>
      <p class="mt-4 text-stone-200 text-lg">your voice, if you want it. silence, if you don't.</p>
    </div>
    <div>
      <h2 class="text-stone-400 text-sm uppercase tracking-widest">three</h2>
      <p class="mt-4 text-stone-200 text-lg">no notifications, ever.</p>
    </div>
  </div>
</section>
```

**Decision:** kept

**Notes:**
The "one / two / three" framing landed — it feels like a gentle list, not a feature grid. "no streaks, no stats" is a direct rejection of the gamification universe. "no notifications, ever" is a promise, and the emphasis on *ever* is a value statement about attention. The register is holding across turns. That matters — taste is only real if it survives composition.

---
```

## Why this format matters

The `notes` field is the signal. When you feed this session to Gemma 4, it reads your *decisions* and your *reasoning*. The structured output extractor doesn't invent taste from thin air — it surfaces the patterns that are already in how you explain your choices.

If your notes say "made it cleaner," the model will write "make it clean" — taste collapsed to generic advice. If your notes say "no streaks, no stats — rejection of gamification," the model has something to work with.

**Specific notes → specific directives. Vague notes → taste collapse.**
