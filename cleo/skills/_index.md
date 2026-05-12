# Cleo Skills

Skills are reusable workflows written as markdown. Each skill tells Cleo how to
complete one specific job, step by step. Anyone (including Cleo herself) can
add a skill by writing a markdown file here or in `$OBSIDIAN_VAULT/skills/`.

This pattern is borrowed from
[Meta's AI Second Brain](https://medium.com/@AnalyticsAtMeta/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-78c507dd795b).
Key principles:

- **Plain markdown, no code.** Anyone can read, copy, and modify a skill.
- **Progressive disclosure.** The system prompt only lists each skill's
  one-line description from this index. Full instructions get loaded when the
  skill is invoked. Keeps context lean.
- **Same skills, two entry points.** Scheduled pipelines (`launchd` →
  `cleo/scheduled/*.py`) and on-demand requests (`@Cleo run weekly-review`)
  both load the same skill file. One source of truth per workflow.

## Skill index

| Skill | Trigger | Writable | Description |
|---|---|---|---|
| `morning-brief` | Daily 8am cron | no | Today's tasks, captures, time-sensitive items. → #daily-brief |
| `eod-digest` | Daily 9pm cron | no | What got done today, what's open, what's tomorrow. → #daily-brief |
| `inbox-triage` | Every 2h, 9am–9pm | yes | File new captures into PARA. → #cleo-log |
| `vault-health` | Sundays 7am | no | Broken links, orphans, stale notes. → #cleo-log |
| `knowledge-graph` | Daily 6am | no | Backlink suggestions for recent notes. → #cleo-log |
| `kid-handoff` | On nanny @mention | no | Surface today's kid info (schedule, meals, notes). |
| `weekly-review` | On request | no | Tiago Forte-style weekly review: review PARA, surface stale projects. |

## How Cleo invokes a skill

1. User says "run weekly review" or a launchd job calls
   `run_skill(settings, "weekly-review")`.
2. Cleo reads `cleo/skills/weekly-review.md` (or `$OBSIDIAN_VAULT/skills/weekly-review.md`
   if it exists — vault overrides repo).
3. She follows the steps in the skill, using whatever tools the skill calls for.
4. Output goes wherever the skill says — Discord webhook, vault, inline reply.

## Writing a new skill

Create a markdown file with this shape:

```markdown
# Skill name (kebab-case to match the filename)

One-line description that fits in the index table.

## When to run
When this skill should fire and who can trigger it.

## Steps
1. Concrete action with the tool to use (qmd.query / Read / Write / Bash etc.).
2. Next action.
3. ...

## Output
Where the result goes. Discord webhook? Vault file? Inline reply?

## Tone
Optional. Override the default Cleo voice for this skill if needed.
```

Drop it in this directory, or in `$OBSIDIAN_VAULT/skills/` for personal skills
that don't belong in the repo. No restart needed — skills are read fresh each
invocation.
