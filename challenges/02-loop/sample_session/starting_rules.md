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
