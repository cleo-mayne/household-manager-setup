"""Permission callback for the Agent SDK's `can_use_tool` hook.

This is a defence-in-depth layer on top of `allowed_tools`. Where
`allowed_tools` is an allowlist of tool *names*, this callback inspects
the *arguments* of each call and can deny or rewrite them.

Rules implemented here:
- Writes (Write/Edit) must land inside the vault's inbox/ or daily/ dirs.
- Bash commands are blocked if they match dangerous patterns.
- Nanny mode hard-denies any write or shell tool regardless of allowed_tools.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .config import Settings

# Bash patterns we refuse outright. Conservative: we'd rather fail loud.
BLOCKED_BASH = re.compile(
    r"""
    (\brm\s+-[rf]+\b)             # rm -rf
    | (\b:\(\)\s*\{)              # fork bomb
    | (\bdd\s+if=)                # low-level disk writes
    | (\bcurl\s+[^|]*\|\s*(ba)?sh)  # curl-to-shell
    | (\bsudo\b)                  # no privilege escalation
    | (\bmkfs\b|\bfdisk\b)        # filesystem nukes
    """,
    re.VERBOSE,
)


def _under(path: Path, roots: list[Path]) -> bool:
    try:
        path = path.resolve()
    except OSError:
        return False
    for root in roots:
        try:
            path.relative_to(root.resolve())
            return True
        except ValueError:
            continue
    return False


def build_can_use_tool(settings: Settings, *, nanny_mode: bool, writable: bool):
    """Returns an async callback matching the SDK's can_use_tool signature."""

    vault = settings.obsidian_vault
    allowed_write_roots = [vault / "inbox", vault / "daily"]

    async def can_use_tool(tool_name: str, tool_input: dict[str, Any], _ctx: Any = None):
        name = tool_name.split("__")[-1]  # MCP tools arrive as "mcp__brain__search"

        # Retired: vault search goes through qmd. Belt-and-braces gate so the
        # model can't fall back to brain_search even if it's still exposed by
        # the brain MCP server.
        if settings.qmd_enabled and tool_name in {
            "mcp__brain__search",
            "mcp__brain__brain_search",
        }:
            return {
                "behavior": "deny",
                "message": "brain_search is retired. Use mcp__qmd__query for vault search.",
            }

        if nanny_mode and name in {"Write", "Edit", "Bash"}:
            return {"behavior": "deny", "message": "Nanny mode is read-only."}

        if not writable and name in {"Write", "Edit", "Bash"}:
            return {"behavior": "deny", "message": "This context is read-only."}

        if name in {"Write", "Edit"}:
            target = tool_input.get("file_path") or tool_input.get("path") or ""
            if not target:
                return {"behavior": "deny", "message": "Missing file_path."}
            if not _under(Path(target), allowed_write_roots):
                return {
                    "behavior": "deny",
                    "message": f"Writes must land under {vault}/inbox or {vault}/daily.",
                }

        if name == "Bash":
            cmd = tool_input.get("command", "")
            if BLOCKED_BASH.search(cmd):
                return {"behavior": "deny", "message": "Blocked bash pattern."}

        return {"behavior": "allow", "updatedInput": tool_input}

    return can_use_tool
