# Rebuilding Cleo on Claude-Native Tools: Feasibility Research

## 1. Executive Summary

**Yes. Ditch OpenClaw, rebuild on the Claude Agent SDK.**

OpenClaw was a harness that existed to spare us from writing our own agent loop. Two things changed:
1. It went pay-per-use, so it's now a metered line item on top of the Anthropic bill.
2. It's been fragile and flaky in practice, which is the worse problem.

Meanwhile, the Claude Agent SDK has matured into a first-class framework that provides the same primitives — agent loops, tool use, MCP, permissions, session handling — with a clean Python API, native MCP support, and the full flexibility to wire it to Discord, iMessage, launchd, and the existing `brain` MCP servers.

**Recommendation: rebuild Cleo as a Python process using the Claude Agent SDK, with discord.py for Discord, BlueBubbles for iMessage, launchd for scheduled pipelines, and the existing MCP servers embedded in-process. Keep the Anthropic API as the model backend initially. If local models become desirable later, route through LiteLLM (see [local-models.md](local-models.md)).**

---

## 2. The Three Claude-Native Options

| Capability | **Claude Code (headless `-p`)** | **Claude Agent SDK** | **Claude API (raw)** |
|---|---|---|---|
| Agentic loop | Built-in | Built-in | DIY |
| Long-running sessions | No (single-shot) | Yes (event streaming) | DIY |
| MCP server integration | Via `.mcp.json` | Native `mcpServers` | Beta (`mcp-client-2025-11-20`) |
| Scheduling | External (cron/launchd) | External (cron/launchd) | External |
| Permission / tool control | `--allowedTools`, settings | `allowedTools` + `canUseTool` callback | `tools=[...]` only |
| Memory / context persistence | CLAUDE.md + auto-memory | Sessions + Agent memory (preview) | DIY (Files API) |
| Headless / webhook-friendly | Yes (`-p`) | Yes | Yes |
| Maintenance burden | Low | Medium | High |
| Best for | Admin/developer work on the host | **The Cleo agent itself** | One-shot webhook classifiers |

**Pick: Agent SDK is the core. Claude Code stays for admin/developer work on the Mac Studio. Raw API only for stateless webhook handlers.**

---

## 3. Recommended Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Household Interfaces                        │
├──────────────────────────────────────────────────────────────┤
│  Discord (discord.py)  │  iMessage (BlueBubbles REST)  │ CLI │
└──────────┬─────────────┴──────────────┬───────────────┴──┬──┘
           │                            │                  │
           └──────────────┬─────────────┴──────────────────┘
                          │
              ┌───────────▼──────────────────┐
              │  Cleo core (Python)          │
              │  - discord_handler.py        │
              │  - imessage_handler.py       │
              │  - scheduled/*.py (launchd)  │
              │  claude-agent-sdk:           │
              │    query() + ClaudeAgentOptions
              └───────────┬──────────────────┘
                          │
        ┌─────────────────┼─────────────────────────┐
        │                 │                         │
┌───────▼────────┐ ┌──────▼──────────┐ ┌────────────▼──────────┐
│ MCP servers    │ │ Anthropic API   │ │ Tools                 │
│ (embedded)     │ │ (Sonnet/Opus)   │ │ Todoist CLI           │
│ - brain_search │ │                 │ │ ElevenLabs `sag`      │
│ - brain_capture│ │                 │ │ Obsidian vault FS     │
│ - brain_health │ │                 │ │                       │
└────────────────┘ └─────────────────┘ └───────────────────────┘
```

Everything runs as Python processes on the Mac Studio under launchd. No separate harness, no external control plane, no pay-per-use middleware.

---

## 4. Discord Handler (example)

```python
# cleo/discord_handler.py
import asyncio, os
import discord
from discord.ext import commands
from claude_agent_sdk import query, ClaudeAgentOptions

TRUSTED_IDS = {int(x) for x in os.environ["TRUSTED_USERS"].split(",")}

class Cleo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author == self.bot.user or not self.bot.user.mentioned_in(msg):
            return
        if msg.author.id not in TRUSTED_IDS:
            return await msg.reply("Sorry, I don't know you.")

        async for event in query(
            prompt=f"[Discord:{msg.channel.name}] {msg.author.name}: {msg.content}",
            options=ClaudeAgentOptions(
                system_prompt=open("prompts/cleo-system.md").read(),
                allowed_tools=["Read", "Grep", "Glob", "Bash"],
                mcp_servers={"brain": {"command": "python",
                                       "args": ["-m", "brain.mcp_server"]}},
                permission_mode="acceptEdits",
            ),
        ):
            if event.type == "assistant" and getattr(event, "text", None):
                await msg.reply(event.text[:2000])

async def main():
    bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
    await bot.add_cog(Cleo(bot))
    await bot.start(os.environ["DISCORD_TOKEN"])

if __name__ == "__main__":
    asyncio.run(main())
```

Key points:
- Trust enforcement is a simple user-ID allowlist — replaces OpenClaw's `groupPolicy`.
- `allowed_tools` + MCP servers in `ClaudeAgentOptions` replace OpenClaw's per-agent tool allowlist.
- System prompt is a plain markdown file we own and version.
- Everything streams; we can post partial updates back to Discord.

---

## 5. Scheduled Pipelines

launchd replaces OpenClaw's pipeline runner. Each `.lobster` becomes a small Python script invoked on schedule.

```xml
<!-- ~/Library/LaunchAgents/com.cleo.morning-brief.plist -->
<plist version="1.0"><dict>
  <key>Label</key><string>com.cleo.morning-brief</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/python3</string>
    <string>/Users/greg/cleo/scheduled/morning_brief.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
</dict></plist>
```

```python
# cleo/scheduled/morning_brief.py
import asyncio, os, requests
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    result = None
    async for event in query(
        prompt="Generate today's morning brief. Read today's daily note, inbox, and Todoist due-today list. Output a concise markdown summary.",
        options=ClaudeAgentOptions(
            system_prompt=open("prompts/cleo-system.md").read(),
            allowed_tools=["Read", "Grep", "Glob"],
            mcp_servers={"brain": {"command": "python",
                                   "args": ["-m", "brain.mcp_server"]}},
            permission_mode="dontAsk",
        ),
    ):
        if event.type == "result":
            result = event.result

    requests.post(os.environ["DISCORD_DAILY_BRIEF_WEBHOOK"],
                  json={"content": result})

asyncio.run(main())
```

Failure handling: launchd exit codes → a tiny `alert.py` that posts to `#alerts` on non-zero.

---

## 6. Mapping OpenClaw → Claude-Native

| OpenClaw feature | What we lose | Replacement | Effort |
|---|---|---|---|
| DM routing + channel policies | Managed message filtering | System prompt + discord.py listeners + TRUSTED_IDS allowlist | ~2h |
| Multi-user pairing | User→agent assignment | Settings scopes + env whitelist | ~1h |
| Per-agent tool allowlist | Managed tool isolation | `allowed_tools` + `canUseTool` callback | ~3h |
| Secrets management | Centralized vault | `.env` + dotenv (or 1Password CLI for prod) | 30m |
| Message trust model | Built-in verification | Hardcode allowed Discord IDs; iMessage only from Mac Studio | ~1h |
| Agent lifecycle mgmt | Restart resilience | launchd KeepAlive + health-check webhook to `#alerts` | ~4h |
| `.lobster` pipelines | DSL runner | Python files invoked by launchd | ~1 day to port |

Total porting work: **~1–2 weeks end-to-end** for a solo maintainer who already knows the existing codebase.

---

## 7. iMessage + Voice (unchanged from OpenClaw era)

- **iMessage:** No official Apple/Anthropic support. Keep BlueBubbles self-hosted on the Mac Studio, REST API. A thin `imessage_handler.py` polls/receives webhooks from BlueBubbles and feeds messages into the same `query()` loop as Discord.
- **Voice:** ElevenLabs `sag` CLI stays. Pipe Claude's reply text through `sag` → `afplay`. No change.

---

## 8. Cost

| Line item | Status quo | Claude-native |
|---|---|---|
| Anthropic API | ~$50–120/mo | ~$30–80/mo (with prompt caching on system prompt + vault-context blocks) |
| OpenClaw fee | New, pay-per-use | **$0** |
| Hosting | Mac Studio (sunk) | Mac Studio (sunk) |
| Total | Paid harness + API | **API only** |

Prompt caching is the big lever: Cleo's system prompt + stable vault-context blocks should cache cleanly, cutting effective per-turn cost materially. See Anthropic's prompt-caching docs.

---

## 9. Maintenance Burden

| Task | OpenClaw | Claude-native |
|---|---|---|
| Update agent behavior | OpenClaw config files | `prompts/cleo-system.md` + code |
| Add a tool / MCP server | Unclear escape hatch | `mcp_servers={...}` in `ClaudeAgentOptions` |
| Upgrade model | OpenClaw version pin | `model="claude-opus-4-7"` one line |
| Monitor health | Opaque | launchd exit codes + Discord alerts |
| Debug user issue | Opaque logs | Full session transcripts on disk |
| Migrate data | Vendor lock-in | Plain markdown + standard APIs |

**Net: meaningfully lower burden. The failure modes we do hit are our own code, which is debuggable.**

---

## 10. Gotchas

1. **MCP servers are local-only by default.** Embed them in the same Python process (simplest) or expose via HTTPS if we ever move to cloud hosting.
2. **Session continuity.** Agent SDK sessions are ephemeral by default. Use `CLAUDE.md`-style persistent context plus Agent memory (preview) for cross-session learning.
3. **iMessage limitation is unchanged.** BlueBubbles or Sendblue — neither is Anthropic-blessed. This was true under OpenClaw too.
4. **Claude Code Routines (scheduled tasks) are still research preview** as of April 2026. Use launchd; migrate to Routines later if they stabilize.
5. **New ownership surface:** we now own launchd jobs, Python deps, `.env` secrets, and Discord bot uptime. That's the tradeoff for getting off a flaky harness.

---

## 11. Implementation Plan

### Phase 1: Core agent (1–2 weeks)
- Stand up Python project with `claude-agent-sdk`
- Wire existing MCP servers (`brain_search`, `brain_capture`, `brain_health`) as `mcpServers`
- Discord bot scaffold with @mention handler + trusted-user gate
- End-to-end test: `@Cleo what's on my plate today?` → real Todoist + vault lookup → reply

### Phase 2: Integrations (1 week)
- BlueBubbles iMessage bridge
- Todoist CLI wiring
- ElevenLabs `sag` voice handoff
- Multi-user trust enforcement + `canUseTool` callback

### Phase 3: Scheduled pipelines (1 week)
- Port `morning-brief.lobster` → `morning_brief.py` + launchd
- Port `inbox-triage`, `vault-health`, `knowledge-graph`
- Health alerts to `#alerts` on failure

### Phase 4: Polish (1 week)
- Prompt caching on system prompt + stable vault blocks
- Slash commands on Discord
- Interactive buttons (approval gates)
- Shutdown of OpenClaw

---

## 12. Sources

- [Claude Agent SDK Quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart)
- [Claude Code Headless Mode](https://code.claude.com/docs/en/headless)
- [Claude Code Hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code Scheduled Tasks / Routines](https://code.claude.com/docs/en/scheduled-tasks)
- [MCP Connector for Claude API](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
- [Prompt Caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)
- [BlueBubbles](https://github.com/BlueBubblesApp/bluebubbles-app)
- [discord.py](https://discordpy.readthedocs.io/)
- [Discord MCP + Agent SDK (Composio)](https://composio.dev/toolkits/discord/framework/claude-agents-sdk)
