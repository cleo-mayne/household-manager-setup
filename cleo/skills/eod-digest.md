# eod-digest

End-of-day digest. The bracket to morning-brief — closes out the day and
prepares tomorrow.

## When to run

Daily 9pm via launchd. Also on demand via `@Cleo wrap up the day`.

## Steps

1. **What got done.** Todoist tasks completed today (`todoist list --filter
   "completed today"` via Bash). Group by assignee.
2. **What's still open from today.** Tasks due today still incomplete. Flag the
   ones that have rolled over more than once.
3. **Captures today.** Notes added to `$OBSIDIAN_VAULT/inbox/` today —
   anything not yet filed? (`inbox-triage` runs at 9pm too, but log
   leftovers.)
4. **Conversations worth noting.** If any Discord/iMessage thread today produced
   a household decision (use `qmd.query` over today's daily note), surface it
   as a one-liner.
5. **Tomorrow.** Tasks due tomorrow (`todoist list --filter "tomorrow"`).
   Highlight if tomorrow has any time-sensitive blockers (appointments, school
   events, deliveries).
6. **Update `CLEO.md`.** Append a one-line entry to the running log section:
   `- YYYY-MM-DD: <one-sentence summary>`. This is the only `Edit` this skill
   makes.

## Output

Markdown, ~150–250 words. Post to `$DISCORD_DAILY_BRIEF_WEBHOOK`.

```
## Wrapping up 🦞

**Done today**
- @greg — …
- @lesley — …

**Still open**
- [ ] <task> (rolled over <n> days)

**Captures not yet filed**
- <count> items in inbox/

**Tomorrow**
- 09:30 — <thing>
- [ ] @greg — …

🦞
```

## Tone

Reflective but brisk. No pep talks. If today went sideways, name it dryly
("rough one — three tasks bounced") rather than spinning.
