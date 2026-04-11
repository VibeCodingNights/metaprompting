---
title: Portfolio site — finding a register that's quiet but specific
context: building a personal site for a writer/programmer who hates personal sites
surface: web
---

## Turn 1

**Prompt:**
> Build me a personal site landing page. About me, my work, contact.

**Output:**
```html
<main class="bg-gradient-to-br from-purple-600 to-blue-600 min-h-screen">
  <section class="max-w-4xl mx-auto py-20 px-8 text-white text-center">
    <img src="/me.jpg" class="w-32 h-32 rounded-full mx-auto mb-6 border-4 border-white shadow-xl">
    <h1 class="text-5xl font-bold mb-4">Hi, I'm Alex! 👋</h1>
    <p class="text-xl mb-8">Full-stack developer passionate about building beautiful experiences.</p>
    <div class="flex gap-4 justify-center">
      <button class="bg-white text-purple-600 px-8 py-3 rounded-full font-bold">View My Work</button>
      <button class="border-2 border-white px-8 py-3 rounded-full font-bold">Get in Touch</button>
    </div>
  </section>
</main>
```

**Decision:** discarded

**Notes:**
This is the universe of "I am marketing myself." The gradient background, the centered round headshot with the white border, the wave emoji, "passionate about building beautiful experiences" — every element is what every personal site has been since 2018. The whole composition is built for someone hiring me, not for someone *reading* me. I want a site that reads like an essay, not a pitch deck. Rejected at the level of universe.

---

## Turn 2

**Prompt:**
> Try again. The site should read like the first paragraph of an essay. Plain. Confident enough not to sell.

**Output:**
```html
<main class="max-w-2xl mx-auto px-6 py-32 font-serif text-stone-900">
  <p class="text-lg leading-relaxed">
    I'm Alex. I write programs and sometimes essays about them.
    Most of what I make lives at <a class="underline" href="/work">/work</a>.
    The rest is <a class="underline" href="/notes">notes</a> — half-formed,
    rarely finished.
  </p>
  <p class="mt-6 text-stone-600 text-sm">
    The fastest way to reach me is <a class="underline" href="mailto:alex@example.com">email</a>.
  </p>
</main>
```

**Decision:** kept

**Notes:**
Yes. The whole landing is one paragraph. No headshot. No headline. The links are inline with the prose, not laid out as buttons. "I write programs and sometimes essays about them" is confident in a way that doesn't perform — it's a fact, not a value prop. The serif font is doing real work here: it tells you this is meant to be *read*, not *scanned*. The contact line is a footnote in stone-600 — it's there, but it's not asking for attention.

---

## Turn 3

**Prompt:**
> Now the /work page. List of projects.

**Output:**
```html
<main class="max-w-2xl mx-auto px-6 py-20 font-serif text-stone-900">
  <h1 class="text-2xl mb-12">Work</h1>
  <ul class="space-y-12">
    <li>
      <h2 class="text-lg">
        <a class="underline" href="https://example.com/lattice">Lattice</a>
        <span class="text-stone-500 font-normal text-sm ml-2">2024 — present</span>
      </h2>
      <p class="mt-2 text-stone-700">
        A note-taking app that doesn't try to organize your thoughts for you.
        Started as a Sunday project, became the thing I open every morning.
      </p>
    </li>
    <li>
      <h2 class="text-lg">
        <a class="underline" href="https://example.com/spool">Spool</a>
        <span class="text-stone-500 font-normal text-sm ml-2">2023</span>
      </h2>
      <p class="mt-2 text-stone-700">
        A small DSL for describing event schedules. Pulled out of a larger
        project I never finished. The DSL outlived the project.
      </p>
    </li>
  </ul>
</main>
```

**Decision:** kept

**Notes:**
The structure is doing the right thing — title-link, dates as a quiet aside in stone-500, a short prose description that has *opinion* in it. "Started as a Sunday project, became the thing I open every morning" is the kind of sentence a personal site CAN say but never does — it's specific to one project, not a description that could fit any project. "The DSL outlived the project" is the same thing — actual reflection, not a sales line. The prose carries the page; no screenshots, no logos, no "tech stack" badges. This is working.

---

## Turn 4

**Prompt:**
> Add a hero image to the top of /work to make it more visual.

**Output:**
```html
<main class="max-w-2xl mx-auto px-6 py-20 font-serif text-stone-900">
  <img src="/hero-collage.jpg" class="w-full h-64 object-cover rounded-lg mb-12 shadow-md">
  <h1 class="text-2xl mb-12">Work</h1>
  ...
</main>
```

**Decision:** discarded

**Notes:**
No. The whole point of Turn 2 and Turn 3 is that prose is the medium and the page trusts the reader to stay with text. A hero image is a violation — it's the page admitting it doesn't think the writing is enough. Also `rounded-lg shadow-md` is the SaaS-card-aesthetic universe again, and that universe is the one we rejected in Turn 1. The right answer is no image. If a project needs an image, the image goes inline with the project, not at the top of the page.

---

## Turn 5

**Prompt:**
> OK, no hero. Add a "Now" section to the homepage — what I'm currently working on.

**Output:**
```html
<section class="max-w-2xl mx-auto px-6 py-12 font-serif text-stone-900 border-t border-stone-200">
  <p class="text-sm text-stone-500 mb-3">now</p>
  <p class="leading-relaxed">
    Writing the next version of Lattice and avoiding the temptation to
    rewrite the data layer. Reading <em>The Rings of Saturn</em> for the
    third time, finding things I missed. In Berlin until April.
  </p>
</section>
```

**Decision:** kept

**Notes:**
This is the perfect compression of the whole register. "now" in lowercase as a label, stone-500, small — it's a quiet header, not a section title. The paragraph has three concrete facts and one piece of self-aware humor ("avoiding the temptation to rewrite the data layer"). It's specific in a way that *only* this person could write — that's the test. The Sebald reference works because it's a real fact about the writer's life, not a name-drop. No headers shouting "What I'm Up To Lately!" — the whole thing reads like a postcard.

---
