---
id: 03-data-table
surface: data
---

## Coding prompt
Build a React component for a server logs table. Each row has: timestamp, log level (info/warn/error), service name, and message. The user is an SRE scanning hundreds of rows looking for anomalies during an incident.

## Taste profile

### density
Bloomberg, not Robinhood. Every pixel earns its keep. The user wants more rows on screen, not more decoration around fewer rows.

**Keep:**
- monospace font so columns align without surprises
- tight vertical padding (`py-0.5` or `py-1`, not `py-3`)
- columns aligned (timestamps right, message left, level center)
- color is functional only — used to encode log level, not for branding
- a dark warm background (`zinc-950`, `stone-950`) — not pure black, easier on a 6-hour incident

**Avoid:**
- card-shaped row containers with shadows or rounded corners
- alternating row backgrounds in pastel colors
- generous py-4+ padding that limits the row count
- decorative dividers between every column
- variable-width fonts for the message column

### motion
A scanner doesn't want motion. Information appears, information stays. Animations belong to onboarding screens, not incident tools.

**Keep:**
- new rows appear instantly, no fade-in
- if a row needs to draw attention (e.g., a new ERROR), flash a `bg-red-900/40` background for ~600ms then fade
- hover state is a slight background shift, no scale or shadow

**Avoid:**
- bounce, slide, or scale animations on row entry
- toast notifications that pop in from the corner with `animate-bounce`
- spinners that obscure data — use a subtle text-based loading indicator

### voice
The labels are the floor, not the ceiling — they recede so the data can speak.

**Keep:**
- column headers are uppercase, tracking-wide, in a low-contrast color (text-zinc-500)
- log levels rendered as 4-letter codes: `INFO`, `WARN`, `ERR `
- timestamps in `HH:MM:SS.mmm` format, monospace, right-aligned

**Avoid:**
- column headers in title-case bold
- log levels as full words ("Information", "Warning", "Error")
- localized timestamp formats with timezone names

## Judging rubric
The judge should reward outputs where:
1. The table uses a monospace font and tight `py-0.5` / `py-1` row padding.
2. The background is a warm dark color, not pure black or a card-style white.
3. Column headers recede (small, uppercase, low-contrast) and rows are dense.
4. Color is functional (encoding log level) and not decorative.
5. The implementation has no entry animations, decorative dividers, or rounded card containers.

The judge should penalize outputs where:
1. Each row is a card with shadow and rounded corners.
2. Headers are bold title-case ("Timestamp", "Service", "Message").
3. There are gradient backgrounds, alternating pastel rows, or `animate-*` classes.
4. The font is sans-serif throughout, including the data columns.
5. Log levels are full words rendered with emoji or pill backgrounds.

Cite specific Tailwind classes or attribute values from the output. "It looks dense" is too vague; "uses `py-0.5 font-mono text-xs` on the row and `text-zinc-500 uppercase tracking-wider text-[10px]` on the headers" is the kind of citation we want.
