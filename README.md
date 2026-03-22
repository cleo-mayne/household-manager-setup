# Household Manager Setup

Platform evaluation and setup documentation for a household AI assistant system.

## Research

Deep research comparing platform choices for three critical dimensions:

| Decision | Research | Verdict |
|---|---|---|
| **Chat platform** | [Discord vs Slack](research/discord-vs-slack.md) | **Discord** — $0/mo, unlimited history, unlimited bots, voice channels |
| **Knowledge management** | [Obsidian vs Notion](research/obsidian-vs-notion.md) | **Obsidian** — local-first, direct filesystem access for AI agent, privacy |
| **Task management** | [Stay on Todoist or migrate?](research/todoist-stay-or-migrate.md) | **Stay on Todoist** — best API + NLP combo, already integrated |

## TL;DR

The current stack is the right stack:

- **Obsidian** for knowledge management (local-first, markdown, AI-native)
- **Todoist** for task management (best API + natural language, $96/yr)
- **Add Discord** as a rich automation channel alongside iMessage ($0)

No migrations needed. The one addition worth making is Discord for a dashboard/automation layer.

## Current Architecture

```
Lesley / Greg (iMessage, Todoist app, Obsidian app)
       │
       ▼
    Cleo (AI assistant)
       │
       ├── Obsidian vaults (knowledge, notes, goals, people)
       ├── Todoist (tasks, projects, shared lists)
       ├── iMessage (primary chat interface)
       └── Discord (proposed: rich dashboard + automation)
```

## Next Steps

1. Set up a Discord server with Cleo bot integration
2. Evaluate Obsidian CLI v1.12 and MCP server for enhanced AI access
3. Consider Linear alongside Todoist for technical project work only
