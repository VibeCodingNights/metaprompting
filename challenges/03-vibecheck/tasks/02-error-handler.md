---
id: 02-error-handler
surface: cli
---

## Coding prompt
Write the user-facing error messages and help text for a small CLI tool called `pq` that runs ad-hoc SQL queries against a Postgres database. Cover three scenarios: (1) the connection string is missing or unparseable, (2) the query has a syntax error returned by Postgres, (3) the query timed out after the configured limit. Also write the `pq --help` output.

## Taste profile

### voice
A senior SRE who has been on call at 3am and respects that you might be too — short, factual, no apology, no decoration.

**Keep:**
- imperative-mood verbs in option descriptions ("attach", "exclude", "override")
- error messages that name the failure, then state where it looked, then state what to do
- next-action hints with concrete commands the user can copy
- "no X.toml found" — lowercase, no "Error:" prefix, no exclamation marks

**Avoid:**
- emoji in any output (no ❌ ✓ 🔔 📁)
- apologetic phrasing ("Oops!", "Sorry, we couldn't…", "Please make sure…")
- editorializing adjectives ("beautiful", "important", "successfully")
- referrals to documentation pages or "contact support" filler
- exclamation marks anywhere

### density
Information per line. Anticipate the next question and answer it without being asked, but never with filler.

**Keep:**
- option flags aligned in a single column with one-line descriptions
- diagnostic output that includes the search path or the SQL fragment that failed
- a "hint:" line with one concrete next command, not two paragraphs of context

**Avoid:**
- ASCII art banners
- multi-paragraph error explanations
- "see the documentation at https://..." trailers
- redundant labels like "Error:" before an obvious error

## Judging rubric
The judge should reward outputs where:
1. Error messages name the failure, the location, and a next action — in that order, in three lines or fewer.
2. The help output uses lowercase command summary lines and aligned options.
3. Voice is calm and assumes competence — no apology, no celebration, no exclamation marks.
4. Specific diagnostic info is included where it's useful (the SQL fragment for syntax errors, the timeout value for the timeout case).

The judge should penalize outputs where:
1. Any emoji appears.
2. Errors apologize or use exclamation marks.
3. Help text editorializes ("beautiful", "powerful", "amazing").
4. Multi-paragraph errors with "see the docs" trailers.

Cite specific lines from the output. "It avoids emoji" is too vague; "the timeout error reads `query timed out after 30s` with no decoration" is the kind of citation we want.
