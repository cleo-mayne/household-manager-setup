# vault-health

Weekly sanity check on the Obsidian vault.

## When to run

Sundays 7am via launchd. Read-only.

## Steps

1. **Broken wiki-links.** Find `[[target]]` references where `target` doesn't
   exist. Use `Grep` for `\[\[[^]]+\]\]` and cross-check against `Glob`.
2. **Orphans.** Files in `projects/` or `areas/` with no inbound links from
   anywhere else. Exclude `daily/` and `inbox/`. Use `qmd.query` or `Grep`.
3. **Stale.** Files tagged `#wip` or `#followup` not modified in >90 days.
4. **Duplicate titles.** Same H1 across multiple folders.
5. **Skip:** `archives/` directory entirely — by definition things rot there.

## Output

Posted to `$DISCORD_CLEO_LOG_WEBHOOK`. Four short sections with **counts and
2–3 examples each** — not exhaustive lists. This is a triage doc, not an
audit. Cap at ~400 words.

```
**Weekly vault health**

🔗 Broken links (12)
- projects/website/spec.md → [[design-doc-v2]] (not found)
- areas/finances/2026-q1.md → [[montalvo-property]] (not found)
- …

🏝️ Orphans (4)
- resources/recipes/dosa.md
- …

🕸️ Stale (8)
- projects/podcast-launch.md (#wip, last modified 2025-11-03)
- …

♊ Duplicate titles (2)
- "Travel checklist" in resources/ and projects/hakone-trip/
```

## Tone

Compact. No softening. If the vault is in good shape, say so in one line and
stop.
