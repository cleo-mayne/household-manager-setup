# kid-handoff

Surface today's kid info for the nanny (or any caregiver) on demand.

## When to run

On @mention in any nanny-visible channel ("what's the plan for the girls
today?", "what time is Mira's class?", etc.). Nanny-mode persona applies —
neutral, no 🦞, no opinions.

## Steps

1. **Read** `$OBSIDIAN_VAULT/areas/kids/today.md` if it exists, or
   `$OBSIDIAN_VAULT/daily/YYYY-MM-DD.md` for today's date.
2. **Use `qmd.query`** to find any meal-plan, schedule, or medical notes that
   apply to today.
3. **Build the handoff** with:
   - Schedule (drop-offs, pickups, classes, appointments)
   - Meals (what's in the fridge, allergies, dietary notes)
   - Mood / sleep / health notes from the last 24 hours
   - Emergency contacts if asked
4. **Never read** from `areas/finances/`, `areas/work/`, or
   `projects/*-private/`. Nanny-mode is scoped to kid-relevant content only.

## Output

Inline reply to the channel. Short. Bulleted. No emoji.

```
Today (Mon, May 13):

- 09:00 Mira drop-off at Bayview Preschool
- 11:30 Reya wake-from-nap, milk + snack
- 14:30 Mira pickup
- 17:00 dinner — leftover chicken pasta in the blue container

Mira had a runny nose this morning, no fever. Reya slept through the night.
```

## Tone

Read off a clipboard. No personality. If the question is outside scope, say
"You'll want to ask Lesley or Greg about that."
