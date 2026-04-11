# AGENTS.md

## Build
- Use `pnpm`, never `npm` or `yarn`
- Strict TypeScript — no `any` unless commented with a `// reason:`
- All imports use the `~/` path alias for `src/`

## Style
- Two-space indent
- Single quotes for strings, double for JSX attributes
- No semicolons
- Tailwind for CSS — never raw CSS files

## Testing
- Vitest + Testing Library
- Co-locate tests next to the file: `foo.ts` → `foo.test.ts`
- Don't mock the database in integration tests; use the test container

## Commits
- Conventional commits (`feat:`, `fix:`, `chore:`)
- One concept per commit
- Run `pnpm lint && pnpm test` before pushing

## Taste

### register
The first paragraph of an essay, not the first slide of a pitch deck — confident enough not to sell.

**Keep:** prose as the primary medium; one paragraph landings; first-person sentences that state facts not value props ("I write programs and sometimes essays about them"); inline links instead of buttons; quiet labels in stone-500 small caps

**Avoid:** marketing landing copy ("passionate about", "beautiful experiences"); centered round headshots with white borders; gradient backgrounds and pill CTAs; section headers that shout ("What I'm Up To Lately!"); emoji greetings (👋)

### typography
A serif voice that signals "this is meant to be read, not scanned" — and trusts the reader to stay with text.

**Keep:** serif body for prose surfaces; small text-sm grey labels for metadata (dates, "now"); inline `<a class="underline">` links rendered as part of the sentence

**Avoid:** large display sans headings; rounded card containers with shadows; tech-stack badges; hero images at the top of text-driven pages

### voice
Personal, specific, slightly self-aware — sentences that only this writer could have written.

**Keep:** project descriptions with one piece of opinion or reflection ("the DSL outlived the project"); specific personal facts (book being reread, city for the next month); humor at the writer's own expense

**Avoid:** descriptions that could fit any project; sales-line phrasing; phrases like "passionate about" or "beautiful experiences"; checkmark-bullet feature lists

### density
Generous margins, single-column max-w-2xl, big vertical rhythm — the page admits it's an essay surface and stops trying to fit more on screen.

**Keep:** max-w-2xl single column; py-20+ section padding; space-y-12 between project entries; border-t section dividers in stone-200 instead of headings

**Avoid:** multi-column grids of project cards; hero images that occupy fold space; dense feature lists with icons; UI elements competing with the prose for attention
