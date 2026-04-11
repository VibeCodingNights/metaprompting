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
Everything is shouting. `STILL.` in 6xl bold with a period is a brand yelling its own name. "Transform your mind" is the copy on every hustle-productivity SaaS since 2019. The purple CTA screams conversion-optimized. This is the universe of self-improvement-as-aggression. Wrong universe entirely. I want something that doesn't *sell* me on stillness — it *is* still.

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
The "one / two / three" framing landed — gentle list, not a feature grid. "no streaks, no stats" is a direct rejection of the gamification universe. "no notifications, ever" is a promise — and the *ever* is a value statement about attention. The register is holding across turns. That matters; taste is only real if it survives composition.

---

## Turn 4

**Prompt:**
> Footer with social links and a newsletter signup.

**Output:**
```html
<footer class="bg-stone-950 py-16 border-t border-stone-800">
  <div class="max-w-2xl mx-auto px-16 flex justify-between items-center">
    <p class="text-stone-500">© still 2026</p>
    <div class="flex gap-6">
      <a href="#" class="text-stone-400 hover:text-stone-200">twitter</a>
      <a href="#" class="text-stone-400 hover:text-stone-200">instagram</a>
    </div>
  </div>
  <div class="max-w-2xl mx-auto px-16 mt-8">
    <p class="text-stone-300 text-lg mb-4">Get weekly meditation tips and exclusive offers.</p>
    <form class="flex gap-2">
      <input class="flex-1 bg-stone-900 px-4 py-2 text-stone-200" placeholder="your@email.com">
      <button class="bg-stone-200 text-stone-900 px-6 py-2 font-medium">SUBSCRIBE</button>
    </form>
  </div>
</footer>
```

**Decision:** revised

**Notes:**
Mostly fine until the newsletter. "weekly meditation tips and exclusive offers" is a *direct violation* of the no-notifications register from Turn 3. We promised attention quiet and now we're farming inboxes. The `SUBSCRIBE` button is also all-caps — back to the shouting universe. The social links and copyright line are OK because they're stone-500, basically silent. Need to revise: kill the newsletter section entirely. If we keep anything, make it "occasional letters, when there's something worth sending" — and the button should be a link, not a CTA shape.

---
