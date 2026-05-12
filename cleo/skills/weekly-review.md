# weekly-review

Tiago Forte-style weekly review across the vault.

## When to run

On request: "@Cleo run a weekly review". Read-only. Not on launchd by default —
weekly review is a deliberate practice, not a schedule.

## Steps

1. **Anchor on `CLEO.md`.** Read the current active portfolio.
2. **Per active project** (in `projects/`):
   - Has there been activity in the last 7 days?
   - Does the project still have a clear next action?
   - Is the goal still relevant, or should it move to `archives/`?
3. **Per area** (in `areas/`):
   - Anything captured this week that updates the area's standing notes?
   - Any followups overdue?
4. **Inbox state.** How much is sitting in `inbox/`? If it's >20 items, flag it.
5. **Calendar / Todoist.** Did anything fall through? (Use `todoist list
   --filter "overdue"`.)

## Output

Inline reply. Long-form for once — this is a thinking document, not a feed
post. Structure:

```
# Weekly review — May 13, 2026

## What's moving 🟢
- projects/podcast-launch: 3 commits, demo recorded, on track
- areas/finances: quarterly close started

## What's stuck 🟡
- projects/website-redesign: no activity 11 days. Next action: pick a designer.
- areas/health/dentist: appointment punted twice. Just book it.

## What to retire 🔴
- projects/old-house-renovation: dormant since Feb. Archive.

## Inbox
12 items, mostly from Hakone trip. Triage manually before next sync.

## Followups
- @greg: response to the Montalvo tax letter (overdue 4 days)
- @lesley: school registration deadline May 18
```

## Tone

Direct. Mark things red without softening. The whole point of a weekly review
is to notice what's stuck before it rots — politeness defeats the purpose.
