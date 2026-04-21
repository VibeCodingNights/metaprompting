# deck

5-minute intro for the metaprompting Vibe Coding Night. Seven slides.

## run it

```bash
cd deck
pnpm install
pnpm dev      # opens http://localhost:3030
```

Press `f` for fullscreen. Arrow keys to navigate. `o` for overview.

## export

```bash
pnpm build    # → dist/
pnpm export   # → PDF
```

## what's in here

- `slides.md` — the deck
- `style.css` — stone palette + serif body + lowercase labels
- `package.json` — slidev deps

The deck is itself a taste artifact. Turn 2 register throughout — stone-950, serif
body, lowercase titles, generous whitespace — except slide 3a, which deliberately
renders in the Turn 1 shout universe (purple gradient, bold sans, SaaS copy) to
demonstrate the register flip before the argument is made in words.

Don't "clean up" slide 3a. It's doing real work.
