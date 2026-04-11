---
title: Backup CLI — finding the voice
context: writing user-facing strings for a backup CLI tool aimed at sysadmins
surface: cli
---

## Turn 1

**Prompt:**
> Write a help message for the `backup snapshot` command. It creates a new snapshot of the configured directories.

**Output:**
```
USAGE:
    backup snapshot [OPTIONS] [PATHS]...

📸 Create a beautiful new snapshot of your important files! ✨

OPTIONS:
    -t, --tag <TAG>           Add a tag to your snapshot 🏷️
    -e, --exclude <PATTERN>   Exclude files matching pattern 🚫
    -h, --host <HOST>         Override the hostname 💻

EXAMPLE:
    backup snapshot ~/Documents --tag "important stuff" 📁
```

**Decision:** discarded

**Notes:**
This is a backup tool for sysadmins. The emoji are an immediate trust failure — they communicate "this software was made by someone who doesn't understand who uses it." "beautiful new snapshot of your important files" is a children's book. Also "your important files" infantilizes the user — they know what files are important to them, that's why they're running a backup tool. The help text should sound like a person who has been on call at 3am and respects that you might be too.

---

## Turn 2

**Prompt:**
> Same command. The voice should be like a senior SRE wrote it. Short. No emoji. Assume the reader is competent.

**Output:**
```
backup snapshot - create a new snapshot

Usage:
    backup snapshot [options] [paths...]

Options:
    -t, --tag <tag>           attach a tag to the snapshot
    -e, --exclude <pattern>   exclude paths matching glob
    -h, --host <host>         override the recorded hostname

If no paths are given, snapshots the directories listed in backup.toml.

Example:
    backup snapshot /etc /var/lib/postgresql --tag pre-upgrade
```

**Decision:** kept

**Notes:**
This is the voice. Lowercase command summary line — concise statement of fact. Options aligned, descriptions are imperative ("attach", "exclude", "override") and *short*. The example is realistic — someone backing up etc and a postgres data dir before an upgrade — not "important stuff." The line about backup.toml is the key inclusion: it answers a question without being asked. That's the tone — anticipates what you need to know, doesn't perform helpfulness.

---

## Turn 3

**Prompt:**
> Write the error message for: user runs `backup snapshot` but there's no backup.toml in the working directory or any parent.

**Output:**
```
❌ Error: We couldn't find your backup configuration!
Please make sure you have created a backup.toml file with your settings.
For more information, see the documentation at https://example.com/docs
Need help? Contact support@example.com
```

**Decision:** discarded

**Notes:**
Three failures at once. (1) `❌ Error:` — emoji again, plus "Error:" is redundant when it's clearly an error. (2) "We couldn't find your backup configuration!" — the exclamation mark is wrong, the apologetic "we" is wrong. The user doesn't need apology, they need to know what to do. (3) The "For more info, see the docs / contact support" is filler — an SRE staring at this at 3am does not want to open a browser, they want the next command they should type. Also: it doesn't say *which directories were searched*, which is the actual diagnostic value.

---

## Turn 4

**Prompt:**
> Try again. State what's wrong, where it looked, and what to do next. No filler.

**Output:**
```
no backup.toml found
  searched: . → /home/sam → /home → /
  hint: run `backup init` to create one, or `cd` into a directory that has a backup.toml
```

**Decision:** kept

**Notes:**
This is right. No "Error:" prefix — the absence of output already established that the command did nothing. The search path printed inline so you can see exactly which directories were checked. The hint gives two concrete next actions, and the second one is the one a senior would actually want first ("you're probably in the wrong directory"). The whole thing is four lines and tells you everything. Also notice — no exclamation marks anywhere. Calm voice. Calm voice is the whole register.

---

## Turn 5

**Prompt:**
> Now the success message after a snapshot completes.

**Output:**
```
✓ Snapshot created successfully!
  ID: a3f2b1c8
  Files: 12,847
  Size: 2.3 GB
  Time: 4.2s

Run `backup list` to see all your snapshots.
```

**Decision:** revised

**Notes:**
Closer. The checkmark is fine — that's a status glyph, not decoration. But "Snapshot created successfully!" is editorializing. Just say what happened: `snapshot a3f2b1c8 created`. The trailing "Run `backup list` to see all your snapshots." is the same filler problem from Turn 3 — the user knows what backup list does, they don't need a tutorial after every command. Strip that line. The stats block (Files, Size, Time) is good — those are facts the user might want without asking.

---
