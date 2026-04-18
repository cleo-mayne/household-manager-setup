# Household Manager Setup

Platform evaluation and setup documentation for a household AI assistant system.

## Research

Deep research across the five platform and runtime decisions:

| Decision | Research | Verdict |
|---|---|---|
| **Chat platform** | [Discord vs Slack](research/discord-vs-slack.md) | **Discord** — $0/mo, unlimited history, unlimited bots, voice channels |
| **Knowledge management** | [Obsidian vs Notion](research/obsidian-vs-notion.md) | **Obsidian** — local-first, direct filesystem access for AI agent, privacy |
| **Task management** | [Stay on Todoist or migrate?](research/todoist-stay-or-migrate.md) | **Stay on Todoist** — best API + NLP combo, already integrated |
| **Agent harness** | [Claude-tools-only rebuild](research/claude-tools-only.md) | **Ditch OpenClaw, rebuild on Claude Agent SDK** |
| **Model backend** | [Local models feasibility](research/local-models.md) | **Stay on Claude API** — local is viable as a phase-2 hybrid, not a standalone move |

## TL;DR

The current *platform* stack is right. The *agent runtime* is not.

- **Obsidian** for knowledge management (local-first, markdown, AI-native)
- **Todoist** for task management (best API + natural language)
- **Discord** as a rich automation channel alongside iMessage
- **Claude Agent SDK** as the new Cleo runtime (replaces OpenClaw)
- **Claude API** as the model backend (local models optional, phase 2)

### The OpenClaw problem

OpenClaw is now both **pay-per-use** and **fragile/flaky** in practice — a metered fee on top of the Anthropic bill for a harness that fails unpredictably. The two-axis decision:

|  | **Claude API** | **Local models** |
|---|---|---|
| **Keep OpenClaw** | Current pain (paid + flaky) | Paid + flaky + inference complexity |
| **Claude-native harness** | ⭐ Recommended | Possible phase 2 via LiteLLM |
| **Custom harness** | More work, no clear win | Most work; only if privacy-driven |

The recommended move is **ditch OpenClaw, rebuild on the Claude Agent SDK, keep Claude API as the model**. Local models are a separable, later decision.

## Target Architecture

```
Lesley / Greg / Mira / Nanny
       │
       ├── iMessage (BlueBubbles bridge)
       └── Discord (discord.py bot)
              │
              ▼
          Cleo (Python, Claude Agent SDK)
              │
              ├── Obsidian vault (filesystem + brain MCP servers)
              ├── Todoist (CLI + API)
              ├── ElevenLabs TTS (sag CLI)
              └── launchd-scheduled pipelines
                    (morning-brief, inbox-triage, vault-health, knowledge-graph)
              │
              ▼
          Claude API (Sonnet 4.6 / Opus 4.7)
          [optional phase 2: LiteLLM → local Ollama/MLX]
```

No external harness. Everything runs as Python processes on the Mac Studio under launchd.

## Next Steps

1. Prototype the Agent SDK Discord loop with one MCP server (`brain_search`)
2. Port `morning-brief.lobster` to `morning_brief.py` + launchd as the first pipeline migration
3. Wire BlueBubbles iMessage bridge into the same `query()` loop
4. Add prompt caching on the system prompt + stable vault blocks
5. Decommission OpenClaw once pipelines and interfaces are live
6. (Optional, later) Evaluate LiteLLM + local model routing if cost or privacy becomes the driver
