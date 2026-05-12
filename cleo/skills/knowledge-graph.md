# knowledge-graph

Suggest backlinks between recent notes. Review-only — humans add the links.

## When to run

Daily 6am via launchd. Read-only.

## Steps

For each note modified in the last 7 days:

1. **Find candidates** with `qmd.query` using the note's title and a sentence
   or two of its body as the query.
2. **Filter:**
   - Skip if the link already exists in either direction.
   - Skip if the candidate is in `archives/` or `daily/`.
   - Skip if your semantic confidence is low — over-linking is worse than
     under-linking.
3. **Pick the top 1–3** per source note.
4. **State the reason** in one short clause per suggestion.

## Output

Posted to `$DISCORD_CLEO_LOG_WEBHOOK`. Group by source note. Cap at ~600 words
total — if there are too many suggestions, surface only the strongest ones.

```
**Link suggestions** — review and add manually

### projects/website-redesign/spec.md
- → resources/design-systems/material-3.md (cites the same color theory)
- → people/sara-designer.md (you mentioned her in this spec)

### areas/finances/2026-q1.md
- → projects/montalvo-property/taxes.md (overlapping tax-prep context)
```

## Tone

Just the list. No editorializing.
