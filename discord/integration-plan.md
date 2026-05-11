# Discord Integration Plan — Cleo Household Bot

## Goal

Wire Cleo's second brain tools into the existing Discord server so the family has a rich dashboard and automation channel alongside iMessage.

## Architecture

```
Discord Server (Guild 1477094930647355626)
  │
  ├── #general          Family chat (Cleo responds when @mentioned)
  ├── #cleo-log         Automated activity feed (webhook, low-noise)
  ├── #daily-brief      Morning briefing posted daily at 8am
  ├── #grocery          Shopping list with interactive buttons
  ├── #tasks            Todoist task feed + quick capture
  ├── #brain            Search and knowledge graph queries
  ├── #alerts           Urgent notifications (high-priority, DM fallback)
  └── 🔊 House          Voice channel for TTS announcements
```

```
Cleo (bot)
  │
  ├── Slash commands     /search, /task, /inbox, /health, /capture
  ├── Message listener   @Cleo triggers (requireMention: true)
  ├── Webhooks           Pipelines post to #cleo-log, #daily-brief
  ├── Voice              TTS announcements via ElevenLabs
  └── Interactive        Buttons for task completion, approval gates
```

## Slash Commands

| Command | Description | Maps To |
|---|---|---|
| `/search <query>` | Hybrid search across vault | `qmd query` MCP tool (BM25 + vector + LLM rerank) |
| `/task <text>` | Quick-add task via Todoist NLP | Todoist Quick Add API |
| `/inbox` | Show inbox items | `brain inbox` |
| `/health` | Vault health summary | `brain-health --report` |
| `/capture <text>` | Save note to vault inbox | `brain_capture` MCP tool |
| `/brief` | Trigger morning briefing now | `morning-brief` pipeline |
| `/links` | Show recent link suggestions | `knowledge-graph` pipeline output |
| `/stats` | Vault and task statistics | `qmd status` + Todoist stats |

## Webhook Integrations

Pipelines post updates via Discord webhooks (no bot code needed):

| Source | Channel | Trigger |
|---|---|---|
| `morning-brief.lobster` | `#daily-brief` | Daily 8am cron |
| `inbox-triage.lobster` | `#cleo-log` | After filing notes |
| `vault-health.lobster` | `#cleo-log` | Weekly health report |
| `knowledge-graph.lobster` | `#cleo-log` | After discovering links |
| `todoist-sync.lobster` | `#tasks` | After syncing tasks |
| Package delivery alerts | `#alerts` | External webhook |
| Calendar reminders | `#alerts` | 1hr before events |

## Interactive Features

### Task Management in #tasks
```
📋 Tasks Due Today (3)

1. ☐ Check on Solar — @lesley — Adulthood
2. ☐ Pay Montalvo Property Taxes — @lesley — Finances
3. ☐ Grocery run — @greg — Household

[✅ Complete] [📝 Add Task] [🔄 Refresh]
```

Buttons trigger Todoist API calls (complete, create, refresh list).

### Grocery List in #grocery
```
🛒 Grocery List

- Milk (2%)
- Paper towels
- Bananas
- Chicken thighs

[➕ Add Item] [🛒 Send to Instacart] [✅ Clear Completed]
```

### Approval Gates in #cleo-log
```
🔔 Inbox Triage — 3 items to file

1. Hakone Day Trip Guide → 3-resources
2. New recipe idea → ideas
3. Greg contact update → people

[✅ Approve All] [❌ Skip] [✏️ Review]
```

Pipeline approval gates surface in Discord instead of requiring CLI interaction.

## Voice Announcements

Using the existing ElevenLabs TTS (`sag` CLI):
- Morning brief summary read aloud in the House voice channel
- "Dinner is ready" / "Package delivered" announcements
- Storytime for Mira (already a documented Cleo feature)

## Implementation Phases

### Phase 1: Foundation (Day 1)
1. Verify bot token is still valid and server accessible
2. Create channel structure (#cleo-log, #daily-brief, #tasks, #grocery, #brain, #alerts)
3. Generate webhook URLs for each channel
4. Create a `discord-bot/` directory in Clawdbot with bot scaffolding
5. Implement basic @mention response handler (echo test)

### Phase 2: Webhooks (Day 1-2)
1. Add webhook posting to existing pipelines:
   - `morning-brief.lobster` → POST formatted embed to #daily-brief webhook
   - `inbox-triage.lobster` → POST to #cleo-log webhook
   - `vault-health.lobster` → POST to #cleo-log webhook
2. Write `discord-webhook` helper script:
   ```bash
   discord-webhook --channel daily-brief --title "Morning Brief" --body "$content"
   ```
3. Test end-to-end: run morning-brief pipeline → see embed appear in Discord

### Phase 3: Slash Commands (Day 2-3)
1. Register slash commands with Discord API
2. Implement command handlers:
   - `/search` → calls `vault-search`, formats as embed
   - `/task` → calls Todoist Quick Add API
   - `/inbox` → calls `brain inbox`, formats as embed
   - `/health` → calls `brain-health --stats`
   - `/capture` → writes note to vault inbox with metadata
3. Deploy bot process (can run on the Mac Studio alongside existing services)

### Phase 4: Interactive Components (Day 3-4)
1. Task list with completion buttons
2. Grocery list management
3. Approval gate buttons for pipeline triage
4. Button interaction handlers

### Phase 5: Voice (Day 4-5)
1. Bot joins House voice channel on command
2. TTS via ElevenLabs `sag` CLI → pipe audio to Discord voice
3. Morning brief voice summary
4. Ad-hoc announcements ("Hey Cleo, tell everyone dinner is ready")

## Security

Carry forward the security hardening recommendations:

```
Discord agent tool restrictions:
  Allow: messaging, brain search, brain capture, todoist read/write
  Deny: exec, process, browser, gateway, cron, file deletion

Message trust model:
  - Discord messages are UNTRUSTED INPUT
  - Slash commands have defined, safe operations
  - @mention freeform text goes through Cleo's safety layer
  - Never execute arbitrary commands from Discord messages
  - DM policy: pairing (must have prior interaction)
```

## Bot Technology Options

| Option | Pros | Cons |
|---|---|---|
| **discord.py** | Python (matches vault-index.py, MCP server), mature, well-documented | Needs async event loop |
| **discord.js** | Node.js, largest ecosystem, Components V2 support | Different language from brain tools |
| **OpenClaw Discord channel** | Already configured, handles message routing | May need updates for new tools |

**Recommendation**: Use **discord.py** for the bot since the brain tools are Python-based (vault-index.py, MCP server.py). Keep it simple — a single `bot.py` file that imports the same `run_cli()` helper pattern from the MCP server.

## File Structure

```
discord-bot/
├── bot.py              Main bot (discord.py, slash commands, event handlers)
├── webhooks.py         Webhook posting helper for pipelines
├── config.json         Channel IDs, webhook URLs (gitignored)
├── requirements.txt    discord.py, aiohttp
├── .env                Bot token (gitignored)
└── embeds/             Embed templates for formatted messages
    ├── morning-brief.py
    ├── health-report.py
    └── task-list.py
```

## Dependencies

- `discord.py>=2.0` — Bot framework
- Existing bot token from OpenClaw secrets
- Existing Discord server (Guild 1477094930647355626)
- Webhook URLs (created per-channel in Discord server settings)
- All existing brain-cli tools (called via subprocess)
