# Cleo (Claude Agent SDK scaffold)

Replacement for the OpenClaw-hosted Cleo. Python, `claude-agent-sdk`, `discord.py`, launchd.

**Deploying for the first time?** See [DEPLOY.md](DEPLOY.md) for the end-to-end runbook.

## Layout

```
cleo/
├── pyproject.toml
├── .env.example
├── prompts/
│   ├── cleo-system.md       # full family persona (playful, 🦞, opinionated)
│   └── cleo-nanny-mode.md   # stripped-down, no personality, read-only
├── src/cleo/
│   ├── config.py            # env loading, persona selection
│   ├── agent.py             # ClaudeAgentOptions builder + one-shot helper
│   ├── permissions.py       # can_use_tool callback (path scoping, bash blocklist)
│   ├── conversation.py      # per-channel ClaudeSDKClient sessions (multi-turn memory)
│   ├── discord_handler.py   # @mention listener, /reset, persona switching
│   ├── imessage_handler.py  # BlueBubbles webhook receiver, same ConversationStore
│   └── scheduled/
│       ├── morning_brief.py   # 8am → #daily-brief
│       ├── inbox_triage.py    # hourly-ish → files vault/inbox/
│       ├── vault_health.py    # Sunday 7am → #cleo-log
│       ├── knowledge_graph.py # daily 6am → link suggestions → #cleo-log
│       └── qmd_reindex.py     # hourly → refresh qmd vault embeddings
└── launchd/
    ├── com.cleo.discord.plist
    ├── com.cleo.imessage.plist
    ├── com.cleo.morning-brief.plist
    ├── com.cleo.inbox-triage.plist
    ├── com.cleo.vault-health.plist
    ├── com.cleo.knowledge-graph.plist
    └── com.cleo.qmd-reindex.plist
```

## Search: qmd (brain_search retired)

Vault search runs through [qmd](https://github.com/tobi/qmd) — a local hybrid search engine (BM25 + vector + LLM rerank, all-local via GGUF models) that ships its own MCP server. Wired in `agent.py` as the `qmd` MCP server. The `brain` MCP server is still wired for `brain_capture` and `brain_health`, but `brain_search` is **explicitly retired** — `permissions.py` denies any `mcp__brain__search` call when qmd is enabled, and the system prompt tells Cleo qmd is the only sanctioned search path.

- **Index**: `~/.cache/qmd/index.sqlite` (auto-managed by qmd)
- **Reindex**: hourly via `scheduled/qmd_reindex.py` (`qmd embed`)
- **Disable / fall back**: set `QMD_ENABLED=false` in `.env` and the permission gate lifts, brain_search becomes callable again.

See [DEPLOY.md](DEPLOY.md) for one-time qmd setup (npm install, collection add, initial embed).

## Setup

```bash
cd cleo/
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env     # fill in tokens
```

### Required env vars
- `ANTHROPIC_API_KEY`
- `DISCORD_TOKEN` (existing bot token from OpenClaw secrets, see `discord/existing-setup.md`)
- `DISCORD_GUILD_ID` — already `1477094930647355626`
- `TRUSTED_DISCORD_IDS` — comma-separated user IDs for Lesley and Greg (full tool access)
- `NANNY_CHANNEL_IDS` — comma-separated channel IDs where Cleo uses nanny-mode persona
- `OBSIDIAN_VAULT` — absolute path to the vault
- `DISCORD_DAILY_BRIEF_WEBHOOK` — webhook URL for the #daily-brief channel
- `DISCORD_CLEO_LOG_WEBHOOK` — webhook URL for #cleo-log (pipeline output)

### iMessage (optional)
- `BLUEBUBBLES_URL`, `BLUEBUBBLES_PASSWORD` — self-hosted BlueBubbles server
- `IMESSAGE_LISTEN_HOST`, `IMESSAGE_LISTEN_PORT` — where the bridge receives BlueBubbles webhooks
- `TRUSTED_IMESSAGE_HANDLES` — comma-separated emails/phone numbers granted full tool access

Point BlueBubbles' new-message webhook at `http://<host>:<port>/webhook`.

## Run locally

```bash
# Long-running services
python -m cleo.discord_handler
python -m cleo.imessage_handler

# One-shot pipelines (for testing — launchd runs them on schedule)
python -m cleo.scheduled.morning_brief
python -m cleo.scheduled.inbox_triage
python -m cleo.scheduled.vault_health
python -m cleo.scheduled.knowledge_graph
```

## Install under launchd

```bash
# Edit plists: replace __CLEO_DIR__ (e.g. /Users/greg/code/cleo) and __PYTHON__ (e.g. /Users/greg/code/cleo/.venv/bin/python)
sed -i '' "s|__CLEO_DIR__|$PWD|g; s|__PYTHON__|$PWD/.venv/bin/python|g" launchd/*.plist
mkdir -p logs
cp launchd/*.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.cleo.discord.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.cleo.morning-brief.plist
```

Unload:
```bash
launchctl bootout gui/$(id -u)/com.cleo.discord
```

## How personality is preserved

- **Two system prompt files.** `cleo-system.md` is the full Cleo — playful, opinionated, lobster emoji, warmer with Mira, direct with Greg/Lesley. `cleo-nanny-mode.md` is a neutral scheduling assistant.
- **Channel-keyed persona switching.** `discord_handler.py` checks whether the incoming message's channel is in `NANNY_CHANNEL_IDS`; if so, it flips to nanny mode for that turn.
- **Multi-turn memory per channel.** `conversation.py` keeps a `ClaudeSDKClient` per channel so consecutive messages share context — you can actually *talk* to Cleo, she doesn't forget between turns. Idle channels are reaped after 30min.
- **Persona change resets the session.** If a channel's trust level or persona flips mid-conversation, the session is torn down and rebuilt to prevent leakage.

## Trust model

| Sender | Channel | Tools |
|---|---|---|
| In `TRUSTED_DISCORD_IDS` | Family channel | Full (Read/Write/Edit/Bash/MCP) |
| In `TRUSTED_DISCORD_IDS` | Nanny channel | Read-only + nanny persona |
| Everyone else | Any | Read-only + nanny persona |

Untrusted message content is never treated as instructions — the system prompt frames every incoming message as `[channel: X] sender: message` so the model sees it as data.

## Permission model (`permissions.py`)

Defence-in-depth on top of `allowed_tools`. The `can_use_tool` callback inspects every tool call and can deny or rewrite it before it runs:

- **Nanny mode:** Write / Edit / Bash always denied.
- **Read-only contexts (untrusted senders):** Write / Edit / Bash denied.
- **Writes:** must land under `$OBSIDIAN_VAULT/inbox/` or `$OBSIDIAN_VAULT/daily/`. Writes elsewhere — plugins, config, `.obsidian/` — are rejected.
- **Bash:** blocks `rm -rf`, fork bombs, `dd if=`, `curl … | sh`, `sudo`, `mkfs`/`fdisk`.

Tune in `permissions.py`. The callback is wired automatically via `build_options()`.

## What's not here yet

- ElevenLabs `sag` voice handoff — wire after reply text is produced.
- Prompt caching — add `cache_control` blocks on the system prompt once the SDK version is pinned.
- Discord interactive components (buttons on task/grocery messages).
- Alert-fanout helper for pipeline failures (`#alerts` webhook on non-zero exit).

## Migrating from OpenClaw

1. Stand this scaffold up in parallel (different bot user if you want a clean cutover, or reuse the existing token).
2. Test one pipeline end-to-end (morning brief is the easiest — low stakes, observable).
3. Shift `@Cleo` handling over channel-by-channel.
4. Turn off the OpenClaw Discord integration.
5. Port remaining pipelines one at a time.
