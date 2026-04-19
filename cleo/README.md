# Cleo (Claude Agent SDK scaffold)

Replacement for the OpenClaw-hosted Cleo. Python, `claude-agent-sdk`, `discord.py`, launchd.

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
│   ├── conversation.py      # per-channel ClaudeSDKClient sessions (multi-turn memory)
│   ├── discord_handler.py   # @mention listener, /reset slash command, persona switching
│   └── scheduled/
│       └── morning_brief.py # 8am pipeline → Discord webhook
└── launchd/
    ├── com.cleo.discord.plist
    └── com.cleo.morning-brief.plist
```

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

## Run locally

```bash
# Discord bot (long-running)
python -m cleo.discord_handler

# One-shot morning brief (for testing)
python -m cleo.scheduled.morning_brief
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

## What's not here yet

- iMessage handler (BlueBubbles bridge) — one more module in the same shape as `discord_handler.py`, feeding into the same `ConversationStore`.
- Ports of `inbox-triage.lobster`, `vault-health.lobster`, `knowledge-graph.lobster` — each becomes a file in `scheduled/` with a `launchd` plist.
- ElevenLabs `sag` voice handoff — wire after reply text is produced.
- `canUseTool` callback for per-tool fine-grained gating.
- Prompt caching — add `cache_control` blocks on the system prompt once the SDK version is pinned.

## Migrating from OpenClaw

1. Stand this scaffold up in parallel (different bot user if you want a clean cutover, or reuse the existing token).
2. Test one pipeline end-to-end (morning brief is the easiest — low stakes, observable).
3. Shift `@Cleo` handling over channel-by-channel.
4. Turn off the OpenClaw Discord integration.
5. Port remaining pipelines one at a time.
