# Second-Brain Architecture: Patterns Borrowed from Meta

Reference notes on the architectural pattern Cleo adopts from
[*How We Built an AI Second Brain for 60K Knowledge Workers* (Analytics at Meta, April 2026)](https://medium.com/@AnalyticsAtMeta/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-78c507dd795b).

## Why this matters here

We were already heading toward "Cleo on the Claude Agent SDK with launchd-scheduled pipelines". The Meta article documents the same shape at much larger scale (60k+ installs across engineers, PMs, designers, legal, finance, comms, sales) and surfaces four specific patterns we hadn't fully named:

1. **PARA structure** for the workspace
2. **Root `CLEO.md` (their `CLAUDE.md`)** as the persistent active-portfolio file
3. **Skills as plain markdown** — pluggable workflows, anyone can write one
4. **Progressive disclosure** over context dumping

All four are now baked into the `cleo/` scaffold. This doc records why.

## Patterns

### 1. PARA structure (Projects / Areas / Resources / Archives)

Tiago Forte's framework. The vault becomes:

| Directory | Meaning | Lifecycle |
|---|---|---|
| `projects/` | Bounded efforts with a finish line | Active until done |
| `areas/` | Ongoing responsibilities | Always active |
| `resources/` | Reference material | Persistent |
| `archives/` | Done / abandoned | Read-only by convention |
| `inbox/` | Fresh captures | Drained by triage |
| `daily/` | Daily notes | Append-only |
| `people/` | Per-person notes | Always active |

This isn't just organisation — it gives the agent **concrete targets to route to** during inbox triage, and a **lifecycle layer** so "what's active right now?" is answerable from `projects/` alone.

Implemented in: `cleo/skills/inbox-triage.md`, `cleo/src/cleo/permissions.py` (write-scoping).

### 2. Root state file (`CLEO.md`)

Meta's deployment has a root `CLAUDE.md` that "holds your identity and active portfolio across every session." Same idea here as `CLEO.md` at the vault root.

Contents:
- Household members
- Active projects (one line each)
- Active areas
- Standing context (travel, ongoing issues, health flags)
- Running log (one line per day, appended by `eod-digest`)

The system prompt instructs Cleo to read `CLEO.md` at the start of any non-trivial session, so she doesn't re-derive household state from scratch every time.

Implemented in: `cleo/templates/CLEO.md`, `cleo/prompts/cleo-system.md`.

### 3. Skills as markdown

Meta's central technical bet: workflows are **plain markdown files plus optional scripts**. No compiled code, no deployment pipeline. Anyone — including the agents themselves — can write, modify, and share a skill.

Cleo's adaptation:
- Skills live in `cleo/skills/<name>.md`
- A vault override path exists: `$OBSIDIAN_VAULT/skills/<name>.md` wins if present
- Each pipeline (`morning_brief.py`, etc.) is a 5-line wrapper around `run_skill("morning-brief")`
- The Discord/iMessage handlers can invoke the same skills on demand ("@Cleo run weekly review")

One workflow definition, two entry points (scheduled + on-demand). Add a skill = write a markdown file. Done.

Implemented in: `cleo/skills/`, `cleo/src/cleo/agent.py:load_skill()` and `run_skill()`.

### 4. Progressive disclosure

From the article: *"Progressive disclosure outperforms context dumping. Feeding an agent everything at once degrades output quality."*

Concretely:
- System prompt only lists each skill's one-line description (from `skills/_index.md`)
- Full skill content gets `Read` only when actually invoked
- `CLEO.md` carries the active portfolio; the full vault is queried on demand via `qmd.query`
- No vault dump in the system prompt — qmd is the retrieval surface

This pairs naturally with the qmd integration: rather than stuffing context into the prompt, the agent searches the index when it needs something specific.

Implemented in: `cleo/prompts/cleo-system.md` (skill index, not full skills), `cleo/skills/_index.md`.

## What we didn't (yet) borrow

- **Third Brain (team-shared layer).** Meta's pilot pools individual workspaces into a shared knowledge layer. For a household this would be `vault/household/` (shared) vs `vault/people/<name>/` (personal). Trust gating across that boundary is more nuanced than what `permissions.py` does today. Worth doing if the family/nanny boundary needs sharper isolation than channel-keyed nanny-mode provides.
- **Community-driven extension.** Meta's most-used features were built by non-author contributors. For a household that's "Lesley writes a skill and drops it in `$OBSIDIAN_VAULT/skills/`" — already supported by the vault-override path, just needs the muscle memory.
- **Eval / monitoring infra.** The article hints at instrumentation; we have launchd exit codes and stderr logs, nothing more sophisticated. Defer until the basics are running.

## Sources

- [How We Built an AI Second Brain for 60K Knowledge Workers (Analytics at Meta)](https://medium.com/@AnalyticsAtMeta/how-we-built-an-ai-second-brain-for-60k-knowledge-workers-78c507dd795b)
- Tiago Forte, *Building a Second Brain* — original PARA framework
