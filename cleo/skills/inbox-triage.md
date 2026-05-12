# inbox-triage

File new captures from `$OBSIDIAN_VAULT/inbox/` into the right PARA bucket.

## When to run

Every 2 hours, 9am–9pm via launchd. Writable — actually moves files.

## Steps

For each file in `$OBSIDIAN_VAULT/inbox/` older than 1 hour:

1. **Read it.** Use `Read` for the full content.
2. **Classify into PARA + sub-target:**
   - `projects/<project-slug>/` — bound to an active goal with a finish line.
     Use `qmd.query` against `projects/_index.md` and active project notes to
     find a match. If no clear active project, leave it in inbox and skip.
   - `areas/<area>/` — ongoing responsibility (finances, health, household,
     parenting). Look at the area names listed in `CLEO.md`.
   - `resources/<topic>/` — reference material, recipes, links worth keeping.
   - `archives/` — already-decided, no longer active. Rare for inbox items.
   - `people/<name>.md` — single person notes that fold into an existing
     people note (append, don't replace).
   - `ephemeral` — explicitly throwaway (shopping list crossed-out items,
     one-off reminders). Delete via Bash `rm`.
3. **Move via Write/Edit** (constrained to vault/inbox and vault/daily, so
   actually: Read source, Write to target, then `rm` source via Bash).
4. **Confidence threshold.** If you're <70% confident, leave the file in
   inbox and note it in the report. Over-filing is worse than under-filing.

## Output

Posted to `$DISCORD_CLEO_LOG_WEBHOOK` as a single markdown summary:

```
**Inbox triage** — <count> items processed

Filed:
- inbox/foo.md → projects/website-redesign/
- inbox/bar.md → areas/finances/

Left in inbox (ambiguous):
- inbox/baz.md — reason

Deleted (ephemeral):
- inbox/list-2026-05-12.md
```

## Tone

Operational. No commentary unless something looks weird (duplicate captures,
file with no usable content, etc.).
