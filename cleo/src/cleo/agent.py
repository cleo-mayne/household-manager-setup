"""Shared Claude Agent SDK options + query helpers.

The two entry points:
- `run_one_shot(prompt, *, nanny_mode, writable)` for stateless pipeline calls
  (morning-brief, inbox-triage, etc.)
- `ConversationStore.reply(channel_id, prompt, *, nanny_mode, writable)` for
  multi-turn chat where we want continuity across messages in a channel.
"""

from __future__ import annotations

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, query

from .config import Settings, system_prompt
from .permissions import build_can_use_tool

FULL_TOOLS = ["Read", "Glob", "Grep", "Write", "Edit", "Bash"]
READ_ONLY_TOOLS = ["Read", "Glob", "Grep"]


def build_options(
    settings: Settings,
    *,
    nanny_mode: bool,
    writable: bool,
) -> ClaudeAgentOptions:
    tools = FULL_TOOLS if writable else READ_ONLY_TOOLS

    mcp_servers: dict[str, dict] = {
        "brain": {
            "command": settings.brain_mcp_cmd,
            "args": settings.brain_mcp_args,
            "env": {"OBSIDIAN_VAULT": str(settings.obsidian_vault)},
        },
    }
    if settings.qmd_enabled:
        # qmd's MCP server: hybrid BM25 + vector + LLM rerank search over the vault.
        # `qmd mcp` speaks MCP on stdio; the index lives at ~/.cache/qmd/index.sqlite
        # and is built by `qmd embed` (see scheduled/qmd_reindex.py).
        mcp_servers["qmd"] = {
            "command": settings.qmd_bin,
            "args": ["mcp"],
        }

    return ClaudeAgentOptions(
        model=settings.model,
        system_prompt=system_prompt(nanny_mode=nanny_mode),
        allowed_tools=tools,
        can_use_tool=build_can_use_tool(
            settings, nanny_mode=nanny_mode, writable=writable
        ),
        mcp_servers=mcp_servers,
        permission_mode="acceptEdits" if writable else "dontAsk",
    )


async def run_one_shot(
    settings: Settings,
    prompt: str,
    *,
    nanny_mode: bool = False,
    writable: bool = False,
) -> str:
    """Stateless call — returns the final assistant text."""
    options = build_options(settings, nanny_mode=nanny_mode, writable=writable)
    chunks: list[str] = []
    async for event in query(prompt=prompt, options=options):
        text = getattr(event, "text", None)
        if event.type == "assistant" and text:
            chunks.append(text)
    return "\n".join(chunks).strip()
