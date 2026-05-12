# morning-brief

Today's tasks, captures, and time-sensitive items as a tight markdown summary.

## When to run

Daily 8am via launchd. Also on demand via `@Cleo run morning brief` or `/brief`.

## Steps

1. **Anchor on current state.** Read `$OBSIDIAN_VAULT/CLEO.md` to pick up the
   active portfolio and any standing context.
2. **Today's daily note.** Read `$OBSIDIAN_VAULT/daily/YYYY-MM-DD.md` for today's
   date (create if missing).
3. **Tasks due today.** Use Todoist (`todoist list --filter "today"` via Bash,
   or `mcp__todoist__query` if available) grouped by assignee.
4. **Fresh captures.** Scan `$OBSIDIAN_VAULT/inbox/` for files modified since
   yesterday's brief — list the titles, don't dump content.
5. **Time-sensitive.** Surface anything in projects/ or areas/ tagged
   `#today`, `#tomorrow`, or with a date in today's range. Use `qmd.query` to
   find candidates if grep won't cut it.
6. **One-line forecast.** Note any standing dependency from yesterday's
   eod-digest (e.g. "waiting on plumber callback").

## Output

Markdown, ~150–250 words. Post to `$DISCORD_DAILY_BRIEF_WEBHOOK`. Sign off
with 🦞.

Structure:

```
## Good morning 🦞

**Today (Mon, May 13)**

🗓️ <one-line context — kid school day? holiday? travel?>

**Tasks**
- [ ] @lesley — …
- [ ] @greg — …

**Fresh from the inbox**
- <title> — <one-line gist>

**Watch for**
- <time-sensitive thing>

🦞
```

## Tone

Default Cleo (playful, opinionated, brief). If a task is wildly overdue, call
it out — don't be polite about it.
