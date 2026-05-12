"""Shared Claude Agent SDK options + query helpers.

The two entry points:
- `run_skill(settings, skill_name, *, writable, nanny_mode)` for scheduled
  pipelines (morning-brief, inbox-triage, etc.) — loads the named skill
  from `cleo/skills/<name>.md` (vault override at `$OBSIDIAN_VAULT/skills/<name>.md`)
  and runs it stateless.
- `ConversationStore.reply(channel_id, prompt, ...)` for multi-turn chat.
"""

from __future__ import annotations

from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, query

from .config import Settings, system_prompt
from .permissions import build_can_use_tool

REPO_SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"

FULL_TOOLS = ["Read", "Glob", "Grep", "Write", "Edit", "Bash"]
READ_ONLY_TOOLS = ["Read", "Glob", "Grep"]


def load_skill(settings: Settings, name: str) -> str:
    """Vault override wins. Returns the markdown contents of the skill."""
    vault_skill = settings.obsidian_vault / "skills" / f"{name}.md"
    if vault_skill.exists():
        return vault_skill.read_text()
    return (REPO_SKILLS_DIR / f"{name}.md").read_text()


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


async def run_skill(
    settings: Settings,
    name: str,
    *,
    extra_context: str = "",
    nanny_mode: bool = False,
    writable: bool = False,
) -> str:
    """Load a named skill and execute it as a one-shot.

    The skill markdown becomes the user prompt — the system prompt already
    instructs Cleo on how to execute skill files.
    """
    skill = load_skill(settings, name)
    prompt = f"Run skill: {name}\n\n---\n\n{skill}"
    if extra_context:
        prompt += f"\n\n---\n\n## Additional context\n\n{extra_context}"
    return await run_one_shot(
        settings, prompt, nanny_mode=nanny_mode, writable=writable
    )
